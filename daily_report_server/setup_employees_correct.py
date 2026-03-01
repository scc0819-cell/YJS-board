#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立正確的 15 位員工名單（移除離職員工：林坤誼、黃振豪、許惠玲）
"""

import sqlite3
import os

DB_PATH = '/home/yjsclaw/.openclaw/workspace/daily_report_server/data/app.db'

# 正確的 15 位員工名單
EMPLOYEES = [
    # 管理部（5 人）
    ('20101', '宋啓綸', '管理部', 'admin'),
    ('20102', '游若誼', '管理部', 'manager'),
    ('22104', '洪淑嫆', '管理部', 'employee'),
    ('24106', '楊傑麟', '管理部', 'employee'),
    ('24108', '褚佩瑜', '管理部', 'employee'),
    
    # 工程部（5 人）
    ('23102', '楊宗衛', '工程部', 'employee'),
    ('24302', '張億峖', '工程部', 'manager'),
    ('25105', '陳明德', '工程部', 'employee'),
    ('25305', '李雅婷', '工程部', 'employee'),
    ('25308', '陳谷濱', '工程部', 'manager'),
    
    # 維運部（1 人）
    ('25108', '陳靜儒', '維運部', 'employee'),
    
    # 行政部（2 人）
    ('25106', '林天睛', '行政部', 'employee'),
    ('25311', '呂宜芹', '行政部', 'employee'),
    
    # 設計部（2 人）
    ('25107', '顏呈晞', '設計部', 'employee'),
    ('25110', '高竹妤', '設計部', 'employee'),
]

# 離職員工（需移除）
RESIGNED = ['lin_kun_yi', 'huang_zhen_hao', 'xu_hui_ling']

def setup_employees():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 建立 employees 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            employee_code TEXT UNIQUE,
            name TEXT NOT NULL,
            department TEXT,
            role TEXT DEFAULT 'employee',
            password_hash TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # 清空現有資料
    cursor.execute('DELETE FROM employees')
    
    # 插入正確的 15 位員工
    for code, name, dept, role in EMPLOYEES:
        # 使用 employee_id = employee_code（簡化）
        emp_id = code
        # 初始密碼 hash（Welcome2026!）
        import hashlib
        password_hash = hashlib.sha256('Welcome2026!'.encode()).hexdigest()
        
        cursor.execute('''
            INSERT OR REPLACE INTO employees 
            (employee_id, employee_code, name, department, role, password_hash, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (emp_id, code, name, dept, role, password_hash))
    
    # 移除離職員工（如果存在）
    for resigned_id in RESIGNED:
        cursor.execute('DELETE FROM employees WHERE employee_id = ?', (resigned_id,))
    
    conn.commit()
    
    # 驗證結果
    cursor.execute('SELECT employee_code, name, department, role FROM employees ORDER BY employee_code')
    rows = cursor.fetchall()
    
    print(f"✅ 已建立 {len(rows)} 位員工：\n")
    print(f"{'編號':<8} {'姓名':<10} {'部門':<10} {'角色':<10}")
    print("-" * 50)
    for row in rows:
        print(f"{row[0]:<8} {row[1]:<10} {row[2]:<10} {row[3]:<10}")
    
    print(f"\n✅ 總計：{len(rows)} 位員工（已移除離職員工：林坤誼、黃振豪、許惠玲）")
    
    conn.close()

if __name__ == "__main__":
    setup_employees()
