# utils.py
import json
import os
import psutil
import subprocess
import time
from config import FAILED_CODES_FILE

def save_failed_code(code: str):
    """Lưu mã đã thử 3 lần vẫn failed"""
    try:
        if os.path.exists(FAILED_CODES_FILE):
            with open(FAILED_CODES_FILE, "r", encoding="utf-8") as f:
                failed = set(json.load(f))
        else:
            failed = set()
        failed.add(code)
        with open(FAILED_CODES_FILE, "w", encoding="utf-8") as f:
            json.dump(list(failed), f, ensure_ascii=False, indent=2)
        print(f"📝 FAILED CODE LOGGED: {code}")
    except Exception as e:
        print(f"⚠️ Failed-code save error: {e}")

def get_failed_codes():
    """Lấy danh sách codes đã failed"""
    try:
        if os.path.exists(FAILED_CODES_FILE):
            with open(FAILED_CODES_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
    except:
        pass
    return set()

def kill_zombie_chrome_processes():
    """Kill zombie Chrome processes trên VPS"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                try:
                    if proc.memory_percent() > 15:
                        print(f"🔪 Killing high-memory Chrome process: {proc.pid}")
                        proc.kill()
                except:
                    pass
    except Exception as e:
        print(f"⚠️ Process cleanup error: {e}")

def check_vps_resources():
    """Check VPS resources"""
    try:
        memory = psutil.virtual_memory()
        print(f"💾 VPS Memory: {memory.percent}% used")
        
        cpu = psutil.cpu_percent(interval=1)
        print(f"🖥️ VPS CPU: {cpu}% used")
        
        if memory.percent > 85:
            print("⚠️ WARNING: High memory usage, cleaning up...")
            kill_zombie_chrome_processes()
        
        if cpu > 85:
            print("⚠️ WARNING: High CPU usage, brief pause...")
            time.sleep(3)
            
    except Exception as e:
        print(f"⚠️ Resource check error: {e}")
