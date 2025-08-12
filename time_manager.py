# time_manager.py - COMPLETE với FIXED non-blocking wait

from datetime import datetime, timedelta
import time
from config import CONFIG

class TimeManager:
    """
    Enhanced Time Manager với:
    - Smart scheduling cho phút 9/39
    - Test mode bypass
    - Next check time calculation
    - FIXED: Non-blocking wait method
    - Optimal timing for enterprise monitoring
    """

    def __init__(self):
        self.target_minutes = CONFIG['timing']['target_minutes']
        self.stop_minutes = CONFIG['timing'].get('stop_minutes', [])  # ✅ NEW: Phút dừng lại
        self.pre_check_offset = CONFIG['timing']['pre_check_offset']

    def get_next_check_time(self):
        """Tính toán thời điểm check tiếp theo"""
        now = datetime.now()
        current_minute = now.minute
        
        # Tìm target minute tiếp theo
        next_target = None
        for target_min in self.target_minutes:
            check_time = now.replace(minute=target_min-self.pre_check_offset, second=0, microsecond=0)
            if check_time > now:
                next_target = check_time
                break
        
        # Nếu không có target trong giờ hiện tại, lấy target đầu tiên của giờ sau
        if not next_target:
            next_hour = now + timedelta(hours=1)
            next_target = next_hour.replace(
                minute=self.target_minutes[0]-self.pre_check_offset,
                second=0,
                microsecond=0
            )
        
        return next_target

    def is_check_time(self):
        """Kiểm tra có phải thời điểm cần check không"""
        # TEST MODE: Bypass timing
        if CONFIG['timing'].get('test_mode', False):
            print("⚡ TEST MODE: Always return True for check time")
            return True
        
        now = datetime.now()
        current_minute = now.minute
        
        # Kiểm tra có trong khoảng thời gian check không (target_minute - offset đến target_minute + 3)
        for target_min in self.target_minutes:
            start_check = (target_min - self.pre_check_offset) % 60
            end_check = (target_min + 3) % 60
            
            if start_check <= end_check:
                if start_check <= current_minute <= end_check:
                    return True
            else:  # Trường hợp qua giờ (ví dụ: 58-2)
                if current_minute >= start_check or current_minute <= end_check:
                    return True
        
        return False

    def get_time_until_next_check(self):
        """Tính thời gian còn lại đến lần check tiếp theo"""
        if CONFIG['timing'].get('test_mode', False):
            return 0
        
        next_check = self.get_next_check_time()
        now = datetime.now()
        return (next_check - now).total_seconds()

    def wait_until_next_check(self):
        """✅ FIXED: Non-blocking method - chỉ trả về thời gian chờ"""
        wait_seconds = self.get_time_until_next_check()
        if wait_seconds > 0:
            next_check = self.get_next_check_time()
            print(f"⏰ Next check: {next_check.strftime('%H:%M:%S')} ({wait_seconds:.0f}s)")
        return wait_seconds

    def is_stop_time(self):
        """✅ NEW: Kiểm tra có phải thời điểm cần dừng hệ thống không"""
        if CONFIG['timing'].get('test_mode', False):
            return False  # Test mode không bao giờ dừng
        
        now = datetime.now()
        current_minute = now.minute
        
        for stop_min in self.stop_minutes:
            # Kiểm tra trong khoảng 2 phút sau thời điểm dừng
            if stop_min <= current_minute <= (stop_min + 2) % 60:
                return True
        
        return False

    def is_avoid_reload_window(self):
        """Kiểm tra có phải thời điểm tránh reload không (8-11, 38-41)"""
        now = datetime.now()
        current_minute = now.minute
        
        # ✅ UPDATED: Avoid reload windows theo target_minutes mới
        avoid_windows = [
            range(8, 12),  # 8-11
            range(38, 42)  # 38-41
        ]
        
        for window in avoid_windows:
            if current_minute in window:
                return True
        
        return False

    def get_status(self):
        """Lấy trạng thái hiện tại của time manager"""
        now = datetime.now()
        next_check = self.get_next_check_time()
        
        return {
            'current_time': now.strftime('%H:%M:%S'),
            'current_minute': now.minute,
            'next_check_time': next_check.strftime('%H:%M:%S'),
            'seconds_until_next_check': self.get_time_until_next_check(),
            'is_check_time': self.is_check_time(),
            'is_avoid_reload_window': self.is_avoid_reload_window(),
            'target_minutes': self.target_minutes,
            'test_mode': CONFIG['timing'].get('test_mode', False)
        }
