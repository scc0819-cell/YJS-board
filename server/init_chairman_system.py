#!/usr/bin/env python3
"""
昱金生能源 - 董事長報告系統初始化
建立必要的資料庫表
"""

import sqlite3
from pathlib import Path

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

def init_tables():
    """建立董事長報告相關表"""
    conn = sqlite3.connect(DB_PATH)
    
    # 董事長通知表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chairman_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            priority TEXT DEFAULT 'normal',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0,
            read_at TIMESTAMP
        )
    """)
    
    # 員工通知表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS employee_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            notification_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0,
            read_at TIMESTAMP
        )
    """)
    
    # 建立索引
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_chairman_notif_created
        ON chairman_notifications(created_at DESC)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_employee_notif_employee
        ON employee_notifications(employee_id, created_at DESC)
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ 董事長報告系統初始化完成")
    print("  - chairman_notifications 表已建立")
    print("  - employee_notifications 表已建立")
    print("  - 索引已建立")

if __name__ == '__main__':
    init_tables()
