"""
uploaders/facebook.py
Facebook Reels uploader — moved from core/facebook_client.py.
"""

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

    def upload_video(self, video_path: str, metadata: dict, session_type: str):
        """Upload a video reel to a Facebook page and return the post ID."""
        try:
            logger.info("📘 Starting Facebook upload...")

            # 1. Create upload session
            upload_url = f"{self.base_url}/{self.page_id}/video_reels"
            params = {
                'access_token': self.access_token,
                'upload_phase': 'start',
                'file_size': os.path.getsize(video_path)
            }
            resp = requests.post(upload_url, params=params, timeout=30)
            if resp.status_code != 200:
                logger.error(f"❌ Failed to start upload session: {resp.text[:200]}")
                return None

            session_data = resp.json()
            video_id = session_data.get('video_id')
            upload_endpoint = session_data.get('upload_url')

            # 2. Upload file bytes
            with open(video_path, 'rb') as vf:
                upload_resp = requests.post(upload_endpoint, files={'video_file': vf}, timeout=120)
            if upload_resp.status_code != 200:
                logger.error(f"❌ Video upload failed: {upload_resp.text[:200]}")
                return None

            # 3. Publish with description
            description = metadata.get('post_text', '') or self._build_description(metadata, session_type)
            publish_resp = requests.post(
                f"{self.base_url}/{video_id}",
                data={
                    'access_token': self.access_token,
                    'description': description,
                    'published': 'true'
                },
                timeout=30
            )

            if publish_resp.status_code == 200:
                post_id = publish_resp.json().get('id')
                logger.info(f"✅ Facebook upload successful! Post ID: {post_id}")
                return post_id

            logger.error(f"❌ Facebook publish failed: {publish_resp.text[:200]}")
            return None

        except Exception as e:
            logger.error(f"💥 Facebook upload error: {e}")
            return None

    def _build_description(self, metadata: dict, session_type: str) -> str:
        emoji_map = {'morning': '☕', 'noon': '🪑', 'evening': '🛌'}
        emoji = emoji_map.get(session_type, '🎬')
        title = metadata.get('title', '')
        hashtags = metadata.get('hashtags', [])

        desc = f"{title}\n\nA new Object Life short has dropped! {emoji}\n\n"
        desc += "Welcome to Object Life — where everyday objects have thoughts too.\n"
        desc += "Follow us for more funny animated shorts!\n\n"
        if hashtags:
            desc += " ".join(hashtags[:10])
        return desc
