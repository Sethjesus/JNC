import csv
import os
import time
import random
from datetime import datetime

def get_today_csv_filename():
    return f"data_{datetime.now().strftime('%Y-%m-%d')}.csv"

def write_data_to_csv(filename, pm25, co2):
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["時間", "PM2.5 (μg/m³)", "CO2 (ppm)"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pm25, co2])

def push_to_git(filename):
    # 🧱 避免 Git crash：如果 lock file 或 rebase 尚未結束，就跳過
    if os.path.exists(".git/index.lock") or os.path.exists(".git/refs/heads/main.lock"):
        print("⚠️ Git 鎖定中，跳過這次操作")
        return
    if os.path.exists(".git/rebase-merge") or os.path.exists(".git/MERGE_HEAD"):
        print("⚠️ 正在進行 rebase 或合併衝突，跳過本次 Git 操作")
        return

    os.system(f"git add {filename}")

    has_changes = os.system("git diff --cached --quiet")
    if has_changes != 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        os.system(f'git commit -m "📈 自動更新 {filename} {now}"')
    else:
        print("🔁 無變更，跳過 commit")

    # ✅ stash 所有內容，防止 log.txt 或 .json 檔卡住 pull
    os.system('git stash push --include-untracked -m "auto_stash_before_pull"')

    # 嘗試 pull --rebase
    pull_status = os.system("git pull origin main --rebase")
    if pull_status != 0:
        print("⚠️ 無法 pull，請稍後重試或手動處理衝突")
        return

    # ✅ push 並還原 stash
    push_status = os.system("git push origin main")
    if push_status == 0:
        os.system("git stash pop")
    else:
        print("⚠️ 無法 push，可能遠端已更新")

while True:
    pm25 = round(random.uniform(10, 50), 2)
    co2 = round(random.uniform(400, 1000), 1)
    filename = get_today_csv_filename()

    write_data_to_csv(filename, pm25, co2)
    print(f"[{datetime.now()}] ✅ 寫入 CSV 成功：PM2.5={pm25}, CO2={co2}")

    push_to_git(filename)
    time.sleep(30)
