# auto_push_data.py
import json
import random
import time
import os
from datetime import datetime

def push_to_git():
    os.system("git pull origin main --rebase")
    os.system("git add data.json")
    os.system(f'git commit -m "自動更新資料 {datetime.now()}"')
    os.system("git push origin main")

while True:
    data = {
        "pm25": round(random.uniform(10, 50), 2),
        "co2": round(random.uniform(400, 1000), 1)
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[{datetime.now()}] ✅ 資料已更新：", data)
    push_to_git()
    time.sleep(30)
