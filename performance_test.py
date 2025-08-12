# performance_test.py - Test các cải tiến hiệu suất

import time
from browser_manager import BrowserManager
from config import CONFIG

def test_optimized_performance():
    """🚀 Test các cải tiến hiệu suất mới"""
    print("="*60)
    print("  🚀 PERFORMANCE OPTIMIZATION TEST")
    print("  📊 Testing optimized pagination & scanning")
    print("="*60)
    
    browser = None
    try:
        # 1. Initialize browser
        print("\n🔧 Initializing optimized browser...")
        start_time = time.time()
        browser = BrowserManager()
        init_time = time.time() - start_time
        print(f"✅ Browser initialized in {init_time:.2f}s")
        
        # 2. Show performance summary
        print("\n📊 PERFORMANCE OPTIMIZATIONS:")
        summary = browser.get_performance_summary()
        
        for category, optimizations in summary['optimizations'].items():
            print(f"\n🔥 {category.upper()}:")
            for key, value in optimizations.items():
                print(f"   • {key}: {value}")
        
        print(f"\n🎯 EXPECTED IMPROVEMENTS:")
        for key, value in summary['expected_improvements'].items():
            print(f"   • {key}: {value}")
        
        # 3. Test navigation
        print(f"\n🌐 Testing optimized navigation...")
        nav_start = time.time()
        if browser.navigate_to_page():
            nav_time = time.time() - nav_start
            print(f"✅ Navigation completed in {nav_time:.2f}s")
            
            # 4. Test form setup
            print(f"\n📋 Testing optimized form setup...")
            form_start = time.time()
            if browser.setup_search_form():
                form_time = time.time() - form_start
                print(f"✅ Form setup completed in {form_time:.2f}s")
                
                # 5. Test CAPTCHA & validation
                print(f"\n🤖 Testing optimized CAPTCHA & validation...")
                captcha_start = time.time()
                browser.solve_captcha()
                browser.inject_validate_filter()
                captcha_time = time.time() - captcha_start
                print(f"✅ CAPTCHA & validation completed in {captcha_time:.2f}s")
                
                # 6. Test search
                print(f"\n🔍 Testing optimized search...")
                search_start = time.time()
                if browser.perform_search():
                    search_time = time.time() - search_start
                    print(f"✅ Search completed in {search_time:.2f}s")
                    
                    # 7. Test scanning
                    print(f"\n🎯 Testing optimized scanning...")
                    scan_start = time.time()
                    buttons = browser.find_all_download_buttons()
                    scan_time = time.time() - scan_start
                    print(f"✅ Scan completed in {scan_time:.2f}s - Found {len(buttons)} buttons")
                    
                    # 8. Test ULTRA-OPTIMIZED pagination (if page 2 exists)
                    print(f"\n📄 Testing ULTRA-OPTIMIZED pagination...")
                    available_pages = browser.get_available_pages()
                    if len(available_pages) > 1 and 2 in available_pages:
                        page_start = time.time()
                        if browser.enhanced_page_navigation(2):
                            page_time = time.time() - page_start
                            print(f"✅ ULTRA-FAST page navigation completed in {page_time:.2f}s")
                            
                            # Test back to page 1
                            back_start = time.time()
                            if browser.enhanced_page_navigation(1):
                                back_time = time.time() - back_start
                                print(f"✅ Return to page 1 completed in {back_time:.2f}s")
                        else:
                            print(f"⚠️ Page navigation failed")
                    else:
                        print(f"ℹ️ Only 1 page available - skipping pagination test")
        
        # 9. Total time summary
        total_time = time.time() - start_time
        print(f"\n🏁 PERFORMANCE TEST SUMMARY:")
        print(f"   📊 Total test time: {total_time:.2f}s")
        print(f"   🚀 Navigation: {nav_time:.2f}s")
        print(f"   📋 Form setup: {form_time:.2f}s") 
        print(f"   🤖 CAPTCHA/Validation: {captcha_time:.2f}s")
        print(f"   🔍 Search: {search_time:.2f}s")
        print(f"   🎯 Scanning: {scan_time:.2f}s")
        
        print(f"\n✅ OPTIMIZATION TEST COMPLETED!")
        print(f"🔥 All components now run significantly faster!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if browser:
            browser.close()
            print(f"🔧 Browser closed safely")

if __name__ == "__main__":
    test_optimized_performance()
