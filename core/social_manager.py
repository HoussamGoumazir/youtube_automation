import os
import tempfile
import time
from utils.logger import get_logger
from config.settings import settings
from .facebook_client import FacebookClient
from .instagram_client import InstagramClient
from .tiktok_client import TikTokClient

logger = get_logger(__name__)

class SocialMediaManager:
    def __init__(self):
        self.facebook = FacebookClient() if settings.SOCIAL_MEDIA['facebook']['enabled'] else None
        self.instagram = InstagramClient() if settings.SOCIAL_MEDIA['instagram']['enabled'] else None
        self.tiktok = TikTokClient() if settings.SOCIAL_MEDIA['tiktok']['enabled'] else None
        
        # Initialize clients (e.g. login)
        if self.instagram:
            logger.info("📱 Initializing Instagram client...")
            self.instagram.login()

    
    def share_to_all_platforms(self, video_content, metadata, session_type, youtube_id=None):
        """مشاركة الفيديو على جميع المنصات"""
        results = {
            'facebook': None,
            'instagram': None,
            'tiktok': None,
            'successful': [],
            'failed': []
        }
        
        try:
            # حفظ الفيديو مؤقتاً للمنصات الأخرى
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(video_content)
                temp_path = temp_file.name
            
            # 1. فيسبوك
            if self.facebook:
                try:
                    fb_result = self.facebook.upload_video(temp_path, metadata, session_type)
                    if fb_result:
                        results['facebook'] = fb_result
                        results['successful'].append('facebook')
                        logger.info("✅ Facebook share completed")
                    else:
                        results['failed'].append('facebook')
                except Exception as e:
                    logger.error(f"💥 Facebook share error: {str(e)}")
                    results['failed'].append('facebook')
            
            # 2. إنستقرام
            if self.instagram:
                try:
                    ig_result = self.instagram.upload_reel(temp_path, metadata, session_type)
                    if ig_result:
                        results['instagram'] = ig_result
                        results['successful'].append('instagram')
                        logger.info("✅ Instagram share completed")
                    else:
                        results['failed'].append('instagram')
                except Exception as e:
                    logger.error(f"💥 Instagram share error: {str(e)}")
                    results['failed'].append('instagram')
            
            # 3. تيكتوك
            if self.tiktok:
                try:
                    # TikTok uploader now returns a status string on success
                    tt_result = self.tiktok.upload_video(temp_path, metadata, session_type)
                    if tt_result:
                        results['tiktok'] = tt_result
                        results['successful'].append('tiktok')
                        logger.info("✅ TikTok share completed")
                    else:
                        results['failed'].append('tiktok')
                except Exception as e:
                    logger.error(f"💥 TikTok share error: {str(e)}")
                    results['failed'].append('tiktok')
            
            # تنظيف الملف المؤقت
            os.unlink(temp_path)
            
            # تسجيل النتائج
            logger.info(f"📊 Social media results: {len(results['successful'])} successful, {len(results['failed'])} failed")
            
            return results
            
        except Exception as e:
            logger.error(f"💥 Social media sharing error: {str(e)}")
            return results