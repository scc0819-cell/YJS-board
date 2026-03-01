#!/usr/bin/env python3
"""
昱金生能源集團 - 員工工號與附件管理設定
依據董事長提供的員工資料建立工號系統

附件歸檔結構：
/固定資料夾/年份/員工ID_姓名/日期/類型/檔案
範例：
/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments/2026/EMP-003_陳明德/2026-03-01/photo/xxx.jpg
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
USERS_JSON = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/users.json')
ATTACHMENTS_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments')

# 昱金生能源集團 - 員工工號對照表（依據董事長提供）
EMPLOYEE_DATA = {
    'EMP-001': {'name': '宋啓綸', 'title': '董事長', 'department': '管理部'},
    'EMP-002': {'name': '李雅婷', 'title': '管理員', 'department': '管理部'},
    'EMP-003': {'name': '陳明德', 'title': '工程專員', 'department': '工程部'},
    'EMP-004': {'name': '楊宗衛', 'title': '工程專員', 'department': '工程部'},
    'EMP-005': {'name': '洪淑嫆', 'title': '工程專員', 'department': '工程部'},
    'EMP-006': {'name': '陳谷濱', 'title': '財務專員', 'department': '財務部'},
    'EMP-007': {'name': '張億峖', 'title': '維運專員', 'department': '維運部'},
    'EMP-008': {'name': '林坤誼', 'title': '維運專員', 'department': '維運部'},
    'EMP-009': {'name': '黃振豪', 'title': '維運專員', 'department': '維運部'},
    'EMP-010': {'name': '許惠玲', 'title': '維運專員', 'department': '維運部'},
}

# 系統 ID 對照（保持向後相容）
SYSTEM_ID_MAP = {
    'EMP-001': 'admin',
    'EMP-002': 'li_ya_ting',
    'EMP-003': 'chen_ming_de',
    'EMP-004': 'yang_zong_wei',
    'EMP-005': 'hong_shu_rong',
    'EMP-006': 'chen_gu_bin',
    'EMP-007': 'zhang_yi_chuan',
    'EMP-008': 'lin_kun_yi',
    'EMP-009': 'huang_zhen_hao',
    'EMP-010': 'xu_hui_ling',
}

def setup_employee_system():
    """建立員工工號系統和附件歸檔結構"""
    
    print("📋 開始建立員工工號系統...\n")
    
    # 1. 建立 users.json
    users = {}
    for emp_code, emp_info in EMPLOYEE_DATA.items():
        system_id = SYSTEM_ID_MAP.get(emp_code, emp_code.lower().replace('-', '_'))
        
        # 預設密碼（首次登入強制修改）
        default_password = 'yjs2026' if emp_code == 'EMP-001' else '1234'
        
        users[system_id] = {
            'id': system_id,
            'employee_code': emp_code,
            'name': emp_info['name'],
            'chinese_name': emp_info['name'],
            'title': emp_info['title'],
            'department': emp_info['department'],
            'role': 'admin' if emp_code == 'EMP-001' else 'manager' if emp_code in ['EMP-003', 'EMP-006', 'EMP-007'] else 'employee',
            'enabled': True,
            'password_hash': '',  # 會由系統產生
            'password_temp': True,
            'manage_departments': [emp_info['department']] if emp_code in ['EMP-003', 'EMP-006', 'EMP-007'] else [],
            'manage_users': []
        }
    
    # 寫入 users.json
    with open(USERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已建立 {len(users)} 個員工帳號")
    
    # 2. 顯示員工清單
    print("\n📊 員工工號對照表：")
    print(f"{'工號':10} | {'姓名':10} | {'職稱':12} | {'部門':10} | {'角色':10} | {'系統 ID':20}")
    print("-" * 85)
    for emp_code, emp_info in EMPLOYEE_DATA.items():
        system_id = SYSTEM_ID_MAP.get(emp_code, emp_code.lower().replace('-', '_'))
        role = users[system_id]['role']
        print(f"{emp_code:10} | {emp_info['name']:10} | {emp_info['title']:12} | {emp_info['department']:10} | {role:10} | {system_id:20}")
    
    # 3. 建立附件歸檔目錄結構
    print("\n📁 建立附件歸檔目錄結構...")
    
    # 建立主目錄
    ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  ✅ 主目錄：{ATTACHMENTS_DIR}")
    
    # 建立年份目錄（2026-2030）
    for year in range(2026, 2031):
        year_dir = ATTACHMENTS_DIR / str(year)
        year_dir.mkdir(exist_ok=True)
        
        # 建立員工目錄
        for emp_code, emp_info in EMPLOYEE_DATA.items():
            system_id = SYSTEM_ID_MAP.get(emp_code, emp_code.lower().replace('-', '_'))
            emp_folder = f"{emp_code}_{emp_info['name']}"
            emp_dir = year_dir / emp_folder
            emp_dir.mkdir(exist_ok=True)
            
            # 建立日期目錄（預留）
            # 實際日期目錄會在上傳時動態建立
    
    print(f"  ✅ 已建立 2026-2030 年份目錄")
    print(f"  ✅ 已建立 {len(EMPLOYEE_DATA)} 個員工目錄")
    
    # 4. 顯示歸檔結構範例
    print("\n📋 附件歸檔結構範例：")
    print(f"""
{ATTACHMENTS_DIR}/
├── 2026/
│   ├── EMP-001_宋啓綸/
│   │   ├── 2026-03-01/
│   │   │   ├── photo/
│   │   │   ├── meeting/
│   │   │   ├── document/
│   │   │   └── other/
│   │   └── 2026-03-02/
│   ├── EMP-002_李雅婷/
│   ├── EMP-003_陳明德/
│   └── ...
├── 2027/
├── 2028/
├── 2029/
└── 2030/
    """)
    
    # 5. 資料庫更新（如果存在）
    if DB_PATH.exists():
        print("\n🗄️  更新資料庫員工資料...")
        conn = sqlite3.connect(DB_PATH)
        
        # 建立員工工號視圖
        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_employee_codes AS
            SELECT 
                id as system_id,
                json_extract(data, '$.employee_code') as employee_code,
                name,
                json_extract(data, '$.title') as title,
                json_extract(data, '$.department') as department,
                json_extract(data, '$.role') as role
            FROM users
            ORDER BY employee_code
        """)
        
        conn.commit()
        conn.close()
        print("  ✅ 已建立 v_employee_codes 視圖")
    
    # 6. 備份策略說明
    print("\n📦 備份策略：")
    print("  - 每三年備份一次")
    print("  - 備份範圍：整個 attachments 目錄")
    print("  - 備份格式：年份壓縮檔（2026.zip, 2027.zip, ...）")
    print("  - 備份位置：NAS 或外部儲存")
    print("\n  範例備份指令：")
    print(f"  cd {ATTACHMENTS_DIR}")
    print("  zip -r 2026_backup.zip 2026/")
    print("  zip -r 2027_backup.zip 2027/")
    
    print("\n✅ 員工工號系統設定完成！")
    print("\n💡 使用說明：")
    print("  1. 員工登入：使用系統 ID（chen_ming_de）或工號（EMP-003）")
    print("  2. 附件上傳：自動歸檔到 /年份/員工 ID_姓名/日期/類型/")
    print("  3. 備份：每三年執行一次，壓縮年份目錄")
    
    return users


if __name__ == '__main__':
    setup_employee_system()
