#!/usr/bin/env python3
# server_main.py - Simplified main for Ubuntu server

import os
import sys
from config import CONFIG

def main():
    """Server main - automatically configured for production"""
    print("🐧 Starting Enterprise Monitor on Ubuntu Server")
    print("="*60)
    
    # Set server mode automatically
    CONFIG['timing']['test_mode'] = False
    CONFIG['browser']['headless'] = True
    CONFIG['browser']['server_mode'] = True
    
    print(f"✅ Server Mode Configuration:")
    print(f"   • Headless: {CONFIG['browser']['headless']}")
    print(f"   • Test Mode: {CONFIG['timing']['test_mode']}")
    print(f"   • Schedule: Start at minutes {CONFIG['timing']['target_minutes']}")
    print(f"   • Schedule: Stop at minutes {CONFIG['timing']['stop_minutes']}")
    print(f"   • Max Threads: {CONFIG['thread_safe']['max_workers']}")
    print(f"   • Telegram: {'Enabled' if CONFIG['telegram']['enabled'] else 'Disabled'}")
    
    # Import and start scheduler
    try:
        from scheduler_system import SchedulerSystem
        
        scheduler = SchedulerSystem()
        print("\n🚀 Starting monitoring system...")
        scheduler.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
