# config.py - FULL CONFIG với Chat ID đúng và pagination support

import random
import string
from datetime import datetime

CONFIG = {
    'captcha': {
        'service': 'capsolver',
        'capsolver_key': 'CAP-ECD789C680F2D216DA142D379B56B7A5CF3C378C8BF6EEAE552655EADEA2AA7F',
        '2captcha_key': 'd3c3c36295fca3ad28741cc51667edaa'
    },
    'telegram': {
        'bot_token': '7983597834:AAH9XAB_wYtEp7c-2mmzPz5NgO7_SnxKgVA',
        'chat_id': '-1002773012711', # ✅ FIXED: Chat ID đúng từ link bạn cung cấp
        'enabled': True
    },
    'threads': {
        'scraper_threads': 2,
        'downloader_threads': 5  # ✅ CONSISTENT: Already 5 threads
    },
    'monitor': {
        'check_interval': 30,
        'max_pages': 40,
        'enabled': True
    },
    'retry': {
        'max_attempts': 3,
        'delay_between_retries': 3
    },
    'vps': {
        'page_load_timeout': 45,
        'script_timeout': 20,
        'implicit_wait': 8,
        'health_check_interval': 600,
        'fast_mode': True
    },
    'prewarming': {
        'enabled': True,
        'pool_size': 10,
        'warm_delay': 300,
        'browser_interval': 120
    },
    'urls': {
        'scraper': 'https://bocaodientu.dkkd.gov.vn/egazette/Forms/Egazette/DefaultAnnouncements.aspx',
        'downloader': 'https://bocaodientu.dkkd.gov.vn/egazette/Forms/Egazette/ANNOUNCEMENTSListingInsUpd.aspx'
    },
    'base_url': 'https://bocaodientu.dkkd.gov.vn/egazette/Forms/Egazette/ANNOUNCEMENTSListingInsUpd.aspx',
    'timing': {
        'target_minutes': [8, 38],  # ✅ UPDATED: Phút thứ 8 và 38 cho khởi chạy
        'stop_minutes': [16, 46],   # ✅ NEW: Phút thứ 16 và 46 cho dừng lại
        'pre_check_offset': 1,
        'page_reload_interval': 5,
        'search_wait_time': 30,
        'page_load_timeout': 60,
        'test_mode': False # ✅ FIXED: Mặc định False, sẽ được set từ main.py
    },
    'browser': {
        'headless': True,  # ✅ REQUIRED for Ubuntu server
        'page_load_timeout': 60,
        'implicit_wait': 10,
        'script_timeout': 30,
        'window_size': '1366,768',
        'server_mode': True,  # ✅ NEW: Enable server optimizations
        'disable_gpu': True,  # ✅ REQUIRED for headless
        'no_sandbox': True   # ✅ REQUIRED for running as root/service
    },
    'download': {
        'folder_pattern': 'enterprise_pdfs_%Y%m%d_%H%M%S',
        'max_concurrent_downloads': 5,  # ✅ CHANGED: 3 → 5
        'retry_attempts': 2,
        'wait_timeout': 25,
        'thread_safe_naming': True,
        'rename_lock_timeout': 5
    },
    'competitive': {
        'enabled': True,
        'max_concurrent_downloads': 5,  # ✅ CHANGED: 3 → 5
        'immediate_telegram': True,
        'thread_safe_mode': True
    },
    'thread_safe': {
        'max_workers': 5,  # ✅ CONSISTENT: Already 5 threads
        'file_detection_timeout': 15,  # ✅ REDUCED: 25s → 15s for faster detection
        'unique_naming_enabled': True,
        'rename_retry_attempts': 3,
        'snapshot_comparison': True,
        'verbose_logging': True,
        'detection_sleep_interval': 0.5,  # ✅ NEW: 0.5s sleep between checks
        'async_telegram_send': True  # ✅ NEW: Enable async telegram sending
    },
    'session': {
        'max_age_seconds': 300,
        'auto_reload_on_stale': True,
        'smart_pagination_enabled': True,
        'zero_data_max_cycles': 3,
        'avoid_reload_minutes': [8, 9, 10, 11, 38, 39, 40, 41]  # ✅ UPDATED: Điều chỉnh theo target_minutes mới
    },
    # ✅ ADDED: Pagination config
    'pagination': {
        'enabled': True,
        'cycle_pattern': [1, 2, 1],
        'wait_between_pages': 1,  # ✅ REDUCED: 2s → 1s cho chuyển trang nhanh hơn
        'max_empty_cycles_before_switch': 1,
        'fallback_to_reload_after_cycles': 3,
        'async_stats_enabled': True,  # ✅ NEW: Enable async stats reporting
        'immediate_navigation': True  # ✅ NEW: Chuyển trang ngay không chờ stats
    },
    'performance': {
        'enable_vps_resource_check': True,
        'memory_threshold_percent': 85,
        'cpu_threshold_percent': 85,
        'kill_zombie_chrome': True,
        'chrome_memory_limit_percent': 15
    },
    'debug': {
        'thread_safe_logging': True,
        'file_operation_logging': True,
        'telegram_debug_messages': False,
        'save_failed_downloads': True,
        'screenshot_on_error': False,
        'max_test_downloads': 10,
        'sequential_mode_fallback': True
    },
    'stealth': {
        'random_delays': True,
        'vary_user_agent': False,
        'disable_automation_flags': True,
        'random_window_size': False
    },
    # 🎯 NEW: Sequential mode configuration
    'use_sequential_mode': True,  # True = No race conditions, False = Competitive mode
    'sequential': {
        'max_concurrent_downloads': 5,  # ✅ INCREASED: 3 → 5 threads
        'download_timeout': 45,
        'file_stability_check': True,
        'exclusive_download_lock': True
    }
}

FAILED_CODES_FILE = "failed_codes.json"

def generate_random_h_param():
    """Tạo tham số h ngẫu nhiên (3 ký tự: số + chữ)"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=3))

def get_current_url():
    """Lấy URL với tham số h ngẫu nhiên"""
    h_param = generate_random_h_param()
    return f"{CONFIG['base_url']}?h={h_param}"

# ✅ ADDED: Missing helper functions

def get_pagination_config():
    """Get pagination configuration"""
    return CONFIG['pagination']

def get_thread_safe_config():
    """Get thread-safe specific configuration"""
    return CONFIG['thread_safe']

def get_download_config():
    """Get download configuration with thread-safe settings"""
    return CONFIG['download']

def is_thread_safe_mode():
    """Check if thread-safe mode is enabled"""
    return CONFIG['competitive'].get('thread_safe_mode', True)

def get_max_concurrent_downloads():
    """Get max concurrent downloads for thread-safe operations"""
    return CONFIG['thread_safe']['max_workers']

def validate_thread_safe_config():
    """Validate thread-safe configuration settings"""
    errors = []
    
    if CONFIG['thread_safe']['max_workers'] < 1:
        errors.append("max_workers must be >= 1")
    
    if CONFIG['thread_safe']['max_workers'] > 10:
        errors.append("max_workers should not exceed 10 for stability")
    
    if CONFIG['thread_safe']['file_detection_timeout'] < 10:
        errors.append("file_detection_timeout should be >= 10 seconds")
    
    if CONFIG['telegram']['enabled'] and not CONFIG['telegram']['bot_token']:
        errors.append("bot_token required when telegram is enabled")
    
    if errors:
        raise ValueError(f"Thread-safe configuration errors: {', '.join(errors)}")
    
    return True

# Auto-validate configuration on import
try:
    validate_thread_safe_config()
    print(f"✅ STEALTH Config validated; Telegram chat_id={CONFIG['telegram']['chat_id']}")
except ValueError as e:
    print(f"❌ Configuration validation failed: {e}")

# Export commonly used values
MAX_CONCURRENT_DOWNLOADS = CONFIG['thread_safe']['max_workers']
THREAD_SAFE_ENABLED = CONFIG['competitive']['thread_safe_mode']
FILE_DETECTION_TIMEOUT = CONFIG['thread_safe']['file_detection_timeout']
