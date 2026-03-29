import re
from utils.logger import get_logger

logger = get_logger(__name__)

class SEOAnalyzer:
    def __init__(self):
        self.power_words = [
            'amazing', 'ultimate', 'secret', 'proven', 'instant', 'easy',
            'powerful', 'essential', 'complete', 'advanced', 'master',
            'unbelievable', 'incredible', 'fantastic', 'perfect', 'best'
        ]
        
        self.negative_words = [
            'never', 'worst', 'avoid', 'bad', 'terrible', 'horrible'
        ]
    
    def analyze_title(self, title):
        """تحليل وتحسين العنوان"""
        analysis = {
            'length': len(title),
            'power_words': [],
            'has_numbers': bool(re.search(r'\d', title)),
            'has_parentheses': '(' in title and ')' in title,
            'score': 0
        }
        
        # البحث عن كلمات القوة
        for word in self.power_words:
            if word.lower() in title.lower():
                analysis['power_words'].append(word)
        
        # حساب النقاط
        analysis['score'] += min(analysis['length'] / 2, 25)  # الطول المثالي
        analysis['score'] += len(analysis['power_words']) * 10  # كلمات القوة
        analysis['score'] += 15 if analysis['has_numbers'] else 0  # وجود أرقام
        analysis['score'] += 10 if analysis['has_parentheses'] else 0  # أقواس
        
        return analysis
    
    def analyze_description(self, description):
        """تحليل الوصف"""
        lines = description.split('\n')
        analysis = {
            'length': len(description),
            'line_count': len(lines),
            'has_timestamps': any('0:00' in line or '00:' in line for line in lines),
            'has_hashtags': '#' in description,
            'has_links': 'http' in description,
            'score': 0
        }
        
        # حساب النقاط
        analysis['score'] += min(analysis['length'] / 100, 30)  # الطول
        analysis['score'] += 20 if analysis['has_timestamps'] else 0  # الطوابع الزمنية
        analysis['score'] += 15 if analysis['has_hashtags'] else 0  # الهاشتاقات
        analysis['score'] += 10 if analysis['has_links'] else 0  # الروابط
        
        return analysis
    
    def optimize_metadata(self, metadata, session_type):
        """تحسين البيانات الوصفية لتحسين SEO"""
        optimized = metadata.copy()
        
        # تحسين العنوان
        title_analysis = self.analyze_title(metadata.get('title', ''))
        if title_analysis['score'] < 60:
            logger.warning(f"📊 Title SEO score low: {title_analysis['score']}/100")
        
        # تحسين الوصف
        desc_analysis = self.analyze_description(metadata.get('description', ''))
        if desc_analysis['score'] < 50:
            logger.warning(f"📊 Description SEO score low: {desc_analysis['score']}/100")
        
        # إضافة تحليل SEO للبيانات
        optimized['seo_analysis'] = {
            'title': title_analysis,
            'description': desc_analysis,
            'overall_score': (title_analysis['score'] + desc_analysis['score']) / 2
        }
        
        logger.info(f"🎯 SEO Analysis - Title: {title_analysis['score']}/100, "
                   f"Description: {desc_analysis['score']}/100, "
                   f"Overall: {optimized['seo_analysis']['overall_score']:.1f}/100")
        
        return optimized
