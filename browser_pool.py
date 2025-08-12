# browser_pool.py
import threading
import time
import os
from queue import Queue, Empty
from config import CONFIG

class PreWarmedBrowserPool:
    def __init__(self, pool_size: int = 10):
        self.pool_size = pool_size
        self.available_browsers: Queue = Queue()
        self.warming_in_progress = False
        self.warm_lock = threading.Lock()
        self.base_download_folder = None
        self.telegram_bot = None
        
    def set_config(self, download_folder: str, telegram_bot):
        """Set cấu hình cho browser pool"""
        self.base_download_folder = download_folder
        self.telegram_bot = telegram_bot
    
    def start_warming_browsers(self):
        """Bắt đầu pre-warm browsers sau khi download xong"""
        with self.warm_lock:
            if self.warming_in_progress:
                print("🔥 Browser warming already in progress...")
                return
            self.warming_in_progress = True
        
        def warm_browsers_async():
            try:
                print(f"\n🔥 === PRE-WARMING {self.pool_size} BROWSERS ===")
                print("⏳ Starting in 5 minutes, 2 minutes between each browser...")
                
                # Đợi 5 phút sau khi download xong
                time.sleep(300)  # 5 minutes
                
                for i in range(self.pool_size):
                    try:
                        print(f"🔥 Warming browser {i+1}/{self.pool_size}...")
                        
                        browser = self._create_prewarmed_browser(i)
                        if browser:
                            self.available_browsers.put(browser)
                            print(f"✅ Browser {i+1} warmed and ready")
                        else:
                            print(f"❌ Failed to warm browser {i+1}")
                        
                        # Đợi 2 phút giữa các browser để không lag VPS
                        if i < self.pool_size - 1:
                            print(f"⏳ Waiting 2 minutes before next browser...")
                            time.sleep(120)  # 2 minutes
                        
                    except Exception as e:
                        print(f"❌ Error warming browser {i+1}: {e}")
                
                print(f"🔥 Browser pool ready: {self.available_browsers.qsize()}/{self.pool_size} browsers")
                
            except Exception as e:
                print(f"❌ Browser warming error: {e}")
            finally:
                with self.warm_lock:
                    self.warming_in_progress = False
        
        # Chạy warming trong background thread
        warming_thread = threading.Thread(target=warm_browsers_async, daemon=True)
        warming_thread.start()
    
    def _create_prewarmed_browser(self, browser_id: int):
        """Tạo và pre-warm 1 browser"""
        try:
            from robust_pdf_downloader import RobustPDFDownloader
            
            downloader = RobustPDFDownloader(
                thread_id=browser_id + 100,  # Offset để tránh conflict
                base_download_folder=self.base_download_folder,
                telegram_bot=self.telegram_bot,
                fast_mode=True,
                prewarmed=True
            )
            
            # Pre-load download page để sẵn sàng
            print(f"🌐 Pre-loading download page for browser {browser_id+1}...")
            downloader.driver.get(CONFIG['urls']['downloader'])
            time.sleep(3)
            
            # Verify page loaded
            title = downloader.driver.title
            if len(title) > 0:
                print(f"✅ Browser {browser_id+1} pre-warmed successfully")
                return downloader
            else:
                print(f"❌ Browser {browser_id+1} failed to load page")
                downloader.close()
                return None
                
        except Exception as e:
            print(f"❌ Error creating browser {browser_id+1}: {e}")
            return None
    
    def get_prewarmed_browser(self):
        """Lấy 1 browser đã pre-warm"""
        try:
            browser = self.available_browsers.get_nowait()
            print(f"🔥 Using pre-warmed browser (pool: {self.available_browsers.qsize()} remaining)")
            return browser
        except Empty:
            print("⚠️ No pre-warmed browsers available, creating new one...")
            return None
    
    def return_browser(self, browser):
        """Trả browser về pool (nếu còn tốt)"""
        try:
            if browser and browser._is_driver_alive():
                self.available_browsers.put(browser)
                print(f"🔄 Browser returned to pool (pool: {self.available_browsers.qsize()})")
            else:
                print("🗑️ Browser discarded (not alive)")
                if browser:
                    browser.close()
        except Exception as e:
            print(f"⚠️ Error returning browser: {e}")
    
    def cleanup_pool(self):
        """Cleanup tất cả browsers trong pool"""
        print("🧹 Cleaning up browser pool...")
        cleaned = 0
        while not self.available_browsers.empty():
            try:
                browser = self.available_browsers.get_nowait()
                browser.close()
                cleaned += 1
            except:
                break
        print(f"🧹 Cleaned up {cleaned} browsers from pool")

# Global browser pool instance
browser_pool = PreWarmedBrowserPool(pool_size=10)
