import time
import subprocess
from datetime import datetime

# 每次間隔（秒）
interval_seconds = 300  # 300秒 = 5分鐘
log_file = "scheduler.log"  # log檔案名稱

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")

log_message(f"⏳ 啟動自動推送排程，每 {interval_seconds/60:.0f} 分鐘執行一次...")

while True:
    try:
        log_message("▶️ 開始執行 auto_push_to_github.py")
        subprocess.run(["python", "auto_push_to_github.py"], check=True)
        log_message("✅ 本次執行完成，等待下次...")
    except Exception as e:
        log_message(f"❌ 執行錯誤: {e}")
    
    time.sleep(interval_seconds)
