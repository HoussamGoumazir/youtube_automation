import os
import time
import tempfile
from datetime import datetime
from utils.logger import get_logger
from config.settings import settings
from .file_manager import AdvancedFileManager
from .gemini_client import AdvancedGeminiClient
from .youtube_client import AdvancedYouTubeClient

logger = get_logger(__name__)

class AdvancedArchiveManager:
    def __init__(self):
        self.file_manager = AdvancedFileManager()
        self.gemini_client = AdvancedGeminiClient()
        self.youtube_client = AdvancedYouTubeClient()
        
        # تهيئة عملاء وسائل التواصل الاجتماعي (مشروط)
        self.social_clients = {}
        self._init_social_clients()
        
        self.session_stats = {
            'total_processed': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'social_shares': 0,
            'last_session': None
        }
    
    def _init_social_clients(self):
        """تهيئة عملاء وسائل التواصل الاجتماعي (مشروط)"""
        try:
            # Facebook Client
            if settings.SOCIAL_MEDIA['facebook']['enabled']:
                try:
                    from .facebook_client import FacebookClient
                    self.social_clients['facebook'] = FacebookClient()
                    logger.info("✅ Facebook client initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize Facebook client: {e}")
            
            # Instagram Client
            if settings.SOCIAL_MEDIA['instagram']['enabled']:
                try:
                    from .instagram_client import InstagramClient
                    self.social_clients['instagram'] = InstagramClient()
                    logger.info("✅ Instagram client initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize Instagram client: {e}")
            
            # TikTok Client
            if settings.SOCIAL_MEDIA['tiktok']['enabled']:
                try:
                    from .tiktok_client import TikTokClient
                    self.social_clients['tiktok'] = TikTokClient()
                    logger.info("✅ TikTok client initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize TikTok client: {e}")
                    
        except Exception as e:
            logger.error(f"💥 Error initializing social clients: {e}")
    
    def process_session(self, session_type):
        """معالجة جلسة كاملة مع تتبع متقدم ووسائل التواصل"""
        session_start = datetime.now()
        logger.info(f"🚀 Starting {session_type.upper()} session at {session_start}")
        
        try:
            # 1. التحقق من توفر الفيديوهات
            video_count = self.file_manager.get_video_count(session_type)
            if video_count == 0:
                logger.error(f"❌ No videos available in {session_type} folder")
                self._update_stats(session_type, False)
                return False
            
            logger.info(f"📊 Found {video_count} videos in {session_type} folder")
            
            # 2. جلب الفيديو
            video_info = self.file_manager.get_video_from_folder(session_type)
            if not video_info:
                logger.error(f"❌ Failed to read video from {session_type} folder")
                self._update_stats(session_type, False)
                return False
            
            # 3. توليد المحتوى بالذكاء الاصطناعي
            logger.info(f"🤖 Generating optimized metadata for: {video_info['name']}...")
            metadata = self.gemini_client.generate_metadata(session_type, video_info['name'])
            
            if not metadata:
                logger.error(f"❌ Failed to generate metadata for {session_type}")
                self._update_stats(session_type, False)
                return False
            
            # 4. رفع الفيديو لليوتيوب
            logger.info("📤 Uploading to YouTube...")
            youtube_id = self.youtube_client.upload_video(
                video_info['content'], 
                metadata.get('youtube', {}), 
                session_type
            )
            
            if youtube_id:
                # 5. مشاركة على وسائل التواصل الاجتماعي (إذا كانت مفعلة)
                social_results = {}
                if self.social_clients:
                    logger.info("📱 Sharing to social media platforms...")
                    social_results = self._share_to_social_media(
                        video_info['content'],
                        metadata,
                        session_type,
                        youtube_id
                    )
                
                # 6. أرشفة الفيديو
                archive_success = self.file_manager.archive_video(
                    video_info, 
                    session_type, 
                    youtube_id
                )
                
                session_duration = (datetime.now() - session_start).total_seconds()
                
                if archive_success:
                    logger.info(f"🎉 {session_type.upper()} session completed successfully!")
                    logger.info(f"⏱️ Session duration: {session_duration:.1f} seconds")
                    logger.info(f"📈 SEO Score: {metadata.get('seo_analysis', {}).get('overall_score', 'N/A')}/100")
                    
                    # تسجيل النتائج
                    self._log_successful_session(
                        session_type, 
                        video_info, 
                        metadata, 
                        youtube_id, 
                        session_duration,
                        social_results
                    )
                    
                    # تحديث الإحصائيات
                    self._update_stats(session_type, True, social_results)
                    
                    # عرض ملخص النتائج
                    self._display_session_summary(session_type, youtube_id, social_results)
                    
                    return True
                else:
                    logger.warning(f"⚠️ YouTube upload successful but archiving failed")
                    self._update_stats(session_type, True, social_results)
                    return True
            else:
                logger.error(f"❌ YouTube upload failed for {session_type}")
                self._update_stats(session_type, False)
                return False
                
        except Exception as e:
            logger.error(f"💥 Critical error in {session_type} session: {str(e)}")
            import traceback
            traceback.print_exc()
            self._update_stats(session_type, False)
            return False
    
    def _share_to_social_media(self, video_content, metadata, session_type, youtube_id):
        """مشاركة الفيديو على وسائل التواصل الاجتماعي"""
        social_results = {
            'successful': [],
            'failed': [],
            'details': {}
        }
        
        if not self.social_clients:
            logger.info("📭 No social media platforms enabled in settings")
            return social_results
        
        # حفظ الفيديو مؤقتاً للمنصات الأخرى
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(video_content)
                temp_path = temp_file.name
            
            logger.info(f"📁 Created temporary video file: {temp_path}")
            
            # مشاركة على كل منصة مفعلة
            for platform, client in self.social_clients.items():
                try:
                    logger.info(f"📤 Sharing to {platform.capitalize()}...")
                    
                    # استخدام دالة الرفع المناسبة لكل منصة
                    platform_metadata = metadata.get(platform, {})
                    
                    if hasattr(client, 'upload_video'):
                        result = client.upload_video(temp_path, platform_metadata, session_type)
                    elif hasattr(client, 'upload_reel'):
                        result = client.upload_reel(temp_path, platform_metadata, session_type)
                    else:
                        result = None
                    
                    if result:
                        social_results['successful'].append(platform)
                        social_results['details'][platform] = result
                        logger.info(f"✅ {platform.capitalize()} share successful! ID: {result}")
                        
                        # تأخير بين المنصات لتجنب rate limits
                        delay = settings.SOCIAL_POST_DELAYS.get(platform, 5)
                        logger.info(f"⏳ Waiting {delay} seconds before next platform...")
                        time.sleep(delay)
                    else:
                        social_results['failed'].append(platform)
                        logger.warning(f"⚠️ {platform.capitalize()} share failed")
                        
                except Exception as e:
                    logger.error(f"💥 Error sharing to {platform}: {str(e)}")
                    social_results['failed'].append(platform)
            
            logger.info(f"📊 Social media results: {len(social_results['successful'])} successful, {len(social_results['failed'])} failed")
            
        except Exception as e:
            logger.error(f"💥 Error in social media sharing: {str(e)}")
        finally:
            # تنظيف الملف المؤقت
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.debug("🧹 Temporary file cleaned up")
        
        return social_results
    
    def _update_stats(self, session_type, success, social_results=None):
        """تحديث إحصائيات الجلسات"""
        self.session_stats['total_processed'] += 1
        self.session_stats['last_session'] = datetime.now()
        
        if success:
            self.session_stats['successful_uploads'] += 1
            
            # تحديث إحصائيات وسائل التواصل
            if social_results:
                self.session_stats['social_shares'] += len(social_results.get('successful', []))
        else:
            self.session_stats['failed_uploads'] += 1
    
    def _log_successful_session(self, session_type, video_info, metadata, youtube_id, duration, social_results=None):
        """تسجيل جلسة ناجحة مع نتائج وسائل التواصل"""
        try:
            log_entry = f"""
✅ SUCCESSFUL UPLOAD - {session_type.upper()}
==========================================
Timestamp: {datetime.now()}
Video: {video_info['name']}
YouTube ID: {youtube_id}
YouTube URL: https://youtube.com/watch?v={youtube_id}
Session Type: {session_type}
Duration: {duration:.1f}s
File Size: {video_info['size_mb']} MB
SEO Score: {metadata.get('seo_analysis', {}).get('overall_score', 'N/A')}/100
Title: {metadata.get('youtube', {}).get('title', 'N/A')}
Pinned Comment: {metadata.get('youtube', {}).get('pinned_comment', 'N/A')}
Strategy: {metadata.get('engagement_strategy', {}).get('opening_hook', 'N/A')}
"""

            # إضافة نتائج وسائل التواصل إذا وجدت
            if social_results and social_results.get('successful'):
                log_entry += f"\n📱 SOCIAL MEDIA RESULTS:\n"
                for platform in social_results['successful']:
                    platform_id = social_results['details'].get(platform, 'N/A')
                    log_entry += f"  • {platform.capitalize()}: {platform_id}\n"
                
                if social_results.get('failed'):
                    log_entry += f"  ❌ Failed: {', '.join(social_results['failed'])}\n"
            elif social_results:
                log_entry += f"\n📭 No successful social media shares\n"
            
            log_entry += "=========================================="
            
            # حفظ في ملف السجلات الرئيسي
            success_log_path = os.path.join(settings.LOGS_DIR, "successful_uploads.log")
            with open(success_log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
            # حفظ في ملف منفصل لوسائل التواصل
            if social_results:
                social_log_path = os.path.join(settings.LOGS_DIR, "social_media.log")
                with open(social_log_path, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                    
        except Exception as e:
            logger.error(f"💥 Error logging successful session: {str(e)}")
    
    def _display_session_summary(self, session_type, youtube_id, social_results=None):
        """عرض ملخص الجلسة في الـ console"""
        print(f"\n{'='*60}")
        print(f"🎉 {session_type.upper()} SESSION SUMMARY")
        print(f"{'='*60}")
        print(f"📺 YouTube: https://youtube.com/watch?v={youtube_id}")
        
        if social_results and social_results.get('successful'):
            print(f"📱 Social Media:")
            for platform in social_results['successful']:
                platform_id = social_results['details'].get(platform, 'N/A')
                print(f"  • {platform.capitalize()}: {platform_id}")
        
        if social_results and social_results.get('failed'):
            print(f"  ❌ Failed: {', '.join(social_results['failed'])}")
        
        print(f"{'='*60}")
    
    def check_video_availability(self):
        """فحص متقدم لتوفر الفيديوهات"""
        try:
            availability = {}
            storage_stats = self.file_manager.get_storage_stats()
            
            for session_type in ['morning', 'noon', 'evening']:
                videos = self.file_manager.list_available_videos(session_type)
                availability[session_type] = {
                    'count': len(videos),
                    'videos': videos,
                    'total_size_mb': storage_stats[session_type]['size_mb']
                }
            
            availability['storage_stats'] = storage_stats
            return availability
        except Exception as e:
            logger.error(f"💥 Error checking video availability: {str(e)}")
            return {}
    
    def get_system_stats(self):
        """إحصائيات النظام"""
        try:
            stats = {
                'session_stats': self.session_stats,
                'storage_stats': self.file_manager.get_storage_stats(),
                'system_uptime': time.time(),
                'social_clients': len(self.social_clients)
            }
            
            # حساب نسبة النجاح
            if self.session_stats['total_processed'] > 0:
                success_rate = (self.session_stats['successful_uploads'] / self.session_stats['total_processed']) * 100
                stats['success_rate'] = f"{success_rate:.1f}%"
            else:
                stats['success_rate'] = "0%"
            
            return stats
        except Exception as e:
            logger.error(f"💥 Error getting system stats: {str(e)}")
            return {}
    
    def health_check(self):
        """فحص صحة النظام المتقدم"""
        try:
            health_status = {
                'directories': {},
                'authentication': True,  # افترض أن المصادقة صحيحة
                'ai_service': False,
                'social_clients': {},
                'overall': False
            }
            
            # 1. فحص المجلدات
            for name, path in settings.LOCAL_FOLDERS.items():
                health_status['directories'][name] = os.path.exists(path)
            
            # 2. فحص خدمة الذكاء الاصطناعي
            try:
                test_metadata = self.gemini_client.generate_metadata('morning')
                health_status['ai_service'] = test_metadata is not None
            except Exception as e:
                logger.warning(f"⚠️ AI service check: {str(e)}")
                health_status['ai_service'] = False
            
            # 3. فحص عملاء وسائل التواصل
            for platform, config in settings.SOCIAL_MEDIA.items():
                if config['enabled']:
                    health_status['social_clients'][platform] = platform in self.social_clients
                else:
                    health_status['social_clients'][platform] = 'disabled'
            
            # 4. الحالة العامة (لا تشمل فحص القناة)
            health_status['overall'] = (
                all(health_status['directories'].values()) and
                health_status['ai_service']
            )
            
            return health_status
            
        except Exception as e:
            logger.error(f"💥 Error in health check: {str(e)}")
            return {
                'directories': {},
                'authentication': True,
                'ai_service': False,
                'social_clients': {},
                'overall': False
            }
    
    def get_social_media_status(self):
        """الحصول على حالة وسائل التواصل الاجتماعي"""
        status = {}
        
        for platform, config in settings.SOCIAL_MEDIA.items():
            status[platform] = {
                'enabled': config['enabled'],
                'initialized': platform in self.social_clients,
                'api_configured': self._check_api_configuration(platform, config)
            }
        
        return status
    
    def _check_api_configuration(self, platform, config):
        """التحقق من تكوين API لمنصة معينة"""
        if not config['enabled']:
            return 'disabled'
        
        # التحقق من وجود بيانات API الأساسية
        if platform == 'facebook':
            required_fields = ['page_id', 'access_token']
        elif platform == 'instagram':
            required_fields = ['business_account_id']
        elif platform == 'tiktok':
            required_fields = ['open_id', 'access_token']
        else:
            return 'unknown'
        
        for field in required_fields:
            if not config.get(field) or str(config.get(field, '')).startswith('YOUR_'):
                return 'missing_credentials'
        
        return 'configured'
    
    def manual_social_share(self, video_path, session_type, metadata=None):
        """مشاركة يدوية على وسائل التواصل الاجتماعي"""
        if not self.social_clients:
            print("❌ No social media clients initialized. Check your settings.")
            return False
        
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return False
        
        if not metadata:
            print("📝 Generating metadata for social media...")
            metadata = self.gemini_client.generate_metadata(session_type)
        
        print(f"📱 Sharing video to social media platforms...")
        social_results = self._share_to_social_media(
            open(video_path, 'rb').read(),
            metadata,
            session_type,
            'manual_share'
        )
        
        print(f"\n📊 Results:")
        for platform in social_results['successful']:
            print(f"  ✅ {platform.capitalize()}: Success")
        for platform in social_results['failed']:
            print(f"  ❌ {platform.capitalize()}: Failed")
        
        return social_results