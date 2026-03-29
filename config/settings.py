import os
from datetime import datetime

class Settings:
    # المسارات
    BASE_DIR = "/home/houssam/Documents/youtube_automation"
    VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
    ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    CONFIG_DIR = os.path.join(BASE_DIR, "config")
    
    # مجلدات الفيديوهات
    LOCAL_FOLDERS = {
        'morning': os.path.join(VIDEOS_DIR, "morning"),
        'noon': os.path.join(VIDEOS_DIR, "noon"),
        'evening': os.path.join(VIDEOS_DIR, "evening")
    }
    
    # إعدادات اليوتيوب
    YOUTUBE_CATEGORY = "24"  # Entertainment
    PRIVACY_STATUS = "public"
    DEFAULT_LANGUAGE = "en"
    
    # إعدادات الذكاء الاصطناعي - Gemini API
    GEMINI_MODEL = "gemini-1.5-flash"
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    # إعدادات SEO ورفع التفاعل
    SEO_SETTINGS = {
        'max_title_length': 60,
        'max_description_length': 5000,
        'min_hashtags': 5,
        'max_hashtags': 15,
        'trending_keywords': ['funny', 'animation', 'object life', 'shorts', 'viral', 'humor', 'relatable', 'comedy'],
        
        # استراتيجيات جذب الانتباه (Hooks)
        'engagement_hooks': [
            "Wait for the end... 😂",
            "POV: Every object has feelings 🥺",
            "This is way too relatable 💀",
            "Did not expect that reaction 🤣",
            "When your objects speak the truth 🗣️"
        ],
        
        # عبارات الحث على اتخاذ إجراء (CTAs)
        'ctas': {
            'youtube': "🔔 Subscribe to Object Life for more funny animated shorts!",
            'instagram': "🔗 Follow for more Object Life comedy!",
            'tiktok': "❤️ Like & Follow for more funny objects!",
            'facebook': "💬 Tag a friend who relates to this!"
        },
        
        # التوجه العاطفي (Tone)
        'tones': {
            'morning': "Humorous, Relatable, Lighthearted, Breakfast/Morning objects",
            'noon': "Funny, Sarcastic, Work/Lunch objects, Midday struggles",
            'evening': "Cozy comedy, Sleepy, Evening/Night objects, Late night thoughts"
        }
    }
    
    # إعدادات وسائل التواصل الاجتماعي
    SOCIAL_MEDIA = {
        'facebook': {
            'enabled': False,  # قم بتغييرها لـ True عندما تحصل على API Keys
            'page_id': 'YOUR_FACEBOOK_PAGE_ID',
            'access_token': 'YOUR_FACEBOOK_ACCESS_TOKEN',
            'app_id': 'YOUR_FACEBOOK_APP_ID',
            'app_secret': 'YOUR_FACEBOOK_APP_SECRET'
        },
        'instagram': {
            'enabled': False,  # Set to True when credentials are set
            'username': 'YOUR_INSTAGRAM_USERNAME',
            'password': 'YOUR_INSTAGRAM_PASSWORD',
            'business_account_id': '' # Kept for backward compatibility if needed, but not used by instagrapi
        },
        'tiktok': {
            'enabled': False,  # Set to True when credentials are set
            'session_id': 'YOUR_TIKTOK_SESSION_ID', # Cookies for browser automation
            'headless': True  # Run browser in background
        }
    }
    
    # أوقات النشر على وسائل التواصل (دقائق بعد رفع اليوتيوب)
    SOCIAL_POST_DELAYS = {
        'facebook': 5,     # 5 دقائق بعد اليوتيوب
        'instagram': 10,   # 10 دقائق بعد اليوتيوب
        'tiktok': 15       # 15 دقيقة بعد اليوتيوب
    }
    
    # إعدادات المحتوى لكل منصة
    CONTENT_SETTINGS = {
        'facebook': {
            'max_video_length': 240,  # 4 دقائق
            'max_description_length': 5000,
            'supported_formats': ['.mp4', '.mov', '.avi']
        },
        'instagram': {
            'max_video_length': 90,   # 90 ثانية للريلز
            'max_caption_length': 2200,
            'supported_formats': ['.mp4', '.mov']
        },
        'tiktok': {
            'max_video_length': 180,  # 3 دقائق
            'max_description_length': 2200,
            'supported_formats': ['.mp4', '.mov']
        }
    }
    
    # إعدادات السجلات والمراقبة
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_SIZE = 10485760  # 10MB لكل ملف log
    LOG_BACKUP_COUNT = 10    # احتفظ بـ 10 ملفات سابقة
    
    # إعدادات الأمان
    ENCRYPT_TOKENS = True
    TOKEN_EXPIRY_DAYS = 30
    
    # إعدادات النظام
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_SECONDS = 5
    UPLOAD_TIMEOUT_SECONDS = 300  # 5 دقائق
    MAX_VIDEO_SIZE_MB = 500       # 500MB كحد أقصى
    
    # إعدادات الجدولة التلقائية
    SCHEDULE_SETTINGS = {
        'morning': {
            'time': '09:00',
            'enabled': True,
            'timezone': 'Africa/Casablanca'
        },
        'noon': {
            'time': '13:00',
            'enabled': True,
            'timezone': 'Africa/Casablanca'
        },
        'evening': {
            'time': '19:00',
            'enabled': True,
            'timezone': 'Africa/Casablanca'
        }
    }
    
    @staticmethod
    def get_seo_optimized_prompt(session_type, video_name="Object Animation"):
        """الحصول على محتوى مخصص لكل فترة للذكاء الاصطناعي مع استراتيجيات رفع التفاعل"""
        seo = Settings.SEO_SETTINGS
        tone = seo['tones'].get(session_type, "Funny and Relatable")
        cta = seo['ctas'].get(session_type if session_type in seo['ctas'] else 'youtube', seo['ctas']['youtube'])
        
        # We integrate the user's specific system prompt
        prompt_template = f"""
            You are an AI assistant that generates viral metadata for short-form videos.

            The channel name is "Object Life".

            Channel concept:
            Everyday objects come to life and speak like humans in funny or relatable situations.

            Your task:
            Generate optimized metadata for a SHORT video (YouTube Shorts, Instagram Reels, Facebook Reels, TikTok).
            Session Type / Context: {session_type}
            
            VIDEO INFORMATION:
            - The video is titled or described as "{video_name}". 
            - The video shows an object that is alive and reacting to its situation.
            - The tone is {tone}.
            - The audience is international (English speaking).
            
            CRITICAL: Generate specific content for EACH platform in a single JSON response.
            
            OUTPUT FORMAT FOR JSON:
            
            1. YouTube: Viral title (max 60 chars), short description encouraging people to follow the channel, 5-8 viral tags (array), and a PINNED COMMENT.
            2. Instagram: Short engaging caption that fits Reels, CTAs ({seo['ctas']['instagram']}), 5-8 viral hashtags (array).
            3. TikTok: Short engaging caption, 5-8 viral hashtags (array), and suggested "Visual Overlay Text" for the video.
            4. Facebook: Short engaging post text, 5-8 viral hashtags (array).

            RULES:
            - Keep the tone humorous, simple, and relatable.
            - Focus on relatability.
            - Avoid long explanations.
            - Optimize for virality.
            - All hashtags should relate to: shorts, animation, funny objects, viral content.

            Example style:
            Title: When Your Ice Cube Realizes It's In Lemon Water
            Caption: POV: The ice cube is enjoying the drink more than you 😂
            Description: Welcome to Object Life — where everyday objects have thoughts too.\\n\\nFollow for more funny animated shorts!
            Hashtags: ["#shorts", "#funny", "#animation", "#viralshorts", "#objectlife"]

            REQUIRED JSON STRUCTURE EXACTLY AS BELOW:
            {{
                "youtube": {{
                    "title": "...",
                    "description": "...",
                    "tags": [],
                    "pinned_comment": "..."
                }},
                "instagram": {{
                    "caption": "...",
                    "hashtags": []
                }},
                "tiktok": {{
                    "caption": "...",
                    "hashtags": [],
                    "visual_overlay": "..."
                }},
                "facebook": {{
                    "post_text": "...",
                    "hashtags": []
                }},
                "engagement_strategy": {{
                    "opening_hook": "...",
                    "cta_used": "{cta}"
                }},
                "seo_score": 95
            }}
            """
        return prompt_template
    
    @staticmethod
    def get_platform_specific_prompt(platform, session_type):
        """الحصول على محتوى مخصص لكل منصة تواصل اجتماعي"""
        prompts = {
            'facebook': {
                'morning': "POV: The coffee mug realizes what happens every morning ☕💀 #ObjectLife #Comedy #Shorts",
                'noon': "When your work desk objects start complaining about the midday slump 🤣 #Funny #ObjectLife",
                'evening': "Your pillow judging you for staying up late again 🛌👀 #Relatable #Animation #Shorts"
            },
            'instagram': {
                'morning': "Morning struggles are real... even for your objects! ☕🤣\n\n#ObjectLife #Funny #Comedy #MorningRoutine",
                'noon': "Objects at work having a meltdown 😭💻\n\n#ObjectLife #Relatable #OfficeComedy #Animation",
                'evening': "Late night object thoughts 🌙💭\n\n#ObjectLife #Funny #Relatable #Comedy"
            },
            'tiktok': {
                'morning': "What your coffee cup really thinks ☕😂 #fyp #objectlife #funny #animation",
                'noon': "Midday struggles as told by objects 😂 #fyp #comedy #objectlife #relatable",
                'evening': "When your bed is tired of you 🛏️🤣 #fyp #funny #animation #objectlife"
            }
        }
        
        platform_prompts = prompts.get(platform, {})
        return platform_prompts.get(session_type, "POV: Everyday objects having feelings 😂 #ObjectLife #Funny")
    
    @staticmethod
    def get_platform_hashtags(platform, session_type):
        """الحصول على هاشتاقات مخصصة لكل منصة"""
        hashtags = {
            'facebook': {
                'morning': ["#ObjectLife", "#Funny", "#Animation", "#MorningRoutine", "#Comedy", "#Relatable", "#Shorts"],
                'noon': ["#ObjectLife", "#Relatable", "#Comedy", "#WorkLife", "#Funny", "#Shorts"],
                'evening': ["#ObjectLife", "#Funny", "#Animation", "#LateNight", "#Comedy", "#Relatable", "#Shorts"]
            },
            'instagram': {
                'morning': ["#ObjectLife", "#Funny", "#Animation", "#ComedyReels", "#Relatable", "#MorningVibes", "#ViralShorts"],
                'noon': ["#ObjectLife", "#OfficeComedy", "#Funny", "#Relatable", "#Animation", "#ComedyReels", "#ViralReels"],
                'evening': ["#ObjectLife", "#Funny", "#Relatable", "#LateNightThoughts", "#Comedy", "#Animation", "#Reels"]
            },
            'tiktok': {
                'morning': ["#fyp", "#funny", "#animation", "#objectlife", "#comedy", "#relatable", "#shorts"],
                'noon': ["#fyp", "#funny", "#animation", "#objectlife", "#comedy", "#relatable", "#worklife"],
                'evening': ["#fyp", "#funny", "#animation", "#objectlife", "#comedy", "#relatable", "#latenight"]
            }
        }
        
        platform_hashtags = hashtags.get(platform, {})
        return platform_hashtags.get(session_type, ["#ObjectLife", "#Funny", "#Animation", "#Shorts"])
    
    @staticmethod
    def validate_settings():
        """التحقق من صحة الإعدادات"""
        errors = []
        
        # تحقق من المسارات
        required_dirs = [Settings.BASE_DIR, Settings.VIDEOS_DIR, Settings.ARCHIVE_DIR, 
                        Settings.LOGS_DIR, Settings.CONFIG_DIR]
        
        for directory in required_dirs:
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                errors.append(f"Directory creation failed for {directory}: {str(e)}")
        
        # تحقق من مجلدات الفيديوهات
        for session_type, folder_path in Settings.LOCAL_FOLDERS.items():
            try:
                os.makedirs(folder_path, exist_ok=True)
            except Exception as e:
                errors.append(f"Video folder creation failed for {session_type}: {str(e)}")
        
        # تحقق من API Keys الأساسية
        if not Settings.GEMINI_API_KEY or Settings.GEMINI_API_KEY.startswith("AIzaSy"):
            errors.append("Gemini API Key needs to be updated with a valid key from Google AI Studio")
        
        # تحقق من إعدادات وسائل التواصل
        for platform, config in Settings.SOCIAL_MEDIA.items():
            if config['enabled']:
                if platform == 'facebook':
                    if not config.get('access_token') or config.get('access_token', '').startswith('YOUR_'):
                        errors.append(f"Facebook {platform} requires valid Access Token")
                elif platform == 'instagram':
                    if not config.get('business_account_id') or config.get('business_account_id', '').startswith('YOUR_'):
                        errors.append(f"Instagram {platform} requires valid Business Account ID")
                elif platform == 'tiktok':
                    if not config.get('access_token') or config.get('access_token', '').startswith('YOUR_'):
                        errors.append(f"TikTok {platform} requires valid Access Token")
        
        return errors

settings = Settings()