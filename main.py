# main.py
import sys
import os
import urllib3

# Tắt SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import dependencies check
try:
    import selenium
    import requests
    import schedule
    from datetime import datetime
    import time
    print("✅ All dependencies available")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Installing required packages...")
    os.system("pip install selenium requests schedule")
    sys.exit(1)

from scheduler_system import SchedulerSystem
from config import CONFIG

def main():
    print("="*60)
    print("  🏢 ENTERPRISE SCHEDULER SYSTEM")
    print("  🔥 COMPETITIVE: 20 parallel downloads")
    print("  ⏰ Automated monitoring at minutes 8 & 38, Stop at 16 & 46")
    print("="*60)
    
    print(f"\n📋 Configuration:")
    print(f"   🌐 Target URL: {CONFIG['base_url']}")
    print(f"   ⏰ Khởi chạy: Phút {CONFIG['timing']['target_minutes']}")
    print(f"   🛑 Dừng lại: Phút {CONFIG['timing']['stop_minutes']}")
    print(f"   📊 Pre-check offset: {CONFIG['timing']['pre_check_offset']} minutes")
    print(f"   🔄 Page reload interval: {CONFIG['timing']['page_reload_interval']}s")
    print(f"   ⏱️ Search wait time: {CONFIG['timing']['search_wait_time']}s")
    print(f"   🤖 CAPTCHA service: {CONFIG['captcha']['service']}")
    print(f"   📱 Telegram: {'Enabled' if CONFIG['telegram']['enabled'] else 'Disabled'}")
    print(f"   🔥 Competitive downloads: {CONFIG['download']['max_concurrent_downloads']}")
    print(f"   🎯 Strategy: .NET buttons parallel download")
    
    # Kiểm tra Chrome WebDriver
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=opts)
        driver.quit()
        print("✅ Chrome WebDriver is available")
    except Exception as e:
        print(f"⚠️ Chrome WebDriver issue: {e}")
        print("   Please ensure ChromeDriver is installed and in PATH")
        if input("Continue anyway? (y/n): ").lower() != 'y':
            return
    
    # ✅ COMPETITIVE MODE option
    competitive_mode = input("🔥 Enable COMPETITIVE MODE (immediate 20 parallel downloads)? (y/n): ").lower() == 'y'
    
    if competitive_mode:
        print("🔥 COMPETITIVE MODE ENABLED")
        CONFIG['competitive'] = {
            'enabled': True,
            'max_concurrent_downloads': 20,
            'immediate_telegram': True
        }
    
    # ✅ IMPROVED: Test mode với prompt rõ ràng hơn
    print(f"\n🧪 TEST MODE CONFIGURATION:")
    print(f"   • YES: Bỏ qua lịch trình thời gian, chạy ngay lập tức")
    print(f"   • NO:  Tuân theo lịch trình (khởi chạy phút {CONFIG['timing']['target_minutes']}, dừng phút {CONFIG['timing']['stop_minutes']})")
    
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
    
    if input(f"\n🚀 Start Enterprise Scheduler System? (y/n): ").lower() == 'y':
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
