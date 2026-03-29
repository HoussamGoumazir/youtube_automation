import logging
import os
from datetime import datetime
from config.settings import settings

class AdvancedLogger:
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name):
        if name not in cls._loggers:
            cls._loggers[name] = cls._create_logger(name)
        return cls._loggers[name]
    
    @classmethod
    def _create_logger(cls, name):
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # إنشاء مجلد السجلات
        os.makedirs(settings.LOGS_DIR, exist_ok=True)
        
        # Formatter متقدم
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File Handler مع rotation
        from logging.handlers import TimedRotatingFileHandler
        log_file = os.path.join(settings.LOGS_DIR, 'youtube_automation.log')
        file_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # إضافة handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.propagate = False
        
        return logger

def get_logger(name):
    return AdvancedLogger.get_logger(name)
