"""
uploaders/instagram.py
Instagram Reels uploader using instagrapi — moved from core/instagram_client.py.
"""

import os
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

    def login(self) -> bool:
        """Login to Instagram; return True on success."""
        try:
            if not self.username or self.username.startswith('YOUR_'):
                logger.warning("⚠️ Instagram credentials not configured — skipping login")
                return False

            logger.info(f"🔐 Logging into Instagram as @{self.username}...")
            self.client.login(self.username, self.password)
            self.is_authenticated = True
            logger.info("✅ Instagram login successful!")
            return True

        except Exception as e:
            logger.error(f"💥 Instagram login failed: {e}")
            return False

    def upload_reel(self, video_path: str, metadata: dict, session_type: str):
        """Upload a video as an Instagram Reel; return media ID on success."""
        if not self.is_authenticated and not self.login():
            logger.error("❌ Instagram upload aborted: not authenticated")
            return None

        try:
            if not os.path.exists(video_path):
                logger.error(f"❌ Video file not found: {video_path}")
                return None

            caption = metadata.get('caption', '') or self._build_caption(metadata, session_type)
            logger.info("📸 Uploading Instagram Reel...")
            media = self.client.clip_upload(path=video_path, caption=caption)

            if media and media.pk:
                logger.info(f"✅ Instagram Reel uploaded! https://instagram.com/p/{media.code}/")
                return media.pk

            logger.error("❌ Instagram upload returned no media ID")
            return None

        except Exception as e:
            logger.error(f"💥 Instagram upload error: {e}")
            return None

    def _build_caption(self, metadata: dict, session_type: str) -> str:
        emoji_map = {'morning': '☕', 'noon': '🪑', 'evening': '🛌'}
        emoji = emoji_map.get(session_type, '🎬')
        title = metadata.get('title', '')
        hashtags = metadata.get('hashtags', [])

        base_tags = ["#ObjectLife", "#Funny", "#Animation", "#ComedyReels",
                     "#Relatable", "#ViralShorts", "#Humor", "#DailyStruggles", "#Shorts"]
        all_tags = list(set(base_tags + hashtags))[:30]

        caption = f"{title}\n\n{emoji} The daily life of your objects ✨\n\nWait for it... 😂\n\n"
        caption += " ".join(all_tags)
        return caption
