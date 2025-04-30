import os
import shutil
import subprocess
from datetime import datetime

# 你的專案路徑
project_path = r'C:\Users\User\Desktop\程式碼\Demo'
source_json = os.path.join(project_path, 'data.json')
target_json = os.path.join(project_path, 'docs', 'data.json')

# 步驟 1：複製 data.json 到 docs 資料夾
try:
    shutil.copy2(source_json, target_json)
    print(f"[{datetime.now()}] ✅ 已同步 data.json 到 docs 資料夾", flush=True)
except Exception as e:
    print(f"[{datetime.now()}] ❌ 同步失敗：{e}", flush=True)
    exit(1)

# 步驟 2：切換到專案目錄
os.chdir(project_path)

# 步驟 3：Git add + 檢查是否有變更再 push
try:
    os.system('git add docs/data.json')
    # 用 subprocess 檢查是否有 staged 的變更
    result = subprocess.run(['git', 'diff', '--cached', '--exit-code'], capture_output=True)
    if result.returncode != 0:
        commit_message = f'自動推送更新 data.json {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        os.system(f'git commit -m "{commit_message}"')
        os.system('git push origin main')
        print(f"[{datetime.now()}] ✅ 成功推送到 GitHub", flush=True)
    else:
        print(f"[{datetime.now()}] 💤 沒有變更，不需要推送", flush=True)
except Exception as e:
    print(f"[{datetime.now()}] ❌ Git 推送失敗：{e}", flush=True)
