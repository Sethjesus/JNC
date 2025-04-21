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
    os.system(f"git add {filename}")
    os.system(f'git commit -m "📈 自動更新 {filename} {datetime.now()}"')
    os.system("git pull origin main --rebase")
    os.system("git push origin main")

while True:
    pm25 = round(random.uniform(10, 50), 2)
    co2 = round(random.uniform(400, 1000), 1)
    filename = get_today_csv_filename()

    write_data_to_csv(filename, pm25, co2)
    print(f"[{datetime.now()}] ✅ 寫入 CSV 成功：PM2.5={pm25}, CO2={co2}")

    push_to_git(filename)
    time.sleep(30)
