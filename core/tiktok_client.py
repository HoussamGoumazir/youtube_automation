import os
import time
import json
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

    def _init_driver(self):
        """تهيئة متصفح كروم"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--window-size=1920,1080")
        
        # لتجنب اكتشاف الأتمتة
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # حقن سكريبت لتجاوز navigator.webdriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
        except Exception as e:
            logger.error(f"💥 Failed to initialize Chrome driver: {str(e)}")
            return False

    def _login(self):
        """تسجيل الدخول باستخدام session_id cookies"""
        try:
            logger.info("🔐 Logging into TikTok using session cookies...")
            self.driver.get('https://www.tiktok.com/')
            
            # إضافة الكوكيز
            # ملاحظة: sessionid هو الأهم
            cookie = {'name': 'sessionid', 'value': self.session_id, 'domain': '.tiktok.com'}
            self.driver.add_cookie(cookie)
            
            # تحديث الصفحة لتطبيق الكوكيز
            self.driver.refresh()
            time.sleep(5)
            
            # التحقق من تسجيل الدخول (البحث عن زر upload أو profile)
            if "login" not in self.driver.current_url:
                logger.info("✅ IPv4 TikTok Login successful")
                return True
            else:
                logger.warning("⚠️ TikTok Login failed or redirected to login page")
                return False
                
        except Exception as e:
            logger.error(f"💥 TikTok login error: {str(e)}")
            return False

    def upload_video(self, video_path, metadata, session_type):
        """رفع فيديو على تيكتوك باستخدام المتصفح"""
        if not self._init_driver():
            return None
            
        try:
            if not self._login():
                return None
            
            logger.info("🎵 Starting TikTok upload via Browser...")
            self.driver.get('https://www.tiktok.com/upload?lang=en')
            
            # انتظار تحميل iframe الرفع أو زر الرفع
            # TikTok يغير الـ selectors باستمرار، هذا الجزء وتحدي
            # سنحاول العثور على input file مباشرة
            
            time.sleep(5)
            
            # العثور على حقل رفع الملف
            file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
            file_input.send_keys(os.path.abspath(video_path))
            
            logger.info("📤 Video file selected, waiting for upload...")
            
            # انتظار اكتمال الرفع (يمكن مراقبة نسبة التقدم أو ظهور نص معين)
            # سننتظر وقتاً كافياً مبدئياً او حتى ظهور حقل "Caption"
            
            # الانتظار حتى يصبح div الـ caption قابلاً للكتابة
            caption_box = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'notranslate public-DraftEditor-content')]"))
            )
            
            # كتابة الوصف
            # Metadata now contains specific tikok caption
            caption_text = metadata.get('caption', '')
            if not caption_text:
                title = self._build_tiktok_title(metadata, session_type)
                hashtags = self._build_tiktok_hashtags(metadata)
                caption_text = f"{title} {' '.join(hashtags)}"
            
            caption_box.send_keys(caption_text)
            time.sleep(2)
             
            # التحقق من اكتمال الرفع (اختفاء شريط التقدم او ظهور معاينة)
            time.sleep(10) # انتظار بسيط للتأكد
            
            # النقر على زر Post
            # البحث عن زر يحتوي على نص "Post"
            post_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post')]")
            
            # التمرير للزر والنقر
            self.driver.execute_script("arguments[0].scrollIntoView();", post_button)
            time.sleep(1)
            post_button.click()
            
            logger.info("✅ Clicked Post button")
            
            # انتظار رسالة النجاح او التحويل
            time.sleep(10)
            
            # إغلاق المتصفح
            self.driver.quit()
            
            logger.info("✅ TikTok upload process completed")
            return "uploaded_via_selenium"
            
        except Exception as e:
            logger.error(f"💥 TikTok upload error: {str(e)}")
            if self.driver:
                self.driver.save_screenshot(f"tiktok_error_{time.time()}.png")
                self.driver.quit()
            return None

    def _build_tiktok_title(self, metadata, session_type):
        """بناء عنوان مناسب لتيكتوك"""
        if session_type == 'morning':
            return f"POV: the coffee mug every morning ☕💀"
        elif session_type == 'noon':
            return f"Midday object struggles 😂"
        else:
            return f"Late night thoughts from your objects 🛌👀"
    
    def _build_tiktok_hashtags(self, metadata):
        """بناء هاشتاقات تيكتوك"""
        base_hashtags = ["#fyp", "#funny", "#animation", "#objectlife"]
        additional_hashtags = metadata.get('hashtags', [])[:5]
        return base_hashtags + additional_hashtags