# pdf_processor.py
import os
import time
import glob
import shutil
from datetime import datetime
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, as_completed

class PDFProcessor:
    def __init__(self, browser_manager, telegram_bot):
        self.browser = browser_manager
        self.telegram_bot = telegram_bot
        self.download_folder = f"enterprise_pdfs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.download_folder, exist_ok=True)
        
    def download_pdfs_for_codes(self, codes):
        """Download PDF cho danh sách mã số DN"""
        if not codes:
            print("⚠️ No codes to download")
            return
        
        print(f"📥 Starting download for {len(codes)} codes...")
        
        successful_downloads = []
        failed_downloads = []
        
        for i, code in enumerate(codes):
            try:
                print(f"📄 [{i+1}/{len(codes)}] Processing code: {code}")
                
                if self._download_pdf_for_code(code):
                    successful_downloads.append(code)
                    print(f"✅ Successfully downloaded: {code}")
                else:
                    failed_downloads.append(code)
                    print(f"❌ Failed to download: {code}")
                    
                # Delay between downloads
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error processing code {code}: {e}")
                failed_downloads.append(code)
        
        # Gửi báo cáo qua Telegram
        self._send_download_report(successful_downloads, failed_downloads)
        
        return successful_downloads, failed_downloads
    
    def _download_pdf_for_code(self, code):
        """Download PDF cho một mã số DN cụ thể"""
        try:
            # Tìm PDF link cho code này
            pdf_selectors = [
                f"//td[contains(text(), '{code}')]/following-sibling::td//a[contains(@id, 'LnkGetPDFActive')]",
                f"//td[contains(text(), '{code}')]/following-sibling::td//input[contains(@id, 'LnkGetPDFActive')]",
                f"//tr[contains(., '{code}')]//a[contains(@id, 'LnkGetPDFActive')]",
                f"//tr[contains(., '{code}')]//input[contains(@id, 'LnkGetPDFActive')]"
            ]
            
            pdf_element = None
            for selector in pdf_selectors:
                try:
                    elements = self.browser.driver.find_elements(By.XPATH, selector)
                    if elements and elements[0].is_displayed():
                        pdf_element = elements[0]
                        break
                except:
                    continue
            
            if not pdf_element:
                print(f"⚠️ PDF link not found for code: {code}")
                return False
            
            # Click để download
            self.browser.driver.execute_script("arguments[0].scrollIntoView();", pdf_element)
            time.sleep(1)
            self.browser.driver.execute_script("arguments[0].click();", pdf_element)
            
            # Đợi file download
            time.sleep(8)
            
            # Kiểm tra file đã download
            return self._check_and_rename_downloaded_file(code)
            
        except Exception as e:
            print(f"❌ Download error for {code}: {e}")
            return False
    
    def _check_and_rename_downloaded_file(self, code):
        """Kiểm tra và đổi tên file đã download"""
        try:
            # Tìm file PDF mới nhất trong thư mục download
            download_folders = glob.glob(f"{self.browser.download_folder}*")
            if not download_folders:
                print(f"⚠️ Download folder not found for {code}")
                return False
            
            latest_folder = max(download_folders, key=os.path.getctime)
            
            # Tìm file PDF mới nhất
            pdf_files = glob.glob(os.path.join(latest_folder, "*.pdf"))
            if not pdf_files:
                print(f"⚠️ No PDF file found for {code}")
                return False
            
            latest_file = max(pdf_files, key=os.path.getctime)
            
            # Đổi tên và di chuyển file
            target_filename = f"{code}.pdf"
            target_path = os.path.join(self.download_folder, target_filename)
            
            # Nếu file đã tồn tại, thêm số thứ tự
            counter = 1
            while os.path.exists(target_path):
                target_filename = f"{code}_v{counter}.pdf"
                target_path = os.path.join(self.download_folder, target_filename)
                counter += 1
            
            # Di chuyển và đổi tên file
            shutil.move(latest_file, target_path)
            
            print(f"📁 File saved as: {target_filename}")
            
            # Gửi file qua Telegram
            self._send_pdf_to_telegram(target_path, code)
            
            return True
            
        except Exception as e:
            print(f"❌ File processing error for {code}: {e}")
            return False
    
    def _send_pdf_to_telegram(self, file_path, code):
        """Gửi PDF lên Telegram"""
        try:
            caption = f"📄 <b>Enterprise PDF</b>\n🔢 Code: <code>{code}</code>\n⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
            
            success = self.telegram_bot.send_document(file_path, caption)
            if success:
                print(f"📱 Sent to Telegram: {code}")
            else:
                print(f"⚠️ Failed to send to Telegram: {code}")
                
        except Exception as e:
            print(f"❌ Telegram send error for {code}: {e}")
    
    def _send_download_report(self, successful, failed):
        """Gửi báo cáo download qua Telegram"""
        try:
            total = len(successful) + len(failed)
            success_rate = (len(successful) / total * 100) if total > 0 else 0
            
            report = f"""📊 <b>Download Report</b>
📈 Total: {total}
✅ Successful: {len(successful)}
❌ Failed: {len(failed)}
📊 Success rate: {success_rate:.1f}%
📁 Folder: {self.download_folder}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            if failed:
                failed_codes = ', '.join(failed[:10])  # Hiển thị tối đa 10 mã lỗi
                if len(failed) > 10:
                    failed_codes += f"... and {len(failed)-10} more"
                report += f"\n\n❌ Failed codes: {failed_codes}"
            
            self.telegram_bot.send_message(report)
            
        except Exception as e:
            print(f"❌ Report send error: {e}")
