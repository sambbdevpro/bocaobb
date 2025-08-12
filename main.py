#!/usr/bin/env python3

import sys
import os
import urllib3
import time

# Tắt SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import dependencies check
try:
    import selenium
    import requests
    import schedule
    from datetime import datetime
    print("✅ All dependencies available")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    sys.exit(1)

try:
    from config import CONFIG
    from scheduler_system import SchedulerSystem
    print("✅ Modules loaded successfully")
except Exception as e:
    print(f"❌ Module loading error: {e}")
    sys.exit(1)

def main():
    print("="*60)
    print("  🏢 ENTERPRISE SCHEDULER SYSTEM")
    print("  🔥 COMPETITIVE: 20 parallel downloads")
    print("  ⏰ Automated monitoring at minutes 8 & 38, Stop at 16 & 46")
    print("="*60)
    
    print(f"\n📋 Configuration:")
    print(f"    🌐 Target URL: {CONFIG['base_url']}")
    print(f"    ⏰ Khởi chạy: Phút {CONFIG['timing']['target_minutes']}")
    print(f"    🛑 Dừng lại: Phút {CONFIG['timing']['stop_minutes']}")
    print(f"    📊 Pre-check offset: {CONFIG['timing']['pre_check_offset']} minutes")
    print(f"    🔄 Page reload interval: {CONFIG['timing']['page_reload_interval']}s")
    print(f"    ⏱️ Search wait time: {CONFIG['timing']['search_wait_time']}s")
    print(f"    🤖 CAPTCHA service: {CONFIG['captcha']['service']}")
    print(f"    📱 Telegram: {'Enabled' if CONFIG['telegram']['enabled'] else 'Disabled'}")
    print(f"    🔥 Competitive downloads: {CONFIG['download']['max_concurrent_downloads']}")
    print(f"    🎯 Strategy: .NET buttons parallel download")

    # Kiểm tra Chrome WebDriver với timeout và error handling
        # Kiểm tra Chrome WebDriver với WebDriver Manager
    print("🔧 Testing Chrome WebDriver with WebDriver Manager...", flush=True)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.common.exceptions import WebDriverException, TimeoutException
        
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        
        # Auto-detect Chrome binary location
        chrome_paths = [
            "/usr/bin/google-chrome-stable",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/opt/google/chrome/chrome"
        ]
        
        chrome_binary = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_binary = path
                break
        
        if chrome_binary:
            opts.binary_location = chrome_binary
            print(f"✅ Found Chrome binary: {chrome_binary}")
        
        # Use WebDriver Manager for automatic version handling
        service = Service(ChromeDriverManager().install())
        
        print("   Creating WebDriver instance with auto-version matching...", flush=True)
        driver = webdriver.Chrome(service=service, options=opts)
        print("   WebDriver created successfully!", flush=True)
        driver.quit()
        print("✅ Chrome WebDriver is available with correct version")
        
    except Exception as e:
        print(f"⚠️ Chrome WebDriver issue: {e}")
        print("   WebDriver Manager will handle version compatibility")
        
        # Auto-continue for service mode, ask for interactive mode
        if not sys.stdin.isatty():  # Service mode
            print("🤖 Service mode: Continuing anyway...")
        else:  # Interactive mode
            continue_anyway = input("Continue anyway? (y/n): ").lower() == 'y'
            if not continue_anyway:
                return

        
        try:
            print("   Creating WebDriver instance...", flush=True)
            driver = webdriver.Chrome(options=opts)
            print("   WebDriver created, testing basic functionality...", flush=True)
            driver.quit()
            signal.alarm(0)  # Cancel timeout
            print("✅ Chrome WebDriver is available")
            
        except (TimeoutException, WebDriverException) as we:
            signal.alarm(0)  # Cancel timeout
            raise we
            
    except Exception as e:
        print(f"⚠️ Chrome WebDriver issue: {e}")
        print("   Please ensure ChromeDriver is installed and in PATH")
        
        # Auto-continue for service mode, ask for interactive mode
        if not sys.stdin.isatty():  # Service mode
            print("🤖 Service mode: Continuing anyway...")
        else:  # Interactive mode
            continue_anyway = input("Continue anyway? (y/n): ").lower() == 'y'
            if not continue_anyway:
                return

    # ✅ COMPETITIVE MODE - Auto answer for service mode
    if not sys.stdin.isatty():  # Service mode
        competitive_mode = True  # Mặc định 'y'
        print("🔥 COMPETITIVE MODE: Auto-enabled (service mode)")
    else:  # Interactive mode
        competitive_mode = input("🔥 Enable COMPETITIVE MODE (immediate 20 parallel downloads)? (y/n): ").lower() == 'y'
    
    if competitive_mode:
        print("🔥 COMPETITIVE MODE ENABLED")
        CONFIG['competitive'] = {
            'enabled': True,
            'max_concurrent_downloads': 20,
            'immediate_telegram': True
        }

    # ✅ TEST MODE - Auto answer for service mode
    print(f"\n🧪 TEST MODE CONFIGURATION:")
    print(f"   • YES: Bỏ qua lịch trình thời gian, chạy ngay lập tức")
    print(f"   • NO: Tuân theo lịch trình (khởi chạy phút {CONFIG['timing']['target_minutes']}, dừng phút {CONFIG['timing']['stop_minutes']})")
    
    if not sys.stdin.isatty():  # Service mode
        test_mode = False  # Mặc định 'n'
        print("⏰ TEST MODE: Auto-disabled (service mode) - Tuân theo lịch trình")
        CONFIG['timing']['test_mode'] = False
    else:  # Interactive mode
        while True:
            test_mode_input = input("🧪 Bật TEST MODE? (yes/no): ").lower().strip()
            if test_mode_input in ['yes', 'y']:
                test_mode = True
                print("⚡ TEST MODE ENABLED - Hệ thống sẽ chạy ngay lập tức")
                CONFIG['timing']['test_mode'] = True
                break
            elif test_mode_input in ['no', 'n']:
                test_mode = False
                print(f"⏰ SCHEDULE MODE - Tuân theo lịch trình: khởi chạy {CONFIG['timing']['target_minutes']}, dừng {CONFIG['timing']['stop_minutes']}")
                break
            else:
                print("❌ Vui lòng nhập 'yes' hoặc 'no'")

    # ✅ START SYSTEM - Auto answer for service mode
    if not sys.stdin.isatty():  # Service mode
        start_system = True  # Mặc định 'y'
        print("🚀 Enterprise Scheduler System: Auto-starting (service mode)")
    else:  # Interactive mode
        start_system = input(f"\n🚀 Start Enterprise Scheduler System? (y/n): ").lower() == 'y'
    
    if start_system:
        try:
            system = SchedulerSystem()
            if test_mode:
                # Test mode: chạy ngay lập tức
                system.start_monitoring()
            else:
                # Schedule mode: chờ đúng giờ theo lịch trình
                print(f"⏰ SCHEDULE MODE: Chờ đến phút {CONFIG['timing']['target_minutes']} để khởi chạy...")
                import schedule
                
                # Lập lịch khởi chạy tại phút 8 và 38
                schedule.every().hour.at(f":{CONFIG['timing']['target_minutes'][0]:02d}").do(lambda: system.start_monitoring())
                schedule.every().hour.at(f":{CONFIG['timing']['target_minutes'][1]:02d}").do(lambda: system.start_monitoring())
                
                print(f"📅 Lịch trình đã được thiết lập:")
                print(f"   🟢 Khởi chạy: Phút {CONFIG['timing']['target_minutes'][0]} và {CONFIG['timing']['target_minutes'][1]} mỗi giờ")
                print(f"   🔴 Dừng lại: Phút {CONFIG['timing']['stop_minutes'][0]} và {CONFIG['timing']['stop_minutes'][1]} mỗi giờ")
                print(f"⏳ Đang chờ thời điểm khởi chạy...")
                
                while True:
                    schedule.run_pending()
                    time.sleep(30)  # Kiểm tra mỗi 30 giây
                    
        except KeyboardInterrupt:
            print("\n⚠️ System interrupted by user")
        except Exception as e:
            print(f"\n💥 System error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Cancelled!")

if __name__ == "__main__":
    main()

