import os
import time
import json
import csv
from datetime import datetime, timedelta
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from influxdb_client import InfluxDBClient, Point, WritePrecision
import mysql.connector

# ✅ InfluxDB 設定
influx_token = "你的 InfluxDB Token"
influx_org = "台北市"
influx_bucket = "air_quality"
influx_url = "https://us-east-1-1.aws.cloud2.influxdata.com"
influx_client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
write_api = influx_client.write_api()

# ✅ MySQL 設定
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "S96910010a.",
    "database": "env_data"
}

# ✅ Git 推送函數
def git_push(files_to_commit):
    try:
        if os.path.exists(".git/index.lock"):
            os.remove(".git/index.lock")
        if os.path.exists(".git/rebase-merge"):
            os.system("rmdir /s /q .git\\rebase-merge")

        os.system("git checkout main")
        os.system("git stash && git pull origin main --rebase && git stash pop")

        for file in files_to_commit:
            os.system(f"git add {file}")
        if os.system("git diff --cached --quiet") != 0:
            os.system(f'git commit -m "自動更新 {datetime.now()}"')
            os.system("git push origin main")
            print("✅ Git 推送成功")
        else:
            print("🔁 沒有變更，不需推送")
    except Exception as e:
        print(f"❌ Git 推送失敗：{e}")

# ✅ Modbus RTU 初始化
client = ModbusSerialClient(method='rtu', port='COM4', baudrate=9600, timeout=3)

while True:
    if not client.connect():
        print("⚠️ COM5 無法連線，5 秒後重試...")
        time.sleep(5)
        continue

    try:
        result = client.read_input_registers(address=0x0084, count=4, unit=1)
        if result.isError():
            print(f"[{datetime.now()}] ❌ Modbus 讀取失敗")
            time.sleep(5)
            continue

        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        co2 = round(decoder.decode_32bit_float(), 1)
        pm25 = round(decoder.decode_32bit_float(), 2)

        # ✅ 台灣時間（UTC+8）
        taiwan_now = datetime.utcnow() + timedelta(hours=8)
        timestamp = taiwan_now.strftime("%Y-%m-%d %H:%M:%S")
        date_str = taiwan_now.strftime("%Y-%m-%d")
        csv_filename = f"data_{date_str}.csv"

        print(f"[{timestamp}] ✅ CO2={co2} ppm, PM2.5={pm25} μg/m³")

        # ✅ InfluxDB 寫入
        try:
            point = Point("env_data").field("co2", co2).field("pm25", pm25).time(taiwan_now, WritePrecision.NS)
            write_api.write(bucket=influx_bucket, org=influx_org, record=point)
        except Exception as e:
            print(f"❌ InfluxDB 寫入失敗：{e}")

        # ✅ MySQL 寫入
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO env_metrics (recorded_at, co2, pm25) VALUES (%s, %s, %s)",
                           (timestamp, co2, pm25))
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ 成功寫入 MySQL")
        except Exception as e:
            print(f"❌ MySQL 寫入失敗：{e}")

        # ✅ 寫入 data.json 與 docs/data.json
        json_data = {
            "timestamp": timestamp,
            "co2": co2,
            "pm25": pm25
        }
        try:
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            with open("docs/data.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            print("✅ 寫入與同步 data.json → docs/data.json")
        except Exception as e:
            print(f"❌ JSON 寫入失敗：{e}")

        # ✅ 寫入 CSV
        try:
            file_exists = os.path.isfile(csv_filename)
            with open(csv_filename, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                if not file_exists:
                    writer.writerow(["時間", "CO2(ppm)", "PM2.5(μg/m³)"])
                writer.writerow([timestamp, co2, pm25])
        except Exception as e:
            print(f"❌ CSV 寫入失敗：{e}")

        # ✅ 寫入 log
        try:
            with open("log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"{taiwan_now.isoformat()} | CO2={co2} ppm | PM2.5={pm25} μg/m³\n")
        except Exception as e:
            print(f"❌ log.txt 寫入失敗：{e}")

        # ✅ Git 推送
        git_push(["data.json", "docs/data.json", csv_filename, "log.txt"])

    except Exception as e:
        print(f"❌ 執行錯誤：{e}")

    time.sleep(30)
