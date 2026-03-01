#!/usr/bin/env python3
"""
改善：部門別權限管理 + 中間主管權限
目的：
1. 新增部門別管理，支援組織架構
2. 中間主管只能查看所屬部門/人員的日報
3. 非他所屬部門/人員日報不顯示
4. 為未來績效管考系統預留介面
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
USERS_JSON = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/users.json')

# 集團組織架構（範例）
ORG_STRUCTURE = {
    '管理部': ['admin', 'li_ya_ting'],
    '工程部': ['chen_ming_de', 'yang_zong_wei', 'hong_shu_rong'],
    '財務部': ['chen_gu_bin'],
    '維運部': ['zhang_yi_chuan', 'lin_kun_yi', 'huang_zhen_hao', 'xu_hui_ling'],
}

# 主管設定（中間主管）
MANAGERS = {
    'chen_ming_de': {
        'role': 'manager',
        'department': '工程部',
        'manage_departments': ['工程部'],  # 可管理的部門
        'manage_users': ['yang_zong_wei', 'hong_shu_rong']  # 可管理的員工
    },
    'chen_gu_bin': {
        'role': 'manager',
        'department': '財務部',
        'manage_departments': ['財務部'],
        'manage_users': []
    },
    'zhang_yi_chuan': {
        'role': 'manager',
        'department': '維運部',
        'manage_departments': ['維運部'],
        'manage_users': ['lin_kun_yi', 'huang_zhen_hao', 'xu_hui_ling']
    }
}

def setup_departments():
    """建立部門別權限管理"""
    
    print("📋 開始設定部門別權限管理...")
    
    # 1. 更新 users.json
    if USERS_JSON.exists():
        with open(USERS_JSON, 'r', encoding='utf-8') as f:
            users = json.load(f)
    else:
        users = {}
    
    # 2. 更新員工部門
    for dept, members in ORG_STRUCTURE.items():
        for member_id in members:
            if member_id not in users:
                users[member_id] = {
                    'id': member_id,
                    'name': member_id,
                    'role': 'employee',
                    'department': dept,
                    'enabled': True,
                    'password_temp': False
                }
            else:
                users[member_id]['department'] = dept
            
            # 如果是主管，更新主管資訊
            if member_id in MANAGERS:
                mgr_info = MANAGERS[member_id]
                users[member_id].update({
                    'role': mgr_info['role'],
                    'manage_departments': mgr_info['manage_departments'],
                    'manage_users': mgr_info['manage_users']
                })
    
    # 3. 寫入 users.json
    with open(USERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 {len(users)} 個使用者資料")
    
    # 4. 在 SQLite 中建立部門視圖（方便查詢）
    conn = sqlite3.connect(DB_PATH)
    
    # 建立部門視圖
    conn.execute("""
        CREATE VIEW IF NOT EXISTS v_department_users AS
        SELECT 
            department,
            GROUP_CONCAT(id, ',') as user_ids,
            COUNT(*) as user_count
        FROM (
            SELECT id, department FROM users ORDER BY department, id
        )
        GROUP BY department
    """)
    
    # 建立主管視圖
    conn.execute("""
        CREATE VIEW IF NOT EXISTS v_managers AS
        SELECT 
            id,
            name,
            department,
            json_extract(data, '$.manage_departments') as manage_departments,
            json_extract(data, '$.manage_users') as manage_users
        FROM users
        WHERE json_extract(data, '$.role') = 'manager'
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ 部門視圖已建立")
    
    # 5. 顯示組織架構
    print("\n📊 集團組織架構：")
    for dept, members in ORG_STRUCTURE.items():
        mgr = next((m for m, info in MANAGERS.items() if info['department'] == dept), None)
        mgr_mark = "👑" if mgr else ""
        print(f"  {mgr_mark} {dept}: {', '.join(members)}")
    
    print("\n👑 主管設定：")
    for mgr_id, info in MANAGERS.items():
        print(f"  {mgr_id} ({info['department']}):")
        print(f"    可管理部門：{info['manage_departments']}")
        print(f"    可管理員工：{info['manage_users']}")
    
    print("\n✅ 部門別權限管理設定完成！")

if __name__ == '__main__':
    setup_departments()
