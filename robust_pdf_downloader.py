# robust_pdf_downloader.py - FIXED CLASS NAME

import os
import time
import threading
import uuid
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Lock, Thread

class CompetitiveStats:
    def __init__(self):
        self.lock = Lock()
        self.processed = 0
        self.success = 0
        self.failed = 0
        self.detection_stats = {'primary': 0, 'fallback1': 0, 'fallback2': 0, 'failed': 0}
    
    def add_result(self, success, code, detection_method='primary'):
        with self.lock:
            self.processed += 1
            if success:
                self.success += 1
                self.detection_stats[detection_method] += 1
            else:
                self.failed += 1
                self.detection_stats['failed'] += 1
    
    def get_stats(self):
        with self.lock:
            return {
                'processed': self.processed,
                'success': self.success,
                'failed': self.failed,
                'detection_stats': self.detection_stats
            }

stats = CompetitiveStats()

class BulletproofFileManager:
    """🛡️ BULLETPROOF file manager với Multiple Detection Strategies"""
    
    def __init__(self):
        self.lock = Lock()
        self.thread_downloads = {}
        self.used_filenames = set()
        self.global_download_tracking = {}
    
    def pre_allocate_unique_filename(self, thread_id, dn_code, download_folder):
        """⚡ Pre-allocation với global tracking"""
        with self.lock:
            timestamp = str(int(time.time() * 1000))[-8:]
            unique_id = str(uuid.uuid4())[:6]
            unique_filename = f"{dn_code}_{timestamp}_{unique_id}.pdf"
            
            self.used_filenames.add(unique_filename)
            
            self.thread_downloads[thread_id] = {
                'dn_code': dn_code,
                'unique_filename': unique_filename,
                'start_time': time.time(),
                'download_folder': download_folder
            }
            
            self.global_download_tracking[dn_code] = {
                'thread_id': thread_id,
                'unique_filename': unique_filename,
                'status': 'allocated',
                'folder': download_folder
            }
            
            return unique_filename
    
    def create_thread_folder(self, thread_id, base_folder):
        """⚡ Enhanced folder creation"""
        thread_folder = os.path.join(base_folder, f"t{thread_id}")
        try:
            os.makedirs(thread_folder, exist_ok=True)
            return thread_folder
        except Exception as e:
            print(f"❌ Folder creation error for thread {thread_id}: {e}")
            return base_folder
    
    def bulletproof_file_detection(self, thread_id, thread_folder, timeout=30):
        """🛡️ BULLETPROOF file detection với multiple strategies"""
        download_info = self.thread_downloads.get(thread_id, {})
        if not download_info:
            return None, 'no_info'
        
        expected_filename = download_info['unique_filename']
        dn_code = download_info['dn_code']
        
        print(f"🔍 BULLETPROOF detection for {dn_code} in thread {thread_id}")
        
        # Strategy 1: Primary Detection
        result = self._strategy_1_primary_detection(thread_id, thread_folder, expected_filename, timeout)
        if result:
            return result, 'primary'
        
        # Strategy 2: Pattern scan
        result = self._strategy_2_pattern_scan(thread_folder, dn_code, expected_filename)
        if result:
            return result, 'fallback1'
        
        # Strategy 3: Time-based scan
        result = self._strategy_3_time_based_scan(thread_folder, download_info['start_time'], expected_filename, dn_code)
        if result:
            return result, 'fallback2'
        
        print(f"❌ BULLETPROOF detection FAILED for {dn_code}")
        return None, 'failed'
    
    def _strategy_1_primary_detection(self, thread_id, thread_folder, expected_filename, timeout):
        """Strategy 1: Enhanced primary detection"""
        try:
            existing_files = set()
            try:
                existing_files = set(os.listdir(thread_folder))
            except:
                existing_files = set()
            
            end_time = time.time() + timeout
            check_count = 0
            
            while time.time() < end_time:
                check_count += 1
                try:
                    current_files = set(os.listdir(thread_folder))
                    new_files = current_files - existing_files
                    
                    pdf_files = [f for f in new_files if f.endswith('.pdf') and not f.endswith('.crdownload') and not f.endswith('.tmp')]
                    
                    if pdf_files:
                        source_file = pdf_files[0]
                        source_path = os.path.join(thread_folder, source_file)
                        target_path = os.path.join(thread_folder, expected_filename)
                        
                        if self._safe_rename_with_retry(source_path, target_path):
                            print(f"✅ Strategy 1 SUCCESS: {expected_filename} (check #{check_count})")
                            return target_path
                    
                    if expected_filename in current_files:
                        target_path = os.path.join(thread_folder, expected_filename)
                        if os.path.exists(target_path):
                            print(f"✅ Strategy 1 SUCCESS: {expected_filename} (already renamed)")
                            return target_path
                            
                except Exception as e:
                    print(f"⚠️ Strategy 1 error: {e}")
                
                time.sleep(0.2)
            
            print(f"⏱️ Strategy 1 timeout after {check_count} checks")
            return None
            
        except Exception as e:
            print(f"❌ Strategy 1 critical error: {e}")
            return None
    
    def _strategy_2_pattern_scan(self, thread_folder, dn_code, expected_filename):
        """Strategy 2: Scan by DN code pattern"""
        try:
            print(f"🔍 Strategy 2: Pattern scan for {dn_code}")
            
            pattern1 = os.path.join(thread_folder, f"*{dn_code}*.pdf")
            pattern2 = os.path.join(thread_folder, f"{dn_code}_*.pdf")
            pattern3 = os.path.join(thread_folder, "*.pdf")
            
            for pattern in [pattern1, pattern2, pattern3]:
                matches = glob.glob(pattern)
                pdf_files = [f for f in matches if not f.endswith('.crdownload') and not f.endswith('.tmp')]
                
                if pdf_files:
                    pdf_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                    
                    source_path = pdf_files[0]
                    target_path = os.path.join(thread_folder, expected_filename)
                    
                    if source_path != target_path:
                        if self._safe_rename_with_retry(source_path, target_path):
                            print(f"✅ Strategy 2 SUCCESS: {expected_filename}")
                            return target_path
                    else:
                        print(f"✅ Strategy 2 SUCCESS: {expected_filename} (already correct name)")
                        return target_path
            
            return None
            
        except Exception as e:
            print(f"❌ Strategy 2 error: {e}")
            return None
    
    def _strategy_3_time_based_scan(self, thread_folder, start_time, expected_filename, dn_code):
        """Strategy 3: Time-based scan"""
        try:
            print(f"🔍 Strategy 3: Time-based scan for {dn_code}")
            
            all_pdfs = glob.glob(os.path.join(thread_folder, "*.pdf"))
            recent_pdfs = []
            
            for pdf_path in all_pdfs:
                if pdf_path.endswith('.crdownload') or pdf_path.endswith('.tmp'):
                    continue
                
                try:
                    file_mtime = os.path.getmtime(pdf_path)
                    if file_mtime >= (start_time - 5):
                        recent_pdfs.append((pdf_path, file_mtime))
                except:
                    continue
            
            if recent_pdfs:
                recent_pdfs.sort(key=lambda x: x[1], reverse=True)
                
                source_path = recent_pdfs[0][0]
                target_path = os.path.join(thread_folder, expected_filename)
                
                if source_path != target_path:
                    if self._safe_rename_with_retry(source_path, target_path):
                        print(f"✅ Strategy 3 SUCCESS: {expected_filename}")
                        return target_path
                else:
                    print(f"✅ Strategy 3 SUCCESS: {expected_filename} (already correct name)")
                    return target_path
            
            return None
            
        except Exception as e:
            print(f"❌ Strategy 3 error: {e}")
            return None
    
    def _safe_rename_with_retry(self, source_path, target_path, max_retries=3):
        """Enhanced rename với retry mechanism"""
        for attempt in range(max_retries):
            try:
                if os.path.exists(source_path) and not os.path.exists(target_path):
                    os.rename(source_path, target_path)
                    return True
                elif os.path.exists(target_path):
                    return True
                else:
                    print(f"⚠️ Rename attempt {attempt + 1}: Source not found: {source_path}")
                    time.sleep(0.5)
            except Exception as e:
                print(f"⚠️ Rename attempt {attempt + 1} failed: {e}")
                time.sleep(0.5)
        
        print(f"❌ All rename attempts failed: {source_path} -> {target_path}")
        return False
    
    def cleanup_thread(self, thread_id):
        """Enhanced cleanup"""
        with self.lock:
            if thread_id in self.thread_downloads:
                download_info = self.thread_downloads[thread_id]
                filename = download_info.get('unique_filename', '')
                dn_code = download_info.get('dn_code', '')
                
                self.used_filenames.discard(filename)
                
                if dn_code in self.global_download_tracking:
                    self.global_download_tracking[dn_code]['status'] = 'cleaned'
                
                del self.thread_downloads[thread_id]

file_manager = BulletproofFileManager()

class FastTelegramSender:
    """📱 Enhanced ASYNC Telegram sender với retry"""
    
    def __init__(self, telegram_bot):
        self.telegram_bot = telegram_bot
        self.send_queue = []
        self.queue_lock = Lock()
        self.retry_count = {}
        self.max_retries = 2
    
    def send_async_with_retry(self, file_path, caption, dn_code):
        """🚀 Enhanced fire-and-forget Telegram send với retry"""
        def send_task():
            retry_count = 0
            max_retries = self.max_retries
            
            while retry_count <= max_retries:
                try:
                    if not os.path.exists(file_path):
                        print(f"📱 FAILED: File not found {os.path.basename(file_path)}")
                        return
                    
                    success = self.telegram_bot.send_document(file_path, caption)
                    if success:
                        print(f"📱 SENT: {os.path.basename(file_path)}")
                        return
                    else:
                        retry_count += 1
                        if retry_count <= max_retries:
                            print(f"📱 RETRY #{retry_count}: {os.path.basename(file_path)}")
                            time.sleep(1)
                        else:
                            print(f"📱 FAILED: {os.path.basename(file_path)} (max retries exceeded)")
                            
                except Exception as e:
                    retry_count += 1
                    if retry_count <= max_retries:
                        print(f"📱 RETRY #{retry_count} (error): {os.path.basename(file_path)} - {e}")
                        time.sleep(1)
                    else:
                        print(f"📱 ERROR: {os.path.basename(file_path)} - {e}")
        
        Thread(target=send_task, daemon=True).start()

class CompetitivePDFProcessor:  # ✅ FIXED: Tên class đúng
    """🔥 BULLETPROOF processor với enhanced file detection"""
    
    def __init__(self, browser_manager, telegram_bot):
        self.browser = browser_manager
        self.telegram_bot = telegram_bot
        self.fast_sender = FastTelegramSender(telegram_bot)
        self.recent_codes = []
        self.download_folder = browser_manager.download_folder
        self.browser_pool = {}  # ✅ NEW: Pool of isolated browsers per thread
        self.browser_pool_lock = Lock()
    
    def load_recent_codes(self, codes_list):
        """✅ Load recent codes"""
        self.recent_codes = codes_list[-100:]
        self.browser.load_recent_codes_cache(self.recent_codes)
        print(f"📋 Loaded {len(self.recent_codes)} recent codes into processor")
        if self.recent_codes:
            print(f"📋 Sample codes: {self.recent_codes[:3]}...")
    
    def download_all_buttons_with_smart_naming(self, max_concurrent=5):
        """🛡️ BULLETPROOF download với enhanced detection"""
        
        buttons = self.browser.find_all_download_buttons()
        
        if not buttons:
            print("⚠️ No download buttons found")
            return []
        
        print(f"🚀 BULLETPROOF processing {len(buttons)} downloads")
        downloaded = []
        failed_downloads = []
        detection_stats = {'primary': 0, 'fallback1': 0, 'fallback2': 0, 'failed': 0}
        
        def bulletproof_download_task(dn_code, button):
            thread_id = threading.current_thread().ident
            start_time = time.time()
            isolated_browser = None
            
            try:
                # 1. Enhanced folder creation
                thread_folder = file_manager.create_thread_folder(thread_id, self.download_folder)
                
                # 2. Enhanced filename allocation
                allocated_filename = file_manager.pre_allocate_unique_filename(thread_id, dn_code, thread_folder)
                
                # 3. 🔥 NEW: Get isolated browser for this thread
                isolated_browser = self._get_or_create_thread_browser(thread_id, thread_folder)
                
                # 4. Find download button in isolated browser
                isolated_button = self._find_button_for_dn_code(isolated_browser, dn_code)
                if not isolated_button:
                    print(f"⚠️ Button not found for {dn_code} in isolated browser")
                    return None
                
                # 5. CLICK download in isolated browser
                isolated_button.click()
                print(f"🔽 ISOLATED download initiated for {dn_code} in thread {thread_id}")
                
                # 6. BULLETPROOF file detection với multiple strategies
                file_path, detection_method = file_manager.bulletproof_file_detection(thread_id, thread_folder, timeout=30)
                
                if file_path and os.path.exists(file_path):
                    download_time = time.time() - start_time
                    
                    # 6. Enhanced async Telegram send với retry
                    caption = f"🛡️ BULLETPROOF DOWNLOAD\n📄 {dn_code}\n⏱️ {download_time:.1f}s\n🔍 Method: {detection_method}\n📁 {os.path.basename(file_path)}\n🧵 {thread_id}\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                    self.fast_sender.send_async_with_retry(file_path, caption, dn_code)
                    
                    # 7. Update stats
                    stats.add_result(True, dn_code, detection_method)
                    detection_stats[detection_method] += 1
                    
                    print(f"⚡ SUCCESS {dn_code} in {download_time:.1f}s ({detection_method})")
                    return dn_code
                else:
                    stats.add_result(False, dn_code, 'failed')
                    detection_stats['failed'] += 1
                    failed_downloads.append(dn_code)
                    print(f"❌ FAILED {dn_code} - No file detected after all strategies")
                    return None
                    
            except Exception as e:
                print(f"❌ ERROR {dn_code}: {e}")
                stats.add_result(False, dn_code, 'failed')
                detection_stats['failed'] += 1
                failed_downloads.append(dn_code)
                return None
            finally:
                # Cleanup thread data
                file_manager.cleanup_thread(thread_id)
                
                # 🔥 NEW: Cleanup isolated browser
                if isolated_browser and thread_id in self.browser_pool:
                    try:
                        isolated_browser.close()
                        with self.browser_pool_lock:
                            del self.browser_pool[thread_id]
                        print(f"✅ Cleaned up isolated browser for thread {thread_id}")
                    except Exception as e:
                        print(f"⚠️ Browser cleanup error for thread {thread_id}: {e}")
        
        # Execute with enhanced concurrency
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = [
                executor.submit(bulletproof_download_task, info['dn_code'], info['button'])
                for info in buttons
            ]
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    downloaded.append(result)
        
        # Enhanced reporting
        total_found = len(buttons)
        total_success = len(downloaded)
        total_failed = len(failed_downloads)
        
        print(f"\n🛡️ BULLETPROOF DOWNLOAD COMPLETE:")
        print(f"📊 Found: {total_found} | Success: {total_success} | Failed: {total_failed}")
        print(f"🔍 Detection Methods:")
        for method, count in detection_stats.items():
            if count > 0:
                print(f"   • {method}: {count}")
        
        if failed_downloads:
            print(f"❌ Failed codes: {failed_downloads}")
        
        # Update cache với new downloads
        if downloaded:
            self.recent_codes.extend(downloaded)
            self.recent_codes = self.recent_codes[-100:]
            self.browser.load_recent_codes_cache(self.recent_codes)
            print(f"📋 Updated cache with {len(downloaded)} new codes")
        
        # 🔥 NEW: Final cleanup of all isolated browsers
        self._cleanup_all_isolated_browsers()
        
        return downloaded
    
    def _find_button_for_dn_code(self, browser, dn_code):
        """🔍 Find download button for specific DN code in isolated browser"""
        try:
            from selenium.webdriver.common.by import By
            
            # Find table rows containing the DN code
            selectors = [
                f"//tr[contains(., '{dn_code}')]//input[contains(@id, 'LnkGetPDFActive')]",
                f"//tr[contains(., '{dn_code}')]//a[contains(@id, 'LnkGetPDFActive')]",
                f"//td[contains(text(), '{dn_code}')]/following-sibling::td//input[contains(@id, 'LnkGetPDFActive')]",
                f"//td[contains(text(), '{dn_code}')]/following-sibling::td//a[contains(@id, 'LnkGetPDFActive')]"
            ]
            
            for selector in selectors:
                try:
                    elements = browser.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            return element
                except Exception as e:
                    print(f"⚠️ Selector error: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ _find_button_for_dn_code error: {e}")
            return None
    
    def _cleanup_all_isolated_browsers(self):
        """🧹 Cleanup all isolated browsers at the end"""
        with self.browser_pool_lock:
            for thread_id, browser in list(self.browser_pool.items()):
                try:
                    browser.close()
                    print(f"✅ Final cleanup: Thread {thread_id} browser closed")
                except Exception as e:
                    print(f"⚠️ Final cleanup error for thread {thread_id}: {e}")
            
            self.browser_pool.clear()
            print(f"✅ All isolated browsers cleaned up")
    
    def _get_or_create_thread_browser(self, thread_id, thread_folder):
        """🔥 NEW: Get dedicated browser for thread với isolated download path"""
        with self.browser_pool_lock:
            if thread_id not in self.browser_pool:
                print(f"🚀 Creating isolated browser for thread {thread_id}")
                
                # Import here to avoid circular imports
                from browser_manager import BrowserManager
                
                # Create isolated browser instance
                isolated_browser = BrowserManager()
                
                # Override download folder to thread-specific folder
                isolated_browser.download_folder = thread_folder
                
                # Reinitialize driver with thread-specific download path
                isolated_browser._init_driver_with_custom_path(thread_folder)
                
                # Setup for current page state
                self._sync_browser_state(isolated_browser)
                
                self.browser_pool[thread_id] = isolated_browser
                print(f"✅ Thread {thread_id} browser isolated to: {thread_folder}")
            
            return self.browser_pool[thread_id]
    
    def _sync_browser_state(self, isolated_browser):
        """🔄 Sync isolated browser to current page state"""
        try:
            # Navigate to current URL
            isolated_browser.driver.get(self.browser.driver.current_url)
            
            # Copy cookies for session persistence
            for cookie in self.browser.driver.get_cookies():
                try:
                    isolated_browser.driver.add_cookie(cookie)
                except:
                    pass
            
            # Refresh to apply cookies
            isolated_browser.driver.refresh()
            time.sleep(2)
            
            print(f"✅ Browser state synchronized")
            
        except Exception as e:
            print(f"⚠️ Browser sync warning: {e}")
    
    def _fast_configure_download(self, thread_folder):
        """⚡ DEPRECATED: Use _get_or_create_thread_browser instead"""
        # This method is now deprecated in favor of isolated browsers
        pass
