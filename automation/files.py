"""
automation/files.py
File management — moved from core/file_manager.py.
No logic changes; imports updated.
"""

import os
import glob
import shutil
import hashlib
from datetime import datetime

from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

VIDEO_EXTENSIONS = ['*.mp4', '*.mov', '*.avi', '*.mkv']


class AdvancedFileManager:
    def __init__(self):
        self._ensure_directories()
        self._create_readme_files()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _ensure_directories(self):
        dirs = [settings.VIDEOS_DIR, settings.ARCHIVE_DIR,
                settings.LOGS_DIR, settings.CONFIG_DIR,
                *settings.LOCAL_FOLDERS.values()]
        for d in dirs:
            os.makedirs(d, exist_ok=True)

    def _create_readme_files(self):
        notes = {
            settings.LOCAL_FOLDERS['morning']: (
                "📁 Morning Videos\nPlace Object Life morning videos here.\nMP4 format only."
            ),
            settings.LOCAL_FOLDERS['noon']: (
                "📁 Noon Videos\nPlace Object Life midday / work videos here.\nMP4 format only."
            ),
            settings.LOCAL_FOLDERS['evening']: (
                "📁 Evening Videos\nPlace Object Life evening / night videos here.\nMP4 format only."
            ),
            settings.ARCHIVE_DIR: (
                "📁 Archive\nSuccessfully uploaded videos are moved here automatically."
            ),
        }
        for folder, note in notes.items():
            path = os.path.join(folder, "README.txt")
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(note)

    # ------------------------------------------------------------------
    # Video access
    # ------------------------------------------------------------------

    def get_video_from_folder(self, session_type: str) -> dict | None:
        """Return info dict for the oldest video in the given session folder."""
        try:
            folder = settings.LOCAL_FOLDERS[session_type]
            files = []
            for ext in VIDEO_EXTENSIONS:
                files.extend(glob.glob(os.path.join(folder, ext)))

            if not files:
                logger.warning(f"📭 No videos in {folder}")
                return None

            files.sort(key=os.path.getmtime)
            path = files[0]
            name = os.path.basename(path)
            stat = os.stat(path)

            with open(path, 'rb') as f:
                content = f.read()

            info = {
                'path': path,
                'name': name,
                'content': content,
                'size_bytes': len(content),
                'size_mb': round(stat.st_size / 1_048_576, 2),
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'file_hash': self._md5(path),
                'session_type': session_type,
            }
            logger.info(f"📹 Using video: {name} ({info['size_mb']} MB)")
            return info

        except Exception as e:
            logger.error(f"💥 Error reading video: {e}")
            return None

    def get_video_count(self, session_type: str) -> int:
        folder = settings.LOCAL_FOLDERS[session_type]
        return sum(len(glob.glob(os.path.join(folder, ext))) for ext in VIDEO_EXTENSIONS)

    def list_available_videos(self, session_type: str) -> list:
        folder = settings.LOCAL_FOLDERS[session_type]
        videos = []
        for ext in VIDEO_EXTENSIONS:
            for p in glob.glob(os.path.join(folder, ext)):
                stat = os.stat(p)
                videos.append({
                    'name': os.path.basename(p),
                    'size_mb': round(stat.st_size / 1_048_576, 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    'path': p,
                })
        videos.sort(key=lambda x: x['modified'])
        return videos

    # ------------------------------------------------------------------
    # Archiving
    # ------------------------------------------------------------------

    def archive_video(self, video_info: dict, session_type: str, youtube_id: str = None) -> bool:
        """Move the uploaded video to the archive folder."""
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(video_info['name'])
            yt = f"_{youtube_id}" if youtube_id else ""
            dest_name = f"{session_type}_{ts}{yt}_{base}{ext}"
            dest = os.path.join(settings.ARCHIVE_DIR, dest_name)

            shutil.move(video_info['path'], dest)

            meta = os.path.join(settings.ARCHIVE_DIR, f"{dest_name}.meta")
            with open(meta, 'w', encoding='utf-8') as f:
                f.write(
                    f"Original: {video_info['name']}\n"
                    f"Session: {session_type}\n"
                    f"Archived: {datetime.now().isoformat()}\n"
                    f"YouTube ID: {youtube_id or 'N/A'}\n"
                    f"Size: {video_info['size_mb']} MB\n"
                )

            logger.info(f"✅ Archived: {video_info['name']} → {dest_name}")
            return True

        except Exception as e:
            logger.error(f"💥 Archiving error: {e}")
            return False

    # ------------------------------------------------------------------
    # Storage stats
    # ------------------------------------------------------------------

    def get_storage_stats(self) -> dict:
        stats = {}
        for st in ['morning', 'noon', 'evening']:
            folder = settings.LOCAL_FOLDERS[st]
            size, count = 0, 0
            for ext in VIDEO_EXTENSIONS:
                for p in glob.glob(os.path.join(folder, ext)):
                    size += os.path.getsize(p)
                    count += 1
            stats[st] = {'count': count, 'size_mb': round(size / 1_048_576, 2)}

        stats['total'] = {
            'count': sum(s['count'] for s in stats.values()),
            'size_mb': round(sum(s['size_mb'] for s in stats.values()), 2),
        }
        return stats

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _md5(path: str) -> str:
        h = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
