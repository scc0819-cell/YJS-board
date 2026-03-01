#!/usr/bin/env python3
"""
昱金生能源 - 建立新员工帳號
根據董事長提供的清單建立 8 位新員工帳號
"""

import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

# 需要建立的新員工（董事長提供）
NEW_EMPLOYEES = [
    # (員工編號，中文名，系統 ID, 部門)
    ('20102', '游若誼', 'you_ruo_yi', '管理部'),
    ('24106', '楊傑麟', 'yang_jie_lin', '管理部'),
    ('24108', '褚佩瑜', 'chu_pei_yu', '管理部'),
    ('25106', '林天睛', 'lin_tian_jing', '行政部'),
    ('25107', '顏呈晞', 'yan_cheng_xi', '設計部'),
    ('25108', '陳靜儒', 'chen_jing_ru', '維運部'),
    ('25110', '高竹妤', 'gao_zhu_yu', '設計部'),
    ('25311', '呂宜芹', 'lu_yi_qin', '行政部'),
]

INITIAL_PASSWORD = 'Welcome2026!'


def hash_password(password):
    """雜湊密碼"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_employees():
    """建立新员工帳號"""
    conn = sqlite3.connect(DB_PATH)
    
    print("🆕 開始建立新员工帳號...\n")
    
    created_count = 0
    skipped_count = 0
    
    for emp_code, chinese_name, system_id, department in NEW_EMPLOYEES:
        # 檢查用戶是否已存在
        cursor = conn.execute("""
            SELECT id FROM users WHERE id = ?
        """, (system_id,))
        
        if cursor.fetchone():
            print(f"⚠️  跳過：{chinese_name} ({system_id}) - 帳號已存在")
            skipped_count += 1
            continue
        
        # 建立新用戶
        password_hash = hash_password(INITIAL_PASSWORD)
        password_changed_at = datetime.now().isoformat()
        password_expires_at = (datetime.now() + timedelta(days=90)).isoformat()
        
        conn.execute("""
            INSERT INTO users 
            (id, name, chinese_name, employee_code, department, role, password_hash, 
             password_temp, password_changed_at, password_expires_at, enabled,
             manage_departments, manage_users, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'employee', ?, 1, ?, ?, 1, '[]', '[]', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (system_id, chinese_name, chinese_name, emp_code, department, password_hash,
              password_changed_at, password_expires_at))
        
        print(f"✅ 建立：{chinese_name} ({system_id})")
        print(f"   編號：{emp_code}")
        print(f"   部門：{department}")
        print(f"   初始密碼：{INITIAL_PASSWORD}")
        print(f"   首次登入需修改密碼 ✅")
        print()
        
        created_count += 1
    
    conn.commit()
    conn.close()
    
    print("="*60)
    print("📊 建立完成:")
    print(f"   已建立：{created_count} 人")
    print(f"   已跳過：{skipped_count} 人")
    print(f"   總人數：{len(NEW_EMPLOYEES)} 人")
    print("="*60)
    
    print("\n📋 初始密碼通知")
    print(f"   所有新員工的初始密碼：{INITIAL_PASSWORD}")
    print(f"   首次登入時系統會強制要求修改密碼")
    print("\n💡 建議行動:")
    print("   1. 將初始密碼個別通知員工")
    print("   2. 提醒員工首次登入需修改密碼")
    print("   3. 安排教育訓練時間")
    
    # 匯出完整清單
    print("\n📋 完整員工清單:")
    export_employee_list()


def export_employee_list():
    """匯出完整員工清單"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.execute("""
        SELECT id, employee_code, chinese_name, department, role, enabled
        FROM users
        WHERE enabled = 1
        ORDER BY department, employee_code
    """)
    
    users = cursor.fetchall()
    conn.close()
    
    # 依部門分組
    by_dept = {}
    for user in users:
        dept = user['department'] or '未分類'
        if dept not in by_dept:
            by_dept[dept] = []
        by_dept[dept].append(dict(user))
    
    print("\n" + "="*70)
    print("📋 昱金生能源 - 完整員工清單")
    print("="*70)
    
    total = 0
    for dept, employees in sorted(by_dept.items()):
        print(f"\n### {dept} ({len(employees)}人)")
        print(f"{'編號':<10} {'姓名':<10} {'系統 ID':<20} {'角色':<10}")
        print("-" * 60)
        
        for user in employees:
            code = user['employee_code'] or '未設定'
            name = user['chinese_name'] or 'N/A'
            print(f"{code:<10} {name:<10} {user['id']:<20} {user['role'] or 'employee':<10}")
        
        total += len(employees)
    
    print("\n" + "="*70)
    print(f"總員工數：{total} 人")
    print("="*70)


if __name__ == '__main__':
    create_employees()
