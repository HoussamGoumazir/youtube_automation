import os
from config.settings import settings

class Credentials:
    # Gemini AI - نستخدم المفتاح من الإعدادات
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    
    # YouTube API - سيتم استخدام ملف youtube_credentials.json
    YOUTUBE_CLIENT_ID = "YOUR_YOUTUBE_CLIENT_ID"
    YOUTUBE_CLIENT_SECRET = "YOUR_YOUTUBE_CLIENT_SECRET"
    
    # Google Drive Scopes (للتحضير للمستقبل)
    DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

credentials = Credentials()