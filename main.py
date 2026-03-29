#!/usr/bin/env python3
import sys
import os
import argparse
from datetime import datetime

# إضافة المسار للوحدات
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from core.archive_manager import AdvancedArchiveManager
from utils.logger import get_logger

logger = get_logger(__name__)

def display_banner():
    banner = """
    🎯 YouTube Automation System
    🚀 Object Life Shorts Uploader
    📅 Version 2.0 | Professional Edition
    """
    print(banner)

def main():
    display_banner()
    
    if len(sys.argv) < 2:
        print("❌ Usage: python main.py <command>")
        print("\n📋 Available commands:")
        print("  morning, noon, evening - Process upload session")
        print("  check                  - Check video availability")
        print("  health                 - System health check")
        print("  stats                  - System statistics")
        print("  setup                  - Setup file structure")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        manager = AdvancedArchiveManager()
        
        if command == "check":
            display_video_availability(manager)
            
        elif command == "health":
            display_health_status(manager)
            
        elif command == "stats":
            display_system_stats(manager)
            
        elif command == "setup":
            from core.file_manager import AdvancedFileManager
            AdvancedFileManager()
            print("✅ System setup completed successfully!")
            
        elif command in ['morning', 'noon', 'evening']:
            logger.info(f"🚀 Starting {command} session...")
            success = manager.process_session(command)
            
            if success:
                logger.info(f"✅ {command.capitalize()} session completed successfully!")
                sys.exit(0)
            else:
                logger.error(f"❌ {command.capitalize()} session failed!")
                sys.exit(1)
                
        else:
            print(f"❌ Unknown command: {command}")
            print("\n📋 Available commands:")
            print("  morning, noon, evening - Process upload session")
            print("  check                  - Check video availability")
            print("  health                 - System health check")
            print("  stats                  - System statistics")
            print("  setup                  - Setup file structure")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 System error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def display_video_availability(manager):
    """عرض توفر الفيديوهات"""
    try:
        availability = manager.check_video_availability()
        
        print("\n📊 VIDEO AVAILABILITY REPORT")
        print("=" * 60)
        
        for session_type in ['morning', 'noon', 'evening']:
            info = availability[session_type]
            print(f"\n{session_type.upper():<10} | Videos: {info['count']} | Size: {info['total_size_mb']} MB")
            print("-" * 40)
            
            for video in info['videos']:
                print(f"  📹 {video['name']}")
                print(f"     Size: {video['size_mb']} MB | Modified: {video['modified']}")
        
        # إحصائيات التخزين
        storage = availability['storage_stats']
        print(f"\n💾 TOTAL STORAGE: {storage['total']['count']} videos, {storage['total']['size_mb']} MB")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error checking video availability: {e}")

def display_health_status(manager):
    """عرض حالة صحة النظام"""
    try:
        health = manager.health_check()
        
        print("\n🔧 SYSTEM HEALTH CHECK")
        print("=" * 50)
        
        print(f"\n📁 Directories:")
        for name, status in health['directories'].items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {name}: {'OK' if status else 'MISSING'}")
        
        print(f"\n🔐 Authentication: {'✅ OK' if health['authentication'] else '❌ FAILED'}")
        print(f"🤖 AI Service: {'✅ OK' if health['ai_service'] else '❌ FAILED'}")
        print(f"\n📈 Overall Status: {'✅ HEALTHY' if health['overall'] else '❌ UNHEALTHY'}")
        print("=" * 50)
    except Exception as e:
        print(f"❌ Error checking system health: {e}")

def display_system_stats(manager):
    """عرض إحصائيات النظام"""
    try:
        stats = manager.get_system_stats()
        
        print("\n📈 SYSTEM STATISTICS")
        print("=" * 50)
        
        session_stats = stats['session_stats']
        print(f"\n🔄 Session Statistics:")
        print(f"  Total Processed: {session_stats['total_processed']}")
        print(f"  Successful: {session_stats['successful_uploads']}")
        print(f"  Failed: {session_stats['failed_uploads']}")
        if session_stats['total_processed'] > 0:
            success_rate = (session_stats['successful_uploads'] / session_stats['total_processed']) * 100
            print(f"  Success Rate: {success_rate:.1f}%")
        else:
            print(f"  Success Rate: 0%")
        
        storage_stats = stats['storage_stats']
        print(f"\n💾 Storage Statistics:")
        for session_type in ['morning', 'noon', 'evening']:
            print(f"  {session_type.title()}: {storage_stats[session_type]['count']} videos, {storage_stats[session_type]['size_mb']} MB")
        
        print("=" * 50)
    except Exception as e:
        print(f"❌ Error getting system stats: {e}")

if __name__ == "__main__":
    main()