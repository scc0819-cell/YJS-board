#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立員工資料表並插入 15 位員工
"""

import sqlite3
from pathlib import Path

DB_PATH = Path('/home/yjsclaw/.openclaw/workspace/daily_report_server/data/app.db')

# 15 位完整員工名單
EMPLOYEES = [
    # 管理部（5 人）
    ('20101', '宋啓綸', 'admin', '管理部'),
    ('20102', '游若誼', 'manager', '管理部'),
    ('22104', '洪淑嫆', 'employee', '管理部'),
    ('24106', '楊傑麟', 'employee', '管理部'),
    ('24108', '褚佩瑜', 'employee', '管理部'),
    
    # 工程部（5 人）
    ('23102', '楊宗衛', 'employee', '工程部'),
    ('24302', '張億峖', 'manager', '工程部'),
    ('25105', '陳明德', 'manager', '工程部'),
    ('25305', '李雅婷', 'employee', '工程部'),
    ('25308', '陳谷濱', 'manager', '工程部'),
    
    # 維運部（1 人）
    ('25108', '陳靜儒', 'employee', '維運部'),
    
    # 行政部（2 人）
    ('25106', '林天睛', 'employee', '行政部'),
    ('25311', '呂宜芹', 'employee', '行政部'),
    
    # 設計部（2 人）
    ('25107', '顏呈晞', 'employee', '設計部'),
    ('25110', '高竹妤', 'employee', '設計部'),
]

def main():
    print("="*70)
    print("🔧 建立員工資料表")
    print("="*70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 檢查是否已存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
    if cursor.fetchone():
        print("⚠️  employees 表已存在，先刪除...")
        cursor.execute("DROP TABLE employees")
    
    # 建立 employees 表
    print("📋 建立 employees 表...")
    cursor.execute('''
        CREATE TABLE employees (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 插入員工資料
    print("👥 插入 15 位員工...")
    
    default_password = 'Welcome2026!'  # 初始密碼
    
    for emp_id, name, role, dept in EMPLOYEES:
        username = name.lower().replace(' ', '_')
        # 特殊處理
        if emp_id == '20101':
            username = 'admin'
        
        try:
            cursor.execute('''
                INSERT INTO employees (id, name, username, password, role, department)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (emp_id, name, username, default_password, role, dept))
            print(f"  ✅ {emp_id} {name} ({username}) - {role} - {dept}")
        except sqlite3.IntegrityError as e:
            print(f"  ⚠️  {emp_id} {name} 已存在：{e}")
    
    conn.commit()
    
    # 驗證
    print("\n📊 驗證結果:")
    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    print(f"  員工總數：{count} 位")
    
    cursor.execute("SELECT id, name, username, role, department FROM employees LIMIT 5")
    print("\n  前 5 位員工:")
    for row in cursor.fetchall():
        print(f"    {row[0]} {row[1]} ({row[2]}) - {row[3]} - {row[4]}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("✅ 員工資料表建立完成！")
    print("="*70)
    print("\n🔐 登入資訊:")
    print("  董事長帳號：20101 或 admin")
    print("  初始密碼：Welcome2026!")
    print("\n🌐 立即登入：http://localhost:5000")
    print("="*70)

if __name__ == "__main__":
    main()
