import os
from datetime import datetime

def git_push():
    try:
        # 顯示目前時間，作為 log
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] 📤 正在上傳 data_2025-04-18.csv 至 GitHub...")

        # 執行 Git 命令
        os.system("git pull origin main --rebase")
        os.system("git add data_2025-04-18.csv")
        os.system('git commit -m "自動更新資料"')
        os.system("git push origin main")

        print(f"[{now}] ✅ 資料上傳完成")
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__":
    git_push()
