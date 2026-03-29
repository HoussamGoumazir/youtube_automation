import os
import pickle
import tempfile
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

class AdvancedYouTubeClient:
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """المصادقة المتقدمة مع YouTube API"""
        creds = None
        token_file = os.path.join(settings.CONFIG_DIR, 'youtube_token.pickle')
        scopes = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube',
            'https://www.googleapis.com/auth/youtube.readonly'
        ]
        
        # إنشاء مجلد config إذا لم يكن موجوداً
        os.makedirs(settings.CONFIG_DIR, exist_ok=True)
        
        try:
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
                    logger.info("🔑 Loaded existing YouTube credentials")
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("🔄 Refreshing expired YouTube credentials")
                    creds.refresh(Request())
                else:
                    logger.info("🔐 Starting new YouTube authentication flow")
                    credentials_path = os.path.join(settings.BASE_DIR, 'youtube_credentials.json')
                    
                    if not os.path.exists(credentials_path):
                        logger.error(f"❌ YouTube credentials file not found: {credentials_path}")
                        raise FileNotFoundError("YouTube credentials file missing")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, 
                        scopes
                    )
                    creds = flow.run_local_server(
                        port=0,
                        open_browser=True,
                        success_message="YouTube authentication successful! You can close this window.",
                        authorization_prompt_message="Please authorize this app to upload videos to your YouTube channel"
                    )
                
                # حفظ credentials الجديدة
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
                logger.info("💾 Saved new YouTube credentials")
            
            self.service = build('youtube', 'v3', credentials=creds)
            logger.info("✅ YouTube authentication successful")
            
        except Exception as e:
            logger.error(f"💥 YouTube authentication failed: {str(e)}")
            raise
    
    def upload_video(self, video_content, metadata, session_type):
        """رفع فيديو متقدم مع إدارة الأخطاء"""
        temp_path = None
        
        try:
            # حفظ الفيديو مؤقتاً
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(video_content)
                temp_path = temp_file.name
            
            # إعداد الوصف المحسن
            description = self._build_enhanced_description(metadata, session_type)
            
            # إعداد بيانات الفيديو
            body = {
                'snippet': {
                    'title': metadata.get('title', 'Object Life Short'),
                    'description': description,
                    'tags': metadata.get('tags', []),
                    'categoryId': settings.YOUTUBE_CATEGORY,
                    'defaultLanguage': settings.DEFAULT_LANGUAGE
                },
                'status': {
                    'privacyStatus': settings.PRIVACY_STATUS,
                    'selfDeclaredMadeForKids': False,
                    'embeddable': True,
                    'publicStatsViewable': True
                }
            }
            
            # إعداد media للرفع
            media = MediaFileUpload(
                temp_path,
                chunksize=1024*1024,
                resumable=True,
                mimetype='video/mp4'
            )
            
            logger.info("📤 Starting YouTube upload process...")
            logger.info(f"📝 Video title: {body['snippet']['title']}")
            logger.info(f"📊 Video size: {len(video_content) / (1024*1024):.1f} MB")
            
            # طلب الرفع
            request = self.service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # رفع مع تتبع التقدم
            response = self._execute_resumable_upload(request)
            
            if response:
                video_id = response['id']
                video_url = f"https://youtube.com/watch?v={video_id}"
                
                logger.info(f"🎉 YouTube upload completed successfully!")
                logger.info(f"📺 Video URL: {video_url}")
                logger.info(f"🆔 Video ID: {video_id}")
                
                return video_id
            else:
                logger.error("❌ YouTube upload failed")
                return None
                
        except HttpError as e:
            logger.error(f"💥 YouTube API error: {e}")
            if e.resp.status in [403, 409]:
                logger.error("🔒 Possible quota exceeded or duplicate upload")
            return None
        except Exception as e:
            logger.error(f"💥 Upload error: {str(e)}")
            return None
        finally:
            # تنظيف الملف المؤقت
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.debug("🧹 Temporary file cleaned up")
    
    def _execute_resumable_upload(self, request):
        """تنفيذ الرفع مع إعادة المحاولة"""
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        logger.info(f"📊 Upload progress: {progress}%")
                
                return response
                
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504] and attempt < max_retries - 1:
                    logger.warning(f"🔄 Server error, retrying in {retry_delay}s... (Attempt {attempt + 1})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"🔄 Upload error, retrying in {retry_delay}s... (Attempt {attempt + 1})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
        
        return None
    
    def _build_enhanced_description(self, metadata, session_type):
        """بناء وصف محسن لتحسين SEO"""
        title = metadata.get('title', '')
        description = metadata.get('description', '')
        hashtags = metadata.get('hashtags', [])
        
        # إيموجي حسب النوع
        emoji = "🌅" if session_type == 'morning' else "☀️" if session_type == 'noon' else "🌙"
        
        # الوصف يأتي جاهزاً من AI
        enhanced_description = description
        
        # إذا لم يكن هناك هاشتاقات في الوصف، أضفها في النهاية (اختياري)
        # لكن الـ prompt الجديد يطلب من AI تضمين الهاشتاقات في الوصف
        
        # التأكد من عدم تجاوز الحد
        if len(enhanced_description) > 5000:
            enhanced_description = enhanced_description[:4990] + "\n..."
        
        return enhanced_description
    
    def get_channel_info(self):
        """الحصول على معلومات القناة"""
        try:
            response = self.service.channels().list(
                part='snippet',
                mine=True
            ).execute()
            
            if response['items']:
                channel = response['items'][0]
                logger.info(f"📺 Channel: {channel['snippet']['title']}")
                return channel
            return None
        except Exception as e:
            logger.warning(f"⚠️ Could not get channel info (may need additional permissions): {str(e)}")
            return None