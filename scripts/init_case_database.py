#!/usr/bin/env python3
"""
昱金生能源 - 初始化案場資料庫
建立測試用案場資料（待替換為真實數據）
"""

import json
from pathlib import Path
from datetime import datetime

# 路徑設定
WORKSPACE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
DATA_DIR = WORKSPACE_DIR / 'daily_report_server' / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 測試案場資料（401 個案場中的樣本）
test_cases = []

# 生成 50 個測試案場
for i in range(1, 51):
    case_id = f"{i:02d}-{1000 + i}"
    test_cases.append({
        'case_id': case_id,
        'case_name': f"測試案場 {i}號" if i <= 10 else "",  # 前 10 個有名稱
        'capacity_kw': 100 + (i * 10),
        'location': f"彰化縣測試區 {i}路",
        'status': 'active',
        'commissioning_date': f"202{i % 5}-0{i % 9 + 1}-01",
        'email_count': 10 + i,
        'last_report_date': datetime.now().strftime('%Y-%m-%d')
    })

# 儲存案場資料庫
db_path = DATA_DIR / 'case_database_from_emails.json'
with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(test_cases, f, ensure_ascii=False, indent=2)

print(f"✅ 已建立 {len(test_cases)} 個測試案場")
print(f"📄 儲存位置：{db_path}")

# 統計
with_names = sum(1 for c in test_cases if c.get('case_name'))
print(f"📊 有名稱案場：{with_names}/{len(test_cases)} ({with_names/len(test_cases)*100:.1f}%)")
