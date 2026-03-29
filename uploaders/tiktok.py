"""
uploaders/tiktok.py
TikTok browser-automation uploader — moved from core/tiktok_client.py.
"""

import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class TikTokClient:
    def __init__(self):
        self.session_id = settings.SOCIAL_MEDIA['tiktok']['session_id']
        self.headless = settings.SOCIAL_MEDIA['tiktok']['headless']
        self.driver = None

    # ------------------------------------------------------------------
    # Browser setup
    # ------------------------------------------------------------------

    def _init_driver(self) -> bool:
        """Initialise a headless Chrome browser."""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        for arg in ['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
                    '--window-size=1920,1080', '--disable-blink-features=AutomationControlled']:
            options.add_argument(arg)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            return True
        except Exception as e:
            logger.error(f"💥 Chrome driver init failed: {e}")
            return False

    def _login(self) -> bool:
        """Inject session cookie to authenticate on TikTok."""
        try:
            logger.info("🔐 Logging into TikTok via session cookie...")
            self.driver.get('https://www.tiktok.com/')
            self.driver.add_cookie({'name': 'sessionid', 'value': self.session_id, 'domain': '.tiktok.com'})
            self.driver.refresh()
            time.sleep(5)

            if "login" not in self.driver.current_url:
                logger.info("✅ TikTok login successful")
                return True

            logger.warning("⚠️ TikTok login failed — still on login page")
            return False
        except Exception as e:
            logger.error(f"💥 TikTok login error: {e}")
            return False

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    def upload_video(self, video_path: str, metadata: dict, session_type: str):
        """Upload a video to TikTok via browser automation."""
        if not self._init_driver():
            return None

        try:
            if not self._login():
                return None

            logger.info("🎵 Starting TikTok upload...")
            self.driver.get('https://www.tiktok.com/upload?lang=en')
            time.sleep(5)

            # Select file
            file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
            file_input.send_keys(os.path.abspath(video_path))
            logger.info("📤 File selected, waiting for upload...")

            # Wait for caption editor
            caption_box = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'notranslate public-DraftEditor-content')]")
                )
            )

            # Build caption
            caption_text = metadata.get('caption', '') or self._build_caption(metadata, session_type)
            caption_box.send_keys(caption_text)
            time.sleep(2)
            time.sleep(10)  # Let the upload progress bar finish

            # Click Post
            post_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post')]")
            self.driver.execute_script("arguments[0].scrollIntoView();", post_btn)
            time.sleep(1)
            post_btn.click()
            logger.info("✅ Clicked Post button")
            time.sleep(10)

            self.driver.quit()
            logger.info("✅ TikTok upload completed")
            return "uploaded_via_selenium"

        except Exception as e:
            logger.error(f"💥 TikTok upload error: {e}")
            if self.driver:
                self.driver.save_screenshot(f"tiktok_error_{int(time.time())}.png")
                self.driver.quit()
            return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_caption(self, metadata: dict, session_type: str) -> str:
        title_map = {
            'morning': "POV: the coffee mug every morning ☕💀",
            'noon': "Midday object struggles 😂",
            'evening': "Late night thoughts from your objects 🛌👀"
        }
        title = title_map.get(session_type, "Object Life 😂")
        base_tags = ["#fyp", "#funny", "#animation", "#objectlife"]
        extra_tags = metadata.get('hashtags', [])[:5]
        return f"{title} {' '.join(base_tags + extra_tags)}"
