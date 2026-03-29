import os
import time
from instagrapi import Client
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

class InstagramClient:
    def __init__(self):
        self.username = settings.SOCIAL_MEDIA['instagram']['username']
        self.password = settings.SOCIAL_MEDIA['instagram']['password']
        self.client = Client()
        self.is_authenticated = False
        
    def login(self):
        """تسجيل الدخول إلى إنستقرام"""
        try:
            if not self.username or self.username.startswith('YOUR_'):
                logger.warning("⚠️ Instagram credentials not set")
                return False
            
            logger.info(f"🔐 Logging into Instagram as {self.username}...")
            self.client.login(self.username, self.password)
            self.is_authenticated = True
            logger.info("✅ Instagram login successful!")
            return True
            
        except Exception as e:
            logger.error(f"💥 Instagram login failed: {str(e)}")
            return False

    def upload_reel(self, video_path, metadata, session_type):
        """رفع رييل على إنستقرام باستخدام instagrapi"""
        # محاولة تسجيل الدخول إذا لم يتم الدخول مسبقاً
        if not self.is_authenticated:
             if not self.login():
                 logger.error("❌ Cannot upload: Authentication failed")
                 return None
                
        try:
            logger.info("📸 Starting Instagram Reel upload...")
            
            # التحقق من وجود الملف
            if not os.path.exists(video_path):
                logger.error(f"❌ Video file not found: {video_path}")
                return None
            
            # بناء الوصف
            # Metadata now contains the ready-made caption
            caption = metadata.get('caption', '')
            if not caption:
                 # Fallback if somehow missing
                 caption = self._build_instagram_caption(metadata, session_type)

            # رفع الرييل
            logger.info("📤 Uploading video file...")
            # clip_upload returns Media object
            media = self.client.clip_upload(
                path=video_path,
                caption=caption
            )
            
            if media and media.pk:
                media_id = media.pk
                code = media.code
                logger.info(f"✅ Instagram Reel uploaded successfully! Media ID: {media_id}")
                logger.info(f"🔗 URL: https://instagram.com/p/{code}/")
                return media_id
            else:
                logger.error("❌ Instagram upload returned no media ID")
                return None
            
        except Exception as e:
            logger.error(f"💥 Instagram upload error: {str(e)}")
            return None
    
    def _build_instagram_caption(self, metadata, session_type):
        """بناء كابشن مناسب لإنستقرام"""
        title = metadata.get('title', '')
        hashtags = metadata.get('hashtags', [])
        
        emoji = "☕" if session_type == 'morning' else "🪑" if session_type == 'noon' else "🛌"
        
        caption = f"{title}\n\n"
        caption += f"{emoji} The daily life of your objects ✨\n\n"
        caption += "Wait for it... 😂\n\n"
        
        # إضافة الهاشتاقات
        if hashtags:
            # دمج هاشتاقات عامة مع هاشتاقات الفيديو
            insta_hashtags = [
                "#ObjectLife", "#Funny", "#Animation", 
                "#ComedyReels", "#Relatable", "#ViralShorts",
                "#Humor", "#DailyStruggles", "#Shorts"
            ]
            
            # تجنب التكرار واستخدام set
            unique_hashtags = list(set(insta_hashtags + hashtags))
            
            # الحد الأقصى لهاشتاقات إنستقرام هو 30
            final_hashtags = unique_hashtags[:30]
            
            caption += " ".join(final_hashtags)
        
        return caption