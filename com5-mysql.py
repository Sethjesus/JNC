import time
import os
from datetime import datetime, timezone
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from influxdb_client import InfluxDBClient, Point, WritePrecision
import mysql.connector

# ✅ InfluxDB 設定
influx_token = "YYbHwHS2JDcYhun3He2OlloMGrm68OBtA0IhzwdhstJDptuUNwgTMd1aQ7Rc6Bppe4G9qDaGLPXHeWp0SDDN2A=="
influx_org = "台北市"
influx_bucket = "air_quality"
influx_url = "https://us-east-1-1.aws.cloud2.influxdata.com"

influx_client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
write_api = influx_client.write_api()

# ✅ MySQL 設定
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "S96910010a.",  # <<< 請填你的 MySQL 密碼
    "database": "env_data"
}

# ✅ Git push 函數（避免 rebase 衝突）
def git_push(files_to_commit):
    try:
        for file in files_to_commit:
            os.system(f"git add {file}")
        result = os.system("git diff --cached --quiet")
        if result != 0:
            os.system(f'git commit -m "自動更新 {datetime.now()}"')
            os.system("git push origin HEAD:main")
            print("✅ Git 推送成功")
        else:
            print("🔁 沒有變更，不需推送")
    except Exception as e:
        print(f"❌ Git 推送失敗: {e}")

# ✅ Modbus RTU 客戶端初始化
client = ModbusSerialClient(method='rtu', port='COM5', baudrate=9600, timeout=3)

# ✅ 每 30 秒讀取 Modbus
while True:
    if not client.connect():
        print("⚠️ COM5 連線失敗，5 秒後重試...")
        time.sleep(5)
        continue

    try:
        result = client.read_input_registers(address=0x0084, count=4, unit=1)
        if result.isError():
            print(f"[{datetime.now()}] ❌ Modbus 讀取失敗")
            time.sleep(5)
            continue

        decoder = BinaryPayloadDecoder.fromRegisters(
            result.registers,
            byteorder=Endian.Big,
            wordorder=Endian.Little
        )
        co2 = round(decoder.decode_32bit_float(), 1)
        pm25 = round(decoder.decode_32bit_float(), 2)
        now = datetime.now(timezone.utc)

        print(f"[{datetime.now()}] ✅ CO2={co2} ppm, PM2.5={pm25} μg/m³")

        # ✅ 寫入 InfluxDB
        point = (
            Point("env_data")
            .field("co2", co2)
            .field("pm25", pm25)
            .time(now, WritePrecision.NS)
        )
        write_api.write(bucket=influx_bucket, org=influx_org, record=point)

        # ✅ 寫入 MySQL
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            sql = "INSERT INTO env_metrics (recorded_at, co2, pm25) VALUES (%s, %s, %s)"
            cursor.execute(sql, (now.strftime("%Y-%m-%d %H:%M:%S"), co2, pm25))
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ 成功寫入 MySQL")
        except Exception as e:
            print(f"❌ MySQL 寫入失敗：{e}")

        # ✅ 寫入 log.txt 並推送 Git
        try:
            with open("log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"{now.isoformat()} | CO2={co2} ppm | PM2.5={pm25} μg/m³\n")
            git_push(["log.txt"])
        except Exception as e:
            print(f"❌ 寫入 log.txt 或 Git 推送失敗：{e}")

    except Exception as e:
        print(f"❌ 執行過程錯誤：{e}")

    time.sleep(30)
