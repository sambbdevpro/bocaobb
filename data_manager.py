# data_manager.py
import threading
import json
import os
from datetime import datetime
from typing import List, Set

class DataManager:
    def __init__(self):
        self.db_file = "enterprise_data.json"
        self.last_check_file = "last_check.json"
        self.lock = threading.Lock()
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                self.known_codes = set(json.load(f))
        except:
            self.known_codes = set()
        
        try:
            with open(self.last_check_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.last_first_code = data.get('last_first_code', '')
                self.last_check_time = data.get('last_check_time', '')
        except:
            self.last_first_code = ''
            self.last_check_time = ''
    
    def save_data(self):
        with self.lock:
            try:
                with open(self.db_file, 'w', encoding='utf-8') as f:
                    json.dump(list(self.known_codes), f, ensure_ascii=False, indent=2)
                
                with open(self.last_check_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'last_first_code': self.last_first_code,
                        'last_check_time': self.last_check_time
                    }, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"❌ Save data error: {e}")
    
    def add_codes(self, codes: List[str]):
        with self.lock:
            self.known_codes.update(codes)
        self.save_data()
    
    def is_new_code(self, code: str) -> bool:
        with self.lock:
            return code not in self.known_codes
    
    def update_last_check(self, first_code: str):
        """Cập nhật mã đầu trang 1 cuối cùng"""
        with self.lock:
            self.last_first_code = first_code
            self.last_check_time = datetime.now().isoformat()
        self.save_data()

    def get_last_first_code(self) -> str:
        """Lấy mã đầu trang 1 cuối cùng"""
        with self.lock:
            return self.last_first_code

    def get_known_codes(self) -> Set[str]:
        with self.lock:
            return set(self.known_codes)
