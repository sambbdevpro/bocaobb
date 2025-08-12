# telegram_bot.py - FIXED: Enhanced constructor

import requests
import os
from config import CONFIG

class TelegramBot:
    def __init__(self, bot_token=None, chat_id=None):
        # ✅ FIXED: Support both parameter-based and config-based initialization
        self.bot_token = bot_token or CONFIG['telegram']['bot_token']
        self.chat_id = chat_id or CONFIG['telegram']['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, message):
        """Gửi tin nhắn"""
        if not CONFIG['telegram']['enabled']:
            return True
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=data, timeout=30)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Telegram message error: {e}")
            return False

    def send_document(self, file_path, caption=""):
        """Gửi file"""
        if not CONFIG['telegram']['enabled'] or not os.path.exists(file_path):
            return False
        
        try:
            url = f"{self.base_url}/sendDocument"
            with open(file_path, 'rb') as file:
                files = {'document': (os.path.basename(file_path), file, 'application/pdf')}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, files=files, data=data, timeout=120)
                return response.status_code == 200
                
        except Exception as e:
            print(f"❌ Telegram file error: {e}")
            return False
