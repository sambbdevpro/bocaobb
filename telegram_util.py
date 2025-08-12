# telegram_util.py - ULTIMATE VERSION with robust error handling

import requests
import time
import threading
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import CONFIG

class TelegramBot:
    """
    🔥 ULTIMATE Telegram Bot với robust error handling
    - Rate limiting compliance (429 error fix)
    - Message size validation (400 error fix)
    - Exponential backoff retry mechanism
    - Queue-based message sending
    - File upload optimization
    """
    
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # 🔥 Enhanced session với retry strategy
        self.session = requests.Session()
        self.session.verify = False
        
        # Enhanced retry strategy cho rate limiting
        retry_strategy = Retry(
            total=5,  # Increased retries
            backoff_factor=2,  # Exponential backoff
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 🔧 Rate limiting management
        self.last_message_time = 0
        self.message_count = 0
        self.rate_limit_window = 60  # 1 minute window
        self.max_messages_per_minute = 15  # Conservative limit (< 20)
        self.message_lock = threading.Lock()
        
        # 🔧 Message queue để handle rate limiting
        self.message_queue = []
        self.queue_lock = threading.Lock()
        self.queue_processor_active = False
        
        print("✅ ULTIMATE Telegram Bot initialized with rate limiting")
    
    def _check_rate_limit(self):
        """🔧 Check và enforce rate limiting"""
        current_time = time.time()
        
        with self.message_lock:
            # Reset counter nếu đã qua 1 minute
            if current_time - self.last_message_time > self.rate_limit_window:
                self.message_count = 0
                self.last_message_time = current_time
            
            # Check nếu đã exceed rate limit
            if self.message_count >= self.max_messages_per_minute:
                wait_time = self.rate_limit_window - (current_time - self.last_message_time)
                if wait_time > 0:
                    print(f"⏳ Rate limit reached, waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    self.message_count = 0
                    self.last_message_time = time.time()
            
            self.message_count += 1
    
    def _validate_message_content(self, text, caption=None):
        """🔧 Validate message content để avoid 400 errors"""
        # Truncate message nếu quá dài
        if len(text) > 4096:
            text = text[:4093] + "..."
            print(f"⚠️ Message truncated to 4096 characters")
        
        # Truncate caption nếu quá dài
        if caption and len(caption) > 1024:
            caption = caption[:1021] + "..."
            print(f"⚠️ Caption truncated to 1024 characters")
        
        return text, caption
    
    def send_message(self, text):
        """🔥 Enhanced send message với robust error handling"""
        if not CONFIG['telegram']['enabled']:
            return True
        
        try:
            # Validate content
            text, _ = self._validate_message_content(text)
            
            # Check rate limit
            self._check_rate_limit()
            
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            # 🔧 Retry với exponential backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.session.post(url, json=data, timeout=30)
                    
                    if response.status_code == 200:
                        print("📱 Telegram: Message sent successfully")
                        return True
                    elif response.status_code == 429:
                        # Rate limit hit - extract retry_after
                        retry_after = self._extract_retry_after(response)
                        wait_time = retry_after if retry_after else (2 ** attempt)
                        print(f"⏳ Rate limited (429), waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    elif response.status_code == 400:
                        print(f"❌ Bad request (400): {response.text}")
                        # Try to fix và retry
                        if "message is too long" in response.text.lower():
                            text = text[:3000] + "..."  # More aggressive truncation
                            data["text"] = text
                            continue
                        else:
                            return False
                    else:
                        print(f"❌ Telegram error: {response.status_code}")
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        return False
                        
                except requests.exceptions.RequestException as e:
                    print(f"❌ Request error (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return False
            
            return False
            
        except Exception as e:
            print(f"❌ Telegram send error: {e}")
            return False
    
    def send_document(self, file_path, caption=""):
        """🔥 Enhanced send document với file validation và rate limiting"""
        if not CONFIG['telegram']['enabled'] or not os.path.exists(file_path):
            return False
        
        try:
            # Validate file size (Telegram limit: 50MB)
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:  # 50MB
                print(f"❌ File too large: {file_size / 1024 / 1024:.1f}MB (max 50MB)")
                return False
            
            # Validate caption
            _, caption = self._validate_message_content("", caption)
            
            # Check rate limit
            self._check_rate_limit()
            
            url = f"{self.base_url}/sendDocument"
            
            # 🔧 Retry với exponential backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with open(file_path, 'rb') as file:
                        files = {
                            'document': (os.path.basename(file_path), file, 'application/pdf')
                        }
                        data = {
                            'chat_id': self.chat_id,
                            'caption': caption,
                            'parse_mode': 'HTML'
                        }
                        
                        response = self.session.post(url, files=files, data=data, timeout=120)
                    
                    if response.status_code == 200:
                        print(f"📱 Telegram: File sent successfully - {os.path.basename(file_path)}")
                        return True
                    elif response.status_code == 429:
                        # Rate limit hit
                        retry_after = self._extract_retry_after(response)
                        wait_time = retry_after if retry_after else (2 ** attempt)
                        print(f"⏳ File upload rate limited (429), waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    elif response.status_code == 400:
                        error_text = response.text
                        print(f"❌ File upload bad request (400): {error_text}")
                        
                        # Handle specific 400 errors
                        if "file too big" in error_text.lower():
                            print("❌ File size exceeds Telegram limit")
                            return False
                        elif "wrong file identifier" in error_text.lower():
                            print("❌ Invalid file format")
                            return False
                        else:
                            # Try with shorter caption
                            if len(caption) > 200:
                                caption = caption[:197] + "..."
                                continue
                            return False
                    else:
                        print(f"❌ Telegram file error: {response.status_code}")
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)
                            continue
                        return False
                        
                except requests.exceptions.RequestException as e:
                    print(f"❌ File upload request error (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return False
            
            return False
            
        except Exception as e:
            print(f"❌ Telegram file send error: {e}")
            return False
    
    def _extract_retry_after(self, response):
        """🔧 Extract retry_after từ 429 response"""
        try:
            response_data = response.json()
            retry_after = response_data.get('parameters', {}).get('retry_after', None)
            return retry_after
        except:
            return None
    
    def send_message_async(self, text):
        """🔄 Queue message để send trong background"""
        with self.queue_lock:
            self.message_queue.append(('message', text, None))
        
        # Start queue processor nếu chưa active
        if not self.queue_processor_active:
            threading.Thread(target=self._process_message_queue, daemon=True).start()
    
    def send_document_async(self, file_path, caption=""):
        """🔄 Queue document để send trong background"""
        with self.queue_lock:
            self.message_queue.append(('document', file_path, caption))
        
        # Start queue processor nếu chưa active
        if not self.queue_processor_active:
            threading.Thread(target=self._process_message_queue, daemon=True).start()
    
    def _process_message_queue(self):
        """🔄 Process message queue với controlled rate"""
        self.queue_processor_active = True
        
        try:
            while True:
                with self.queue_lock:
                    if not self.message_queue:
                        break
                    item = self.message_queue.pop(0)
                
                msg_type, content, extra = item
                
                if msg_type == 'message':
                    self.send_message(content)
                elif msg_type == 'document':
                    self.send_document(content, extra or "")
                
                # Add delay để comply với rate limits
                time.sleep(1.5)  # 1.5s between messages
                
        except Exception as e:
            print(f"❌ Queue processor error: {e}")
        finally:
            self.queue_processor_active = False
    
    def send_batch_summary(self, downloads_info):
        """📊 Send batch summary thay vì individual messages"""
        try:
            if not downloads_info:
                return True
            
            # Group by status
            successful = [info for info in downloads_info if info.get('success', False)]
            failed = [info for info in downloads_info if not info.get('success', False)]
            
            # Create summary message
            summary = f"📊 <b>BATCH DOWNLOAD SUMMARY</b>\n"
            summary += f"✅ Successful: {len(successful)}\n"
            summary += f"❌ Failed: {len(failed)}\n"
            summary += f"📈 Success Rate: {len(successful)/len(downloads_info)*100:.1f}%\n"
            summary += f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
            
            # Add successful codes (limited)
            if successful:
                summary += "✅ <b>Downloaded:</b>\n"
                for info in successful[:10]:  # Limit to first 10  
                    summary += f"• <code>{info['dn_code']}</code>\n"
                if len(successful) > 10:
                    summary += f"• ... and {len(successful) - 10} more\n"
            
            # Add failed codes if any
            if failed:
                summary += "\n❌ <b>Failed:</b>\n"
                for info in failed[:5]:  # Limit to first 5
                    summary += f"• <code>{info['dn_code']}</code>\n"
            
            return self.send_message(summary)
            
        except Exception as e:
            print(f"❌ Batch summary error: {e}")
            return False
