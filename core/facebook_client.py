import os
import requests
import time
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

class FacebookClient:
    def __init__(self):
        self.page_id = settings.SOCIAL_MEDIA['facebook']['page_id']
        self.access_token = settings.SOCIAL_MEDIA['facebook']['access_token']
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    def upload_video(self, video_path, metadata, session_type):
        """رفع فيديو لصفحة فيسبوك"""
        try:
            logger.info("📘 Starting Facebook upload...")
            
            # 1. إنشاء جلسة رفع
            upload_session_url = f"{self.base_url}/{self.page_id}/video_reels"
            
            params = {
                'access_token': self.access_token,
                'upload_phase': 'start',
                'file_size': os.path.getsize(video_path)
            }
            
            response = requests.post(upload_session_url, params=params)
            
            if response.status_code != 200:
                logger.error(f"❌ Facebook upload session failed: {response.text}")
                return None
            
            session_data = response.json()
            video_id = session_data.get('video_id')
            upload_url = session_data.get('upload_url')
            
            # 2. رفع الفيديو
            with open(video_path, 'rb') as video_file:
                files = {'video_file': video_file}
                upload_response = requests.post(upload_url, files=files)
            
            if upload_response.status_code != 200:
                logger.error(f"❌ Facebook video upload failed: {upload_response.text}")
                return None
            
            # 3. إضافة الوصف والمعلومات
            publish_url = f"{self.base_url}/{video_id}"
            
            # بناء وصف فيسبوك
            facebook_description = metadata.get('post_text', '')
            if not facebook_description:
                 facebook_description = self._build_facebook_description(metadata, session_type)
            
            publish_data = {
                'access_token': self.access_token,
                'description': facebook_description,
                'published': 'true'
            }
            
            publish_response = requests.post(publish_url, data=publish_data)
            
            if publish_response.status_code == 200:
                result = publish_response.json()
                post_id = result.get('id')
                logger.info(f"✅ Facebook upload successful! Post ID: {post_id}")
                logger.info(f"🔗 URL: https://facebook.com/{post_id}")
                return post_id
            else:
                logger.error(f"❌ Facebook publish failed: {publish_response.text}")
                return None
            
        except Exception as e:
            logger.error(f"💥 Facebook upload error: {str(e)}")
            return None
    
    def _build_facebook_description(self, metadata, session_type):
        """بناء وصف مناسب لفيسبوك"""
        title = metadata.get('title', '')
        hashtags = metadata.get('hashtags', [])
        
        emoji = "☕" if session_type == 'morning' else "🪑" if session_type == 'noon' else "🛌"
        
        description = f"{title}\n\n"
        description += f"A new Object Life short has dropped! {emoji}\n\n"
        description += "Welcome to Object Life — where everyday objects have thoughts too.\n"
        description += "Follow us for more funny animated shorts!\n\n"
        
        # أخذ أول 10 هاشتاقات
        if hashtags:
            description += " ".join(hashtags[:10])
        
        return description
    
    def schedule_post(self, video_path, metadata, session_type, schedule_time=None):
        """جدولة منشور على فيسبوك"""
        try:
            if not schedule_time:
                # افتراضي: بعد 5 دقائق
                schedule_time = int(time.time()) + (settings.SOCIAL_SCHEDULE['facebook'] * 60)
            
            logger.info(f"📅 Scheduling Facebook post for {time.ctime(schedule_time)}")
            
            # رفع الفيديو أولاً
            video_id = self.upload_video(video_path, metadata, session_type)
            
            if video_id:
                # جدولة النشر
                schedule_url = f"{self.base_url}/{self.page_id}/feed"
                
                schedule_data = {
                    'access_token': self.access_token,
                    'published': 'false',
                    'scheduled_publish_time': schedule_time,
                    'message': self._build_facebook_description(metadata, session_type),
                    'attached_media': f"[{{'media_fbid':'{video_id}'}}]"
                }
                
                response = requests.post(schedule_url, data=schedule_data)
                
                if response.status_code == 200:
                    scheduled_post_id = response.json().get('id')
                    logger.info(f"✅ Facebook post scheduled! ID: {scheduled_post_id}")
                    return scheduled_post_id
            
            return None
            
        except Exception as e:
            logger.error(f"💥 Facebook scheduling error: {str(e)}")
            return None