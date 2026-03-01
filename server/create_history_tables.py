#!/usr/bin/env python3
"""
改善 C：風險/任務歷程追蹤
建立 risk_history 和 task_history 表，記錄所有狀態變更
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

def create_history_tables():
    """建立風險和任務的歷史記錄表"""
    
    conn = sqlite3.connect(DB_PATH)
    
    # 1. 風險歷史記錄表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS risk_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            risk_id INTEGER NOT NULL,
            changed_at TEXT NOT NULL,
            changed_by TEXT NOT NULL,
            change_type TEXT NOT NULL,
            old_status TEXT,
            new_status TEXT,
            old_owner TEXT,
            new_owner TEXT,
            old_due_date TEXT,
            new_due_date TEXT,
            old_level TEXT,
            new_level TEXT,
            comment TEXT,
            FOREIGN KEY (risk_id) REFERENCES risks(id)
        )
    """)
    
    # 2. 任務歷史記錄表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS task_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            changed_at TEXT NOT NULL,
            changed_by TEXT NOT NULL,
            change_type TEXT NOT NULL,
            old_status TEXT,
            new_status TEXT,
            old_owner TEXT,
            new_owner TEXT,
            old_due_date TEXT,
            new_due_date TEXT,
            old_priority TEXT,
            new_priority TEXT,
            comment TEXT,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)
    
    # 3. 增加索引加速查詢
    conn.execute("CREATE INDEX IF NOT EXISTS idx_risk_history_risk_id ON risk_history(risk_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_task_history_task_id ON task_history(task_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_risk_history_changed_at ON risk_history(changed_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_task_history_changed_at ON task_history(changed_at)")
    
    conn.commit()
    conn.close()
    
    print("✅ 風險/任務歷史記錄表建立完成！")
    print("   - risk_history: 記錄所有風險狀態變更")
    print("   - task_history: 記錄所有任務狀態變更")

if __name__ == '__main__':
    create_history_tables()
