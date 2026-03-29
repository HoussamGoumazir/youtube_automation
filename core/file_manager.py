import os
import glob
import shutil
import hashlib
from datetime import datetime
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

class AdvancedFileManager:
    def __init__(self):
        self._ensure_directories()
        self._create_readme_files()
    
    def _ensure_directories(self):
        """إنشاء جميع المجلدات المطلوبة"""
        directories = [
            settings.VIDEOS_DIR,
            settings.ARCHIVE_DIR,
            settings.LOGS_DIR,
            settings.CONFIG_DIR,
            *settings.LOCAL_FOLDERS.values()
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"📁 Directory ensured: {directory}")
    
    def _create_readme_files(self):
        """إنشاء ملفات إرشادية في كل مجلد"""
        readme_content = {
            settings.LOCAL_FOLDERS['morning']: """
            📁 Morning Videos Folder
            ========================
            Place your Object Life morning routine videos here.
            
            Requirements:
            - MP4 format only
            - Recommended length: 5-15 minutes
            - Morning/relaxation themed content
            - File naming: morning_001.mp4, morning_002.mp4, etc.
            
            The system will automatically process the oldest video first.
            """,
            
            settings.LOCAL_FOLDERS['noon']: """
            📁 Noon Videos Folder
            =====================
            Place your Object Life midday/work videos here.
            
            Requirements:
            - MP4 format only
            - Recommended length: 5-15 minutes
            - Noon/productive/cooking themed content
            - File naming: noon_001.mp4, noon_002.mp4, etc.
            """,
            
            settings.LOCAL_FOLDERS['evening']: """
            📁 Evening Videos Folder
            ========================
            Place your Object Life evening/sleep videos here.
            
            Requirements:
            - MP4 format only
            - Recommended length: 8-20 minutes
            - Evening/sleep/relaxation themed content
            - File naming: evening_001.mp4, evening_002.mp4, etc.
            """,
            
            settings.ARCHIVE_DIR: """
            📁 Archive Folder
            =================
            Successfully uploaded videos are moved here automatically.
            
            File naming convention:
            {session}_{timestamp}_{original_name}
            
            Example:
            morning_20231201_093015_my_video.mp4
            """
        }
        
        for folder, content in readme_content.items():
            readme_path = os.path.join(folder, "README.txt")
            if not os.path.exists(readme_path):
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(content.strip())
    
    def get_video_from_folder(self, session_type):
        """جلب فيديو من المجلد المحلي مع معالجة متقدمة"""
        try:
            folder_path = settings.LOCAL_FOLDERS[session_type]
            
            # البحث عن ملفات فيديو مع دعم صيغ متعددة
            video_extensions = ['*.mp4', '*.mov', '*.avi', '*.mkv']
            video_files = []
            
            for ext in video_extensions:
                video_files.extend(glob.glob(os.path.join(folder_path, ext)))
            
            if not video_files:
                logger.warning(f"📭 No videos found in {folder_path}")
                return None
            
            # ترتيب الملفات حسب تاريخ التعديل (الأقدم أولاً)
            video_files.sort(key=os.path.getmtime)
            video_path = video_files[0]
            video_name = os.path.basename(video_path)
            
            # جمع معلومات الفيديو
            file_stats = os.stat(video_path)
            file_size_mb = file_stats.st_size / (1024 * 1024)
            
            # حساب hash للملف للتتبع
            file_hash = self._calculate_file_hash(video_path)
            
            # قراءة محتوى الفيديو
            with open(video_path, 'rb') as video_file:
                video_content = video_file.read()
            
            video_info = {
                'path': video_path,
                'name': video_name,
                'content': video_content,
                'size_bytes': len(video_content),
                'size_mb': round(file_size_mb, 2),
                'modified_time': datetime.fromtimestamp(file_stats.st_mtime),
                'file_hash': file_hash,
                'session_type': session_type
            }
            
            logger.info(f"📹 Found video: {video_name} ({video_info['size_mb']} MB)")
            logger.info(f"📊 Video details: Hash {file_hash[:8]}, Modified: {video_info['modified_time']}")
            
            return video_info
            
        except Exception as e:
            logger.error(f"💥 Error reading video file: {str(e)}")
            return None
    
    def _calculate_file_hash(self, file_path):
        """حساب hash للملف للتتبع"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return "unknown"
    
    def archive_video(self, video_info, session_type, youtube_id=None):
        """أرشفة الفيديو مع معلومات إضافية"""
        try:
            if not video_info:
                return False
            
            source_path = video_info['path']
            video_name = video_info['name']
            
            # إنشاء اسم جديد للارشفة مع معلومات كاملة
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(video_name)[0]
            extension = os.path.splitext(video_name)[1]
            
            if youtube_id:
                new_name = f"{session_type}_{timestamp}_{youtube_id}_{base_name}{extension}"
            else:
                new_name = f"{session_type}_{timestamp}_{base_name}{extension}"
            
            archive_path = os.path.join(settings.ARCHIVE_DIR, new_name)
            
            # نقل الفيديو للأرشيف
            shutil.move(source_path, archive_path)
            
            # إنشاء ملف وصف للأرشيف
            metadata_path = os.path.join(settings.ARCHIVE_DIR, f"{new_name}.meta")
            metadata_content = f"""Video Archive Metadata
========================
Original Name: {video_name}
Session Type: {session_type}
Archived: {datetime.now().isoformat()}
YouTube ID: {youtube_id or 'N/A'}
File Size: {video_info['size_mb']} MB
File Hash: {video_info.get('file_hash', 'N/A')}
Original Path: {video_info['path']}
"""
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write(metadata_content)
            
            logger.info(f"✅ Video archived: {video_name} -> {new_name}")
            if youtube_id:
                logger.info(f"📎 YouTube ID: {youtube_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Error archiving video: {str(e)}")
            return False
    
    def get_video_count(self, session_type):
        """الحصول على عدد الفيديوهات المتاحة"""
        folder_path = settings.LOCAL_FOLDERS[session_type]
        video_extensions = ['*.mp4', '*.mov', '*.avi', '*.mkv']
        count = 0
        
        for ext in video_extensions:
            count += len(glob.glob(os.path.join(folder_path, ext)))
        
        return count
    
    def list_available_videos(self, session_type):
        """عرض الفيديوهات المتاحة مع معلومات إضافية"""
        folder_path = settings.LOCAL_FOLDERS[session_type]
        video_extensions = ['*.mp4', '*.mov', '*.avi', '*.mkv']
        videos_info = []
        
        for ext in video_extensions:
            for video_path in glob.glob(os.path.join(folder_path, ext)):
                file_stats = os.stat(video_path)
                file_size_mb = file_stats.st_size / (1024 * 1024)
                modified_time = datetime.fromtimestamp(file_stats.st_mtime)
                
                videos_info.append({
                    'name': os.path.basename(video_path),
                    'size_mb': round(file_size_mb, 2),
                    'modified': modified_time.strftime("%Y-%m-%d %H:%M"),
                    'path': video_path
                })
        
        # ترتيب حسب التاريخ (الأقدم أولاً)
        videos_info.sort(key=lambda x: x['modified'])
        return videos_info
    
    def get_storage_stats(self):
        """إحصائيات التخزين"""
        stats = {}
        total_size = 0
        
        for session_type in ['morning', 'noon', 'evening']:
            folder_path = settings.LOCAL_FOLDERS[session_type]
            session_size = 0
            video_count = 0
            
            for video_path in glob.glob(os.path.join(folder_path, "*.*")):
                if video_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    session_size += os.path.getsize(video_path)
                    video_count += 1
            
            stats[session_type] = {
                'count': video_count,
                'size_mb': round(session_size / (1024 * 1024), 2)
            }
            total_size += session_size
        
        stats['total'] = {
            'count': sum(s['count'] for s in stats.values()),
            'size_mb': round(total_size / (1024 * 1024), 2)
        }
        
        return stats
