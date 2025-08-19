import os
import time
import zipfile
import requests
from datetime import datetime

# === Cấu hình ===
BOT_TOKEN = "7983597834:AAH9XAB_wYtEp7c-2mmzPz5NgO7_SnxKgVA"
CHAT_ID = "-1002812252160"
SEARCH_DIRECTORY = "."  # Dùng đường dẫn tuyệt đối
TEMP_ZIP_PREFIX = "pdfs_batch"
MAX_ZIP_SIZE_MB = 10  # <- Giới hạn zip file 10MB
TELEGRAM_FILE_LIMIT_MB = 50
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

def find_pdfs(directory):
    pdf_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def chunk_pdfs(pdfs, max_size_mb):
    """Chia file PDF thành các nhóm sao cho mỗi nhóm zip < max_size_mb."""
    batches = []
    current_batch = []
    current_size = 0
    max_bytes = max_size_mb * 1024 * 1024

    for pdf in pdfs:
        size = os.path.getsize(pdf)
        if size > max_bytes:
            print(f"[BỎ QUA] {pdf} quá lớn ({size/1024/1024:.2f} MB)")
            continue
        if current_size + size > max_bytes and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_size = 0
        current_batch.append(pdf)
        current_size += size
    if current_batch:
        batches.append(current_batch)
    return batches

def create_zip(batch, index):
    zip_name = f"{TEMP_ZIP_PREFIX}_{index}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for pdf in batch:
            zf.write(pdf, os.path.basename(pdf))
    return zip_name

def send_to_telegram(file_path):
    with open(file_path, 'rb') as f:
        resp = requests.post(API_URL, data={"chat_id": CHAT_ID}, files={"document": f})
    if resp.status_code == 200:
        print(f"[GỬI OK] {file_path}")
    else:
        print(f"[LỖI] Không gửi được {file_path} - {resp.text}")

def cleanup_files(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            if file.lower().endswith(".pdf") or file.lower().endswith(".zip"):
                os.remove(os.path.join(root, file))
        for d in dirs:
            try:
                os.rmdir(os.path.join(root, d))
            except OSError:
                pass

def main_task():
    print(f"\n[{datetime.now()}] Bắt đầu xử lý...")
    pdf_files = find_pdfs(SEARCH_DIRECTORY)
    if not pdf_files:
        print("Không tìm thấy PDF.")
        return
    batches = chunk_pdfs(pdf_files, MAX_ZIP_SIZE_MB)
    for idx, batch in enumerate(batches, start=1):
        zip_file = create_zip(batch, idx)
        # Bỏ qua nếu vượt quá giới hạn Telegram
        if os.path.getsize(zip_file) > TELEGRAM_FILE_LIMIT_MB * 1024 * 1024:
            print(f"[BỎ QUA] {zip_file} vì vượt quá 50MB Telegram.")
            os.remove(zip_file)
            continue
        send_to_telegram(zip_file)
    cleanup_files(SEARCH_DIRECTORY)
    print(f"[{datetime.now()}] Hoàn thành và dọn dẹp.")

if __name__ == "__main__":
    print("=== Script auto chạy tại phút 20 và 50 mỗi giờ ===")
    while True:
        now = datetime.now()
        if now.minute in (20, 50) and now.second == 0:
            main_task()
            time.sleep(60)  # Chờ hết phút này để tránh chạy lặp lại
        time.sleep(1)

