"""
automation/workflow.py
Main upload orchestrator — moved from core/archive_manager.py.
Imports updated to use the new ai/, uploaders/, automation/ packages.
"""

import os
import time
import tempfile
from datetime import datetime

from utils.logger import get_logger
from config.settings import settings
from ai.generator import AdvancedGeminiClient
from uploaders.youtube import AdvancedYouTubeClient
from automation.files import AdvancedFileManager

logger = get_logger(__name__)


class AdvancedArchiveManager:
    """Orchestrates the full pipeline: pick video → generate metadata → upload → archive."""

    def __init__(self):
        self.file_manager = AdvancedFileManager()
        self.ai_client = AdvancedGeminiClient()
        self.youtube_client = AdvancedYouTubeClient()
        self.social_clients: dict = {}
        self._init_social_clients()

        self.stats = {
            'total_processed': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'social_shares': 0,
            'last_session': None
        }

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    def _init_social_clients(self):
        """Conditionally initialise enabled social media uploaders."""
        platform_map = {
            'facebook': ('uploaders.facebook', 'FacebookClient'),
            'instagram': ('uploaders.instagram', 'InstagramClient'),
            'tiktok': ('uploaders.tiktok', 'TikTokClient'),
        }
        for platform, (module_path, class_name) in platform_map.items():
            if settings.SOCIAL_MEDIA[platform]['enabled']:
                try:
                    import importlib
                    module = importlib.import_module(module_path)
                    client = getattr(module, class_name)()
                    # Auto-login for Instagram
                    if platform == 'instagram' and hasattr(client, 'login'):
                        client.login()
                    self.social_clients[platform] = client
                    logger.info(f"✅ {platform.capitalize()} client ready")
                except Exception as e:
                    logger.warning(f"⚠️ Could not init {platform} client: {e}")

    # ------------------------------------------------------------------
    # Main pipeline
    # ------------------------------------------------------------------

    def process_session(self, session_type: str) -> bool:
        """Run the full pipeline for the given session type; return True on success."""
        start = datetime.now()
        logger.info(f"🚀 Starting {session_type.upper()} session at {start}")

        try:
            # 1. Check video availability
            if self.file_manager.get_video_count(session_type) == 0:
                logger.error(f"❌ No videos in '{session_type}' folder")
                self._update_stats(False)
                return False

            # 2. Load video
            video = self.file_manager.get_video_from_folder(session_type)
            if not video:
                self._update_stats(False)
                return False

            # 3. Generate AI metadata
            logger.info(f"🤖 Generating metadata for: {video['name']}")
            metadata = self.ai_client.generate_metadata(session_type, video['name'])
            if not metadata:
                logger.error("❌ Metadata generation failed")
                self._update_stats(False)
                return False

            # 4. Upload to YouTube
            logger.info("📤 Uploading to YouTube...")
            youtube_id = self.youtube_client.upload_video(
                video['content'],
                metadata.get('youtube', {}),
                session_type
            )

            if not youtube_id:
                logger.error("❌ YouTube upload failed")
                self._update_stats(False)
                return False

            # 5. Share to social media
            social_results = {}
            if self.social_clients:
                social_results = self._share_to_social(video['content'], metadata, session_type)

            # 6. Archive video
            self.file_manager.archive_video(video, session_type, youtube_id)

            duration = (datetime.now() - start).total_seconds()
            self._log_success(session_type, video, metadata, youtube_id, duration, social_results)
            self._display_summary(session_type, youtube_id, social_results)
            self._update_stats(True, social_results)
            return True

        except Exception as e:
            logger.error(f"💥 Critical error in {session_type} session: {e}")
            import traceback; traceback.print_exc()
            self._update_stats(False)
            return False

    # ------------------------------------------------------------------
    # Social sharing
    # ------------------------------------------------------------------

    def _share_to_social(self, video_content: bytes, metadata: dict, session_type: str) -> dict:
        results = {'successful': [], 'failed': [], 'details': {}}
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                tmp.write(video_content)
                temp_path = tmp.name

            for platform, client in self.social_clients.items():
                try:
                    logger.info(f"📤 Sharing to {platform.capitalize()}...")
                    platform_meta = metadata.get(platform, {})

                    if hasattr(client, 'upload_reel'):
                        result = client.upload_reel(temp_path, platform_meta, session_type)
                    else:
                        result = client.upload_video(temp_path, platform_meta, session_type)

                    if result:
                        results['successful'].append(platform)
                        results['details'][platform] = result
                        logger.info(f"✅ {platform.capitalize()} done: {result}")
                        time.sleep(settings.SOCIAL_POST_DELAYS.get(platform, 5))
                    else:
                        results['failed'].append(platform)

                except Exception as e:
                    logger.error(f"💥 {platform} error: {e}")
                    results['failed'].append(platform)

        except Exception as e:
            logger.error(f"💥 Social sharing setup error: {e}")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

        logger.info(
            f"📊 Social results: {len(results['successful'])} OK, {len(results['failed'])} failed"
        )
        return results

    # ------------------------------------------------------------------
    # Health / stats
    # ------------------------------------------------------------------

    def check_video_availability(self) -> dict:
        availability = {}
        storage = self.file_manager.get_storage_stats()
        for st in ['morning', 'noon', 'evening']:
            videos = self.file_manager.list_available_videos(st)
            availability[st] = {
                'count': len(videos),
                'videos': videos,
                'total_size_mb': storage[st]['size_mb']
            }
        availability['storage_stats'] = storage
        return availability

    def health_check(self) -> dict:
        health = {
            'directories': {n: os.path.exists(p) for n, p in settings.LOCAL_FOLDERS.items()},
            'ai_service': False,
            'social_clients': {},
            'overall': False,
        }
        try:
            test = self.ai_client.generate_metadata('morning')
            health['ai_service'] = test is not None
        except Exception:
            pass

        for platform, cfg in settings.SOCIAL_MEDIA.items():
            health['social_clients'][platform] = (
                platform in self.social_clients if cfg['enabled'] else 'disabled'
            )

        health['overall'] = all(health['directories'].values()) and health['ai_service']
        return health

    def get_system_stats(self) -> dict:
        total = self.stats['total_processed']
        rate = f"{(self.stats['successful_uploads'] / total * 100):.1f}%" if total else "0%"
        return {
            'stats': self.stats,
            'storage': self.file_manager.get_storage_stats(),
            'success_rate': rate,
            'social_clients': len(self.social_clients),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_stats(self, success: bool, social_results: dict = None):
        self.stats['total_processed'] += 1
        self.stats['last_session'] = datetime.now()
        if success:
            self.stats['successful_uploads'] += 1
            if social_results:
                self.stats['social_shares'] += len(social_results.get('successful', []))
        else:
            self.stats['failed_uploads'] += 1

    def _log_success(self, session_type, video, metadata, youtube_id, duration, social_results):
        try:
            log_path = os.path.join(settings.LOGS_DIR, "successful_uploads.log")
            entry = (
                f"\n✅ UPLOAD — {session_type.upper()}\n"
                f"{'='*42}\n"
                f"Time:     {datetime.now()}\n"
                f"Video:    {video['name']}\n"
                f"YT URL:   https://youtube.com/watch?v={youtube_id}\n"
                f"Duration: {duration:.1f}s\n"
                f"Title:    {metadata.get('youtube', {}).get('title', 'N/A')}\n"
            )
            if social_results and social_results.get('successful'):
                for p in social_results['successful']:
                    entry += f"  • {p}: {social_results['details'].get(p, 'OK')}\n"
            entry += '='*42
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(entry)
        except Exception as e:
            logger.error(f"💥 Log write error: {e}")

    def _display_summary(self, session_type, youtube_id, social_results):
        print(f"\n{'='*60}")
        print(f"🎉 {session_type.upper()} SESSION COMPLETE")
        print(f"📺 https://youtube.com/watch?v={youtube_id}")
        if social_results:
            for p in social_results.get('successful', []):
                print(f"  ✅ {p.capitalize()}: {social_results['details'].get(p, 'OK')}")
            for p in social_results.get('failed', []):
                print(f"  ❌ {p.capitalize()}: failed")
        print('='*60)
