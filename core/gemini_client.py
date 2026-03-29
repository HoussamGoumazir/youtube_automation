import os
import requests
import json
import re
import time
from utils.logger import get_logger
from utils.seo_analyzer import SEOAnalyzer
from config.settings import settings

logger = get_logger(__name__)

class AdvancedGeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = settings.GEMINI_API_URL  # استخدام الرابط من الإعدادات
        self.seo_analyzer = SEOAnalyzer()
        self.retry_count = 3
        self.retry_delay = 2
    
    def generate_metadata(self, session_type, video_name="Object Animation"):
        """توليد بيانات وصفية محسنة لتحسين SEO"""
        for attempt in range(self.retry_count):
            try:
                prompt = self._get_prompt(session_type, video_name)
                if not prompt:
                    logger.error(f"❌ No prompt found for session type: {session_type}")
                    return self._get_fallback_metadata(session_type)
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.8,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 2000,
                    }
                }
                
                logger.info(f"🤖 Generating AI metadata for {session_type} (Attempt {attempt + 1})...")
                response = requests.post(
                    f"{self.base_url}?key={self.api_key}",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text_result = data['candidates'][0]['content']['parts'][0]['text']
                    
                    # استخراج JSON من النص
                    json_match = re.search(r'\{.*\}', text_result, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        metadata = json.loads(json_str)
                        
                        # تحسين SEO skipped as structure is now complex
                        # optimized_metadata = self.seo_analyzer.optimize_metadata(metadata, session_type)
                        
                        logger.info(f"✅ AI metadata generated successfully (SEO: {metadata.get('seo_score', 'N/A')}/100)")
                        return metadata
                    else:
                        logger.warning("❌ No JSON found in AI response, using fallback")
                else:
                    logger.error(f"❌ Gemini API error: {response.status_code} - {response.text}")
                    
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"💥 Error in AI generation (attempt {attempt + 1}): {str(e)}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
        
        logger.error("❌ All AI generation attempts failed, using fallback")
        return self._get_fallback_metadata(session_type)
    
    def _get_prompt(self, session_type, video_name="Object Animation"):
        """الحصول على الـ prompt المناسب"""
        return settings.get_seo_optimized_prompt(session_type, video_name)
    
    def _get_fallback_metadata(self, session_type):
        """بيانات احتياطية محسنة لـ Object Life"""
        fallback_templates = {
            'morning': {
                "youtube": {
                    "title": "When Your Coffee Mug Realizes What Happens Every Morning ☕️💀",
                    "description": "Welcome to Object Life — where everyday objects have thoughts too.\\n\\nFollow for more funny animated shorts!",
                    "tags": ["shorts", "funny", "animation", "objectlife", "viral"],
                    "pinned_comment": "What object should we animate next? 👇"
                },
                "instagram": {
                    "caption": "POV: The coffee mug is more tired than you 😂☕\\n\\n#ObjectLife #Funny #Animation",
                    "hashtags": ["#ObjectLife", "#Funny", "#Animation", "#ComedyReels"]
                },
                "tiktok": {
                    "caption": "What your coffee mug really thinks 😂 #fyp #objectlife #funny #animation",
                    "hashtags": ["#fyp", "#objectlife", "#funny", "#animation"],
                    "visual_overlay": "Wait for the mug's face ☕💀"
                },
                "facebook": {
                    "post_text": "Tag someone who needs their morning coffee 😂☕",
                    "hashtags": ["#ObjectLife", "#Funny", "#Animation"]
                },
                "engagement_strategy": {
                    "opening_hook": "POV: Every object has feelings 🥺",
                    "cta_used": "🔔 Subscribe to Object Life for more funny animated shorts!"
                },
                "seo_score": 75
            },
            'noon': {
                "youtube": {
                    "title": "When Your Office Chair Has Had Enough 🪑😡",
                    "description": "Welcome to Object Life — where everyday objects have thoughts too.\\n\\nFollow for more funny animated shorts!",
                    "tags": ["shorts", "funny", "animation", "objectlife", "officecomedy"],
                    "pinned_comment": "Has your chair complained lately? 🪑"
                },
                "instagram": {
                    "caption": "POV: Your office chair during the midday slump 😂🪑\\n\\n#ObjectLife #Funny #Animation",
                    "hashtags": ["#ObjectLife", "#Funny", "#Animation", "#OfficeComedy"]
                },
                "tiktok": {
                    "caption": "What your chair really thinks 😂 #fyp #objectlife #funny #animation",
                    "hashtags": ["#fyp", "#objectlife", "#funny", "#animation"],
                    "visual_overlay": "The chair's reaction 😂"
                },
                "facebook": {
                    "post_text": "Tag your coworker who sits like this 😂🪑",
                    "hashtags": ["#ObjectLife", "#Funny", "#Animation"]
                },
                "engagement_strategy": {
                    "opening_hook": "This is way too relatable 💀",
                    "cta_used": "🔔 Subscribe to Object Life for more funny animated shorts!"
                },
                "seo_score": 75
            },
            'evening': {
                "youtube": {
                    "title": "Your Pillow Judging You For Staying Up Late 🛌👀",
                    "description": "Welcome to Object Life — where everyday objects have thoughts too.\\n\\nFollow for more funny animated shorts!",
                    "tags": ["shorts", "funny", "animation", "objectlife", "latenight"],
                    "pinned_comment": "What time did you go to sleep yesterday? 🛌"
                },
                "instagram": {
                    "caption": "POV: It's 3 AM and your pillow has had enough 👀🛌\\n\\n#ObjectLife #Funny #Animation",
                    "hashtags": ["#ObjectLife", "#Funny", "#Animation", "#LateNightThoughts"]
                },
                "tiktok": {
                    "caption": "Go to sleep already! 😂 #fyp #objectlife #funny #animation",
                    "hashtags": ["#fyp", "#objectlife", "#funny", "#animation"],
                    "visual_overlay": "When it's 3 AM..."
                },
                "facebook": {
                    "post_text": "Who else stays up way too late? 🙋‍♂️🛌",
                    "hashtags": ["#ObjectLife", "#Funny", "#Animation"]
                },
                "engagement_strategy": {
                    "opening_hook": "When your objects speak the truth 🗣️",
                    "cta_used": "🔔 Subscribe to Object Life for more funny animated shorts!"
                },
                "seo_score": 75
            }
        }
        
        metadata = fallback_templates.get(session_type, fallback_templates['morning'])
        return metadata