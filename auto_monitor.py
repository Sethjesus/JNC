import os
import csv
import time
import random
import mysql.connector
from datetime import datetime

def get_sensor_data():
    # 模擬感測器數據
    pm25 = round(random.uniform(10, 50), 2)
    co2 = round(random.uniform(400, 1000), 2)
    return pm25, co2

def write_to_csv(pm25, co2):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"data_{today}.csv"
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["time", "pm25", "co2"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pm25, co2])

def write_to_mysql(pm25, co2):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="S96910010a.",  # 👈 請改成你自己的密碼
        database="env_data"
    )
    cursor = conn.cursor()
    sql = "INSERT INTO env_metrics (recorded_at, pm25, co2) VALUES (NOW(), %s, %s)"
    cursor.execute(sql, (pm25, co2))
    conn.commit()
    cursor.close()
    conn.close()

def git_push():
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"data_{today}.csv"
    os.system("git pull origin main --rebase")
    os.system(f"git add {filename}")
    os.system(f'git commit -m "自動更新 {filename}"')
    os.system("git push origin main")

# 🧠 主流程：每 5 分鐘自動執行一次
while True:
    pm25, co2 = get_sensor_data()
    write_to_csv(pm25, co2)
    write_to_mysql(pm25, co2)
    git_push()

    print(f"✅ 已寫入 PM2.5: {pm25} μg/m³, CO2: {co2} ppm")
    time.sleep(300)  # 每 5 分鐘執行一次
