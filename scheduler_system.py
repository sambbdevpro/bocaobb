# scheduler_system.py - ENHANCED với Auto-Reload Navigation + 5 Threads

import time
import threading
import json
import os
from datetime import datetime

from time_manager import TimeManager
from browser_manager import BrowserManager
from robust_pdf_downloader import CompetitivePDFProcessor
from thread_safe_downloader import ParallelPDFProcessor  # 🎯 NEW: Sequential approach
from telegram_bot import TelegramBot
from config import CONFIG, get_max_concurrent_downloads, is_thread_safe_mode
from data_manager import DataManager
from stats import RobustStats

class SchedulerSystem:
    """
    ENHANCED Smart Scheduler với Auto-Reload Navigation:
    - Enhanced navigation với auto-reload sau 5 lần failed page 2
    - Automatic URL reload khi không có data đủ để tạo page 2
    - 5 threads download concurrent
    - Logic đúng: Scan page hiện tại → Download → Enhanced navigation
    """
    
    RECENT_CODES_FILE = "recent_codes.json"
    
    def __init__(self):
        self.time_manager = TimeManager()
        self.telegram_bot = TelegramBot()
        self.browser = None
        self.processor = None
        self.is_running = False
        self.known_codes = set()
        
        # ✅ NEW: Data management và stats tracking
        self.data_manager = DataManager()
        self.stats = RobustStats()
        self.session_start_time = datetime.now()
        self.total_downloads = 0
        self.successful_downloads = 0
        
        # Enhanced: Zero data detection
        self.zero_data_cycles = 0
        self.max_zero_cycles = CONFIG['session']['zero_data_max_cycles']
        self.total_cycles = 0
        
        # ✅ NEW: Enhanced Pagination tracking
        self.in_pagination_window = False
        self.pagination_start_time = None
        
        # Thread-safe settings - Auto-updated to 5 threads
        self.max_concurrent = get_max_concurrent_downloads()  # Returns 5
        self.thread_safe_enabled = is_thread_safe_mode()
        
        # Load existing data để có thống kê từ các session trước
        self.known_codes = self.data_manager.known_codes.copy()
        
        print(f"🚀 SchedulerSystem initialized with {self.max_concurrent} threads")
        print(f"📊 Loaded {len(self.known_codes)} existing codes from previous sessions")
    
    def _load_recent_codes(self):
        """Load top 100 recent DN codes from JSON."""
        if os.path.exists(self.RECENT_CODES_FILE):
            with open(self.RECENT_CODES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("recent_codes", [])[-100:]
        return []
    
    def _save_recent_codes(self, new_codes):
        """Save merged top 100 recent DN codes back to JSON."""
        existing = self._load_recent_codes()
        merged = existing + new_codes
        
        # Remove duplicates while preserving order
        seen = set()
        ordered = []
        for code in merged:
            if code not in seen:
                seen.add(code)
                ordered.append(code)
        
        recent = ordered[-100:]
        
        with open(self.RECENT_CODES_FILE, "w", encoding="utf-8") as f:
            json.dump({"recent_codes": recent}, f, ensure_ascii=False, indent=2)
    
    def _async_stats_report(self, current_page, downloaded, total_downloads, unique_codes, max_concurrent):
        """⚡ SPEED OPTIMIZATION: Async stats calculation and telegram reporting"""
        try:
            # Get navigation stats for reporting (có thể tốn thời gian)
            nav_stats = self.browser.get_navigation_stats() if self.browser else {}
            
            # Enhanced message với stats (có thể tốn thời gian tính toán)
            runtime = datetime.now() - self.session_start_time
            runtime_str = str(runtime).split('.')[0]  # Remove microseconds
            
            msg = (
                f"✅ Page {current_page} downloaded: {len(downloaded)} files\n"
                f"📊 Session stats: {total_downloads} total, {unique_codes} unique\n"
                f"🧵 Using {max_concurrent} threads\n"
                f"🔄 Page 2 failures: {nav_stats.get('page2_failed_count', 0)}/{nav_stats.get('max_page2_failures', 5)}\n"
                f"⏱️ Runtime: {runtime_str}\n"
                f"⏰ {datetime.now().strftime('%H:%M:%S')}"
            )
            
            # Send telegram message (có thể tốn thời gian network)
            self.telegram_bot.send_message(msg)
            print(f"📊 Async stats report sent for page {current_page}")
            
        except Exception as e:
            print(f"⚠️ Async stats report error: {e}")
            # Không raise exception để không ảnh hưởng main flow
    
    def _async_test_mode_report(self, downloaded, total_downloads, unique_codes, max_concurrent, refresh_reason, total_cycles):
        """⚡ SPEED OPTIMIZATION: Async test mode stats reporting"""
        try:
            # Get navigation stats for reporting (có thể tốn thời gian)
            nav_stats = self.browser.get_navigation_stats() if self.browser else {}
            
            # Enhanced message với stats (có thể tốn thời gian tính toán)
            runtime = datetime.now() - self.session_start_time
            runtime_str = str(runtime).split('.')[0]
            
            success_message = (
                f"✅ ENHANCED TEST MODE SUCCESS\n"
                f"📥 Downloaded: {len(downloaded)} files\n"
                f"📊 Session total: {total_downloads} downloads, {unique_codes} unique codes\n"
                f"🔄 Strategy: {refresh_reason or 'NO_REFRESH'}\n"
                f"🧵 Thread-safe mode: ON\n"
                f"🔢 Concurrent workers: {max_concurrent}\n"
                f"🔄 Page 2 failures: {nav_stats.get('page2_failed_count', 0)}\n"
                f"📊 Cycle: #{total_cycles}\n"
                f"⏱️ Runtime: {runtime_str}\n"
                f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
                f"📋 Files: {', '.join(downloaded[:5])}{'...' if len(downloaded) > 5 else ''}"
            )
            
            # Send telegram message (có thể tốn thời gian network)
            self.telegram_bot.send_message(success_message)
            print(f"📊 Async test mode report sent for {len(downloaded)} files")
            
        except Exception as e:
            print(f"⚠️ Async test mode report error: {e}")
            # Không raise exception để không ảnh hưởng main flow
    
    def _enhanced_pagination_loop(self):
        """✅ ENHANCED: Logic với Auto-Reload Navigation"""
        current_page = 1  # Bắt đầu từ page 1 (mặc định sau search)
        
        while self.is_running:
            # ✅ NEW: Kiểm tra thời điểm dừng hệ thống
            if self.time_manager.is_stop_time():
                stop_message = f"🛑 Hệ thống tự động dừng tại phút {datetime.now().minute} (theo lịch trình: {CONFIG['timing']['stop_minutes']})"
                print(stop_message)
                self.telegram_bot.send_message(stop_message)
                self.stop_monitoring()
                break
            
            print(f"📄 Processing page {current_page}")
            
            # 1. ✅ SCAN VÀ DOWNLOAD PAGE HIỆN TẠI TRƯỚC
            # Check processor type and call appropriate method
            if hasattr(self.processor, 'download_all_buttons_sequential'):
                downloaded = self.processor.download_all_buttons_parallel(
                    max_concurrent=min(self.max_concurrent, 5)  # ✅ INCREASED: Limit to 5 threads
                )
            else:
                downloaded = self.processor.download_all_buttons_with_smart_naming(
                    max_concurrent=self.max_concurrent  # Uses 5 threads
                )
            
            # 2. ✅ XỬ LÝ KẾT QUẢ DOWNLOAD VÀ TRACKING STATS  
            if downloaded:
                # ✅ CRITICAL: Update essential data immediately
                self.total_downloads += len(downloaded)
                self.successful_downloads += len(downloaded)
                self.known_codes.update(downloaded)
                
                # Update stats tracking (nhanh)
                for code in downloaded:
                    self.stats.add_result(True, code)
                
                # 🔥 CRITICAL: Save to JSON AND update browser cache (nhanh)!
                self._save_recent_codes(downloaded)
                self.data_manager.add_codes(downloaded)  # Save to persistent storage
                
                # 🔥 CRITICAL: Reload updated codes into processor cache (nhanh)
                updated_recent_codes = self._load_recent_codes()
                self.processor.load_recent_codes(updated_recent_codes)
                print(f"🔄 Updated cache with {len(downloaded)} new codes. Total cache: {len(updated_recent_codes)}")
                
                # ⚡ SPEED OPTIMIZATION: Start async stats reporting while continuing
                stats_thread = threading.Thread(
                    target=self._async_stats_report, 
                    args=(current_page, downloaded, self.total_downloads, len(self.known_codes), self.max_concurrent),
                    daemon=True
                )
                stats_thread.start()
                
                print(f"✅ Page {current_page}: Downloaded {len(downloaded)} files with {self.max_concurrent} threads")
            else:
                print(f"⚠️ Page {current_page}: No new files found")
            
            # 3. ✅ SAU KHI DOWNLOAD XONG → ENHANCED NAVIGATION
            target_page = 2 if current_page == 1 else 1
            
            # Use enhanced navigation with auto-reload
            if self.browser.enhanced_page_navigation(target_page):
                current_page = target_page
                print(f"✅ Enhanced navigation to page {current_page} successful")
            else:
                print(f"❌ Enhanced navigation to page {target_page} failed")
                
                # Get updated navigation stats after failure
                nav_stats = self.browser.get_navigation_stats()
                if nav_stats['page2_failed_count'] == 0:  # If counter was reset, reload happened
                    print("🔄 Auto-reload was triggered and completed")
            
            # 4. ⚡ SPEED OPTIMIZATION: Delay ngắn hơn cho pagination nhanh hơn
            page_delay = CONFIG['pagination'].get('wait_between_pages', 1)
            time.sleep(page_delay)  # Reduced from 2s to configurable (default 1s)
    
    def start_monitoring(self):
        """✅ ENHANCED: Start monitoring với Enhanced Navigation"""
        test_mode = CONFIG['timing'].get('test_mode', False)
        
        startup_message = (
            f"🚀 ENHANCED PAGINATION Scheduler Started (5 THREADS + AUTO-RELOAD)\n"
            f"⚡ Logic: Scan → Download → Enhanced Navigation\n"
            f"🔄 Auto-reload after 5 page 2 failures\n"
            f"🛡️ Protection against new-day data shortage\n"
            f"📊 INITIAL STATS:\n"
            f"   • Existing codes loaded: {len(self.known_codes)}\n"
            f"   • Session start: {self.session_start_time.strftime('%H:%M:%S')}\n"
            f"   • Downloads this session: 0\n"
            f"🧵 TECHNICAL CONFIG:\n"
            f"   • Thread-safe downloads: {'ON' if self.thread_safe_enabled else 'OFF'}\n"
            f"   • Max concurrent: {self.max_concurrent} (ENHANCED)\n"
            f"   • Recent codes cache: 100\n"
            f"📱 Telegram: {'ON' if CONFIG['telegram']['enabled'] else 'OFF'}"
        )
        
        self.telegram_bot.send_message(startup_message)
        self.is_running = True
        
        try:
            # Initialize browser and processor
            self.browser = BrowserManager()
            
            # 🎯 NEW: Choose processor based on mode
            use_sequential = CONFIG.get('use_sequential_mode', True)  # Default to sequential for safety
            
            if use_sequential:
                self.processor = ParallelPDFProcessor(self.browser, self.telegram_bot)
                print("🚀 Using PARALLEL processor (TRUE 5 THREADS with isolated folders)")
            else:
                self.processor = CompetitivePDFProcessor(self.browser, self.telegram_bot)
                print("🔥 Using COMPETITIVE processor (race condition risk)")
            
            # Load recent codes for duplicate check
            recent = self._load_recent_codes()
            self.processor.load_recent_codes(recent)
            
            # Perform initial setup
            if not self.browser.navigate_to_page():
                return
            if not self.browser.setup_search_form():
                return
            if not self.browser.solve_captcha():
                return
            if not self.browser.inject_validate_filter():
                return
            if not self.browser.perform_search():
                return
            
            # Start enhanced pagination loop (bắt đầu từ page 1)
            self._enhanced_pagination_loop()
            
        except KeyboardInterrupt:
            self.stop_monitoring()
        except Exception as e:
            error_msg = f"💥 System Error: {e}"
            print(error_msg)
            self.telegram_bot.send_message(error_msg)
    
    def stop_monitoring(self):
        """✅ ENHANCED: Stop monitoring với full stats và navigation stats"""
        self.is_running = False
        
        # Calculate session duration
        session_duration = datetime.now() - self.session_start_time
        duration_str = str(session_duration).split('.')[0]  # Remove microseconds
        
        # Get final navigation stats
        nav_stats = {}
        if self.browser:
            nav_stats = self.browser.get_navigation_stats()
            self.browser.close()
        
        # Get stats from stats tracker
        stats_data = self.stats.get_stats()
        
        # Enhanced stop message với full reporting
        stop_message = (
            f"🛑 ENHANCED PAGINATION Scheduler Stopped\n"
            f"📊 SESSION SUMMARY:\n"
            f"   • Total processed codes: {len(self.known_codes)}\n"
            f"   • Downloads this session: {self.total_downloads}\n"
            f"   • Successful downloads: {self.successful_downloads}\n"
            f"   • Success rate: {stats_data['success']}/{stats_data['processed']} ({(stats_data['success']/max(1,stats_data['processed'])*100):.1f}%)\n"
            f"   • Session duration: {duration_str}\n"
            f"🔄 OPERATION STATS:\n"
            f"   • Total cycles: {self.total_cycles}\n"
            f"   • Final zero streak: {self.zero_data_cycles}\n"
            f"   • Page 2 failures: {nav_stats.get('page2_failed_count', 0)}\n"
            f"🧵 TECHNICAL CONFIG:\n"
            f"   • Thread-safe mode: {'ON' if self.thread_safe_enabled else 'OFF'}\n"
            f"   • Max concurrent used: {self.max_concurrent}\n"
            f"   • Auto-reload protection: {'ACTIVE' if nav_stats.get('auto_reload_enabled', False) else 'OFF'}\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        self.telegram_bot.send_message(stop_message)
        print("🛑 Enhanced Scheduler stopped gracefully")
        print(f"📊 Final stats: {stats_data}")
        
        # Save final data
        self.data_manager.save_data()
    
    def get_status(self):
        """✅ ENHANCED: Get status với full stats và navigation stats"""
        next_time = self.time_manager.get_next_check_time().strftime('%H:%M:%S')
        
        nav_stats = {}
        if self.browser:
            nav_stats = self.browser.get_navigation_stats()
        
        # Calculate session duration
        session_duration = datetime.now() - self.session_start_time
        duration_str = str(session_duration).split('.')[0]
        
        # Get stats data
        stats_data = self.stats.get_stats()
        
        return {
            'is_running': self.is_running,
            'session_stats': {
                'duration': duration_str,
                'total_downloads': self.total_downloads,
                'successful_downloads': self.successful_downloads,
                'known_codes_count': len(self.known_codes),
                'stats_tracker': stats_data
            },
            'browser_session_age': time.time() - (self.browser.last_reload_time if self.browser else 0),
            'zero_data_cycles': self.zero_data_cycles,
            'total_cycles': self.total_cycles,
            'next_check_time': next_time,
            'thread_safe_enabled': self.thread_safe_enabled,
            'max_concurrent_downloads': self.max_concurrent,  # Now shows 5
            'in_pagination_window': self.in_pagination_window,
            'enhanced_navigation': nav_stats,
            'thread_safe_config': CONFIG['thread_safe']
        }

    def force_run_cycle(self):
        """✅ PRESERVED: Original force run cycle"""
        print("🔧 Force running monitoring cycle...")
        self._run_monitoring_cycle()

    def get_download_stats(self):
        """✅ ENHANCED: Download stats với full session và navigation info"""
        nav_stats = {}
        if self.browser:
            nav_stats = self.browser.get_navigation_stats()
        
        # Calculate session duration
        session_duration = datetime.now() - self.session_start_time
        duration_str = str(session_duration).split('.')[0]
        
        # Get stats data
        stats_data = self.stats.get_stats()
            
        return {
            'session_info': {
                'duration': duration_str,
                'start_time': self.session_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'downloads_this_session': self.total_downloads,
                'successful_downloads': self.successful_downloads
            },
            'data_summary': {
                'total_known_codes': len(self.known_codes),
                'recent_codes_count': len(self._load_recent_codes()),
                'stats_tracker': stats_data
            },
            'operation_stats': {
                'zero_data_cycles': self.zero_data_cycles,
                'total_cycles': self.total_cycles,
                'in_pagination_window': self.in_pagination_window
            },
            'technical_config': {
                'thread_safe_mode': self.thread_safe_enabled,
                'max_concurrent': self.max_concurrent,  # Now shows 5
                'enhanced_navigation': nav_stats
            }
        }
    
    def _run_monitoring_cycle(self):
        """✅ TEST MODE: Enhanced monitoring cycle"""
        try:
            self.total_cycles += 1
            print(f"🔄 Starting ENHANCED TEST MODE cycle #{self.total_cycles}...")
            current_minute = datetime.now().minute

            # Initialize browser and processor if needed
            if not self.browser:
                self.browser = BrowserManager()
                
                # 🎯 NEW: Choose processor based on mode
                use_sequential = CONFIG.get('use_sequential_mode', True)
                
                if use_sequential:
                    self.processor = ParallelPDFProcessor(self.browser, self.telegram_bot)
                    print("✅ SEQUENTIAL Browser and processor initialized")
                else:
                    self.processor = CompetitivePDFProcessor(self.browser, self.telegram_bot)
                    print("✅ COMPETITIVE Browser and processor initialized")

            # Load recent codes into processor for duplicate check
            recent = self._load_recent_codes()
            self.processor.load_recent_codes(recent)
            print(f"📋 Loaded {len(recent)} recent codes for duplicate check")

            # Full initial setup only on first time or after cleanup
            if not hasattr(self, '_initial_setup_done') or not self._initial_setup_done:
                if not self._initial_setup():
                    self._cleanup_and_retry()
                    return
                self._initial_setup_done = True

            # Enhanced SESSION MANAGEMENT with Zero Data Fallback
            refresh_reason = self._determine_refresh_strategy(current_minute)
            if refresh_reason:
                print(f"🔄 REFRESH TRIGGERED: {refresh_reason}")
                
                if refresh_reason == "ZERO_DATA_FALLBACK":
                    print("🎯 Executing zero data fallback refresh...")
                    if not self.browser.reload_current_url():
                        print("❌ Zero data fallback reload failed")
                        self._cleanup_and_retry()
                        return
                elif refresh_reason == "SESSION_STALE":
                    print("🕒 Executing session stale refresh...")
                    if not self.browser.reload_current_url():
                        print("❌ URL reload failed")
                        self._cleanup_and_retry()
                        return

            # *** ENHANCED THREAD-SAFE DOWNLOAD EXECUTION ***
            # Check processor type and call appropriate method
            if hasattr(self.processor, 'download_all_buttons_sequential'):
                print(f"🎯 Starting SEQUENTIAL downloads with {min(self.max_concurrent, 3)} workers...")
                downloaded = self.processor.download_all_buttons_parallel(
                    max_concurrent=min(self.max_concurrent, 5)  # ✅ INCREASED: Limit to 5 threads
                )
            else:
                print(f"🔽 Starting COMPETITIVE downloads with {self.max_concurrent} workers...")
                downloaded = self.processor.download_all_buttons_with_smart_naming(
                    max_concurrent=self.max_concurrent  # Uses 5 threads
                )

            # Enhanced: Update zero data counter and send notifications
            if downloaded:
                self.zero_data_cycles = 0  # Reset counter on success
                
                # ✅ UPDATE STATS - duplicate logic from pagination loop
                self.total_downloads += len(downloaded)
                self.successful_downloads += len(downloaded)
                self.known_codes.update(downloaded)
                
                # Update stats tracking
                for code in downloaded:
                    self.stats.add_result(True, code)
                
                # 🔥 CRITICAL: Save to JSON AND update browser cache!
                self._save_recent_codes(downloaded)
                self.data_manager.add_codes(downloaded)  # Save to persistent storage
                
                # 🔥 CRITICAL: Reload updated codes into processor cache
                updated_recent_codes = self._load_recent_codes()
                self.processor.load_recent_codes(updated_recent_codes)
                print(f"✅ Successfully downloaded {len(downloaded)} files")
                print(f"🔄 Updated cache with {len(downloaded)} new codes. Total cache: {len(updated_recent_codes)}")

                # ⚡ SPEED OPTIMIZATION: Async reporting cho test mode cũng 
                test_stats_thread = threading.Thread(
                    target=self._async_test_mode_report, 
                    args=(downloaded, self.total_downloads, len(self.known_codes), self.max_concurrent, refresh_reason, self.total_cycles),
                    daemon=True
                )
                test_stats_thread.start()
            else:
                self.zero_data_cycles += 1  # Increment on zero data
                print(f"⚠️ No new files - Zero data streak: {self.zero_data_cycles}/{self.max_zero_cycles}")

        except Exception as e:
            error_msg = f"❌ Enhanced cycle error: {e}"
            print(error_msg)
            self.telegram_bot.send_message(f"❌ Enhanced Cycle Error: {e}")
            self._cleanup_and_retry()

    def _determine_refresh_strategy(self, current_minute):
        """✅ PRESERVED: Original refresh strategy logic"""
        # Priority 1: Zero data fallback (highest priority)
        if self.zero_data_cycles >= self.max_zero_cycles:
            return "ZERO_DATA_FALLBACK"

        # Priority 2: Session stale check
        if self.browser and self.browser.should_reload():
            return "SESSION_STALE"

        # Priority 3: Target minutes pagination (avoid during download windows)
        avoid_minutes = CONFIG['session'].get('avoid_reload_minutes', [])
        if current_minute in CONFIG['timing']['target_minutes'] and current_minute not in avoid_minutes:
            return "SMART_PAGINATION"

        # No refresh needed
        return None

    def _initial_setup(self):
        """✅ PRESERVED: Original initial setup"""
        try:
            print("⚙️ Performing enhanced initial setup...")
            if not self.browser.navigate_to_page():
                print("❌ Navigate to page failed")
                return False
            if not self.browser.setup_search_form():
                print("❌ Setup search form failed")
                return False
            if not self.browser.solve_captcha():
                print("❌ Solve CAPTCHA failed")
                return False
            if not self.browser.inject_validate_filter():
                print("❌ Inject validate filter failed")
                return False
            time.sleep(0.5)  # minimal delay
            if not self.browser.perform_search():
                print("❌ Perform search failed")
                return False

            print("✅ Enhanced initial setup completed successfully")
            return True

        except Exception as e:
            error_msg = f"❌ Enhanced initial setup error: {e}"
            print(error_msg)
            self.telegram_bot.send_message(f"❌ Enhanced Setup Error: {e}")
            return False

    def _cleanup_and_retry(self):
        """✅ PRESERVED: Original cleanup and retry"""
        try:
            print("🔄 Enhanced cleaning up for retry...")
            if self.browser:
                self.browser.close()
            self.browser = None
            self.processor = None
            self._initial_setup_done = False

            # Reset zero data counter on cleanup
            self.zero_data_cycles = 0
            print("✅ Enhanced cleanup completed")

        except Exception as e:
            print(f"⚠️ Enhanced cleanup error: {e}")
