"""
uploaders/youtube.py
YouTube uploader — moved from core/youtube_client.py.
No logic changes; imports updated to use new package paths.
"""

import os
import pickle
import tempfile
import time
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.readonly'
]


class AdvancedYouTubeClient:
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        """OAuth 2.0 authentication with token caching."""
        creds = None
        token_file = os.path.join(settings.CONFIG_DIR, 'youtube_token.pickle')
        os.makedirs(settings.CONFIG_DIR, exist_ok=True)

        try:
            if os.path.exists(token_file):
                with open(token_file, 'rb') as f:
                    creds = pickle.load(f)
                logger.info("🔑 Loaded existing YouTube credentials")

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("🔄 Refreshing expired credentials")
                    creds.refresh(Request())
                else:
                    credentials_path = os.path.join(settings.BASE_DIR, 'youtube_credentials.json')
                    if not os.path.exists(credentials_path):
                        raise FileNotFoundError(f"YouTube credentials file not found: {credentials_path}")
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0, open_browser=True)

                with open(token_file, 'wb') as f:
                    pickle.dump(creds, f)
                logger.info("💾 Saved new YouTube credentials")

            self.service = build('youtube', 'v3', credentials=creds)
            logger.info("✅ YouTube authentication successful")

        except Exception as e:
            logger.error(f"💥 YouTube authentication failed: {e}")
            raise

    def upload_video(self, video_content: bytes, metadata: dict, session_type: str):
        """Upload a video bytes object to YouTube and return its video ID."""
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                tmp.write(video_content)
                temp_path = tmp.name

            description = self._build_description(metadata)
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

            media = MediaFileUpload(temp_path, chunksize=1024 * 1024, resumable=True, mimetype='video/mp4')
            logger.info(f"📤 Uploading to YouTube — '{body['snippet']['title']}'")

            request = self.service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            response = self._execute_resumable_upload(request)

            if response:
                video_id = response['id']
                logger.info(f"🎉 YouTube upload done! https://youtube.com/watch?v={video_id}")
                return video_id

            logger.error("❌ YouTube upload returned no response")
            return None

        except HttpError as e:
            logger.error(f"💥 YouTube API HttpError: {e}")
            if e.resp.status in [403, 409]:
                logger.error("🔒 Possible quota exceeded or duplicate upload")
            return None
        except Exception as e:
            logger.error(f"💥 Upload error: {e}")
            return None
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    def _execute_resumable_upload(self, request):
        """Execute a resumable upload with exponential back-off."""
        max_retries, delay = 3, 5
        for attempt in range(max_retries):
            try:
                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        logger.info(f"📊 Upload progress: {int(status.progress() * 100)}%")
                return response
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504] and attempt < max_retries - 1:
                    logger.warning(f"🔄 Server error — retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"🔄 Upload error — retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise
        return None

    def _build_description(self, metadata: dict) -> str:
        description = metadata.get('description', '')
        if len(description) > 5000:
            description = description[:4990] + "\n..."
        return description

    def get_channel_info(self):
        """Return basic channel info for the authenticated account."""
        try:
            response = self.service.channels().list(part='snippet', mine=True).execute()
            if response.get('items'):
                channel = response['items'][0]
                logger.info(f"📺 Channel: {channel['snippet']['title']}")
                return channel
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch channel info: {e}")
        return None
