"""
ai/prompts.py
Centralized prompt templates for the Object Life channel.
All AI prompt logic has been separated from config/settings.py.
"""

from config.settings import settings


def get_seo_optimized_prompt(session_type: str, video_name: str = "Object Animation") -> str:
    """
    Build and return the full AI prompt for a given session type and video name.
    This is the main prompt used to generate viral metadata via Gemini.
    """
    seo = settings.SEO_SETTINGS
    tone = seo['tones'].get(session_type, "Funny and Relatable")
    cta = seo['ctas'].get(session_type if session_type in seo['ctas'] else 'youtube', seo['ctas']['youtube'])

    return f"""
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


def get_platform_specific_prompt(platform: str, session_type: str) -> str:
    """Return a platform-specific fallback prompt string."""
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
    return prompts.get(platform, {}).get(session_type, "POV: Everyday objects having feelings 😂 #ObjectLife #Funny")


def get_platform_hashtags(platform: str, session_type: str) -> list:
    """Return a list of platform-specific hashtags for a session type."""
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
    return hashtags.get(platform, {}).get(session_type, ["#ObjectLife", "#Funny", "#Animation", "#Shorts"])
