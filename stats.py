# stats.py
import threading

class RobustStats:
    def __init__(self):
        self.lock = threading.Lock()
        self.processed = 0
        self.success = 0
        self.failed = 0
        self.retry_needed = []
        
    def add_result(self, success: bool, code: str = ""):
        with self.lock:
            self.processed += 1
            if success:
                self.success += 1
            else:
                self.failed += 1
                if code and code not in self.retry_needed:
                    self.retry_needed.append(code)
            print(f"📊 SPEED STATS: {self.success}/{self.processed} success, {len(self.retry_needed)} need retry")
    
    def get_retry_codes(self):
        with self.lock:
            return self.retry_needed.copy()
    
    def clear_retry_codes(self):
        with self.lock:
            self.retry_needed.clear()
    
    def get_stats(self):
        with self.lock:
            return {
                'processed': self.processed, 
                'success': self.success, 
                'failed': self.failed,
                'retry_needed': len(self.retry_needed)
            }

# Global stats instance
stats = RobustStats()
