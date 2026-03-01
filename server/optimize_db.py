#!/usr/bin/env python3
"""
昱金生能源 - 資料庫效能優化腳本
功能：建立索引、啟用外鍵約束、優化查詢
"""

import sqlite3
from pathlib import Path

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

def optimize_database():
    """優化資料庫"""
    print("\n🚀 昱金生能源 - 資料庫效能優化")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    
    # 1. 啟用外鍵約束
    print("\n🔗 啟用外鍵約束...")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.execute("PRAGMA foreign_keys")
    status = cursor.fetchone()[0]
    print(f"  外鍵約束狀態：{'✅ 已啟用' if status else '❌ 未啟用'}")
    
    # 2. 建立索引
    print("\n📊 建立效能索引...")
    
    indexes = [
        # 日報表索引
        ("idx_reports_date", "reports", "report_date"),
        ("idx_reports_employee", "reports", "employee_id"),
        ("idx_reports_case", "reports", "case_id"),
        
        # 風險項目索引
        ("idx_risks_status", "risk_items", "status"),
        ("idx_risks_level", "risk_items", "risk_level"),
        ("idx_risks_owner", "risk_items", "owner_id"),
        ("idx_risks_due_date", "risk_items", "due_date"),
        
        # 任務索引
        ("idx_tasks_status", "tasks", "status"),
        ("idx_tasks_priority", "tasks", "priority"),
        ("idx_tasks_owner", "tasks", "owner_id"),
        ("idx_tasks_due_date", "tasks", "due_date"),
        
        # 案件索引
        ("idx_cases_status", "cases", "status"),
        ("idx_cases_department", "cases", "department"),
        
        # 審計日誌索引
        ("idx_audit_timestamp", "audit_logs", "timestamp"),
        ("idx_audit_user", "audit_logs", "user_id"),
        ("idx_audit_action", "audit_logs", "action"),
        
        # 歷史記錄索引
        ("idx_risk_history_risk", "risk_history", "risk_id"),
        ("idx_risk_history_timestamp", "risk_history", "timestamp"),
        ("idx_task_history_task", "task_history", "task_id"),
        ("idx_task_history_timestamp", "task_history", "timestamp"),
    ]
    
    created_count = 0
    for index_name, table_name, column_name in indexes:
        try:
            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"
            conn.execute(sql)
            print(f"  ✅ {index_name} ON {table_name}({column_name})")
            created_count += 1
        except Exception as e:
            print(f"  ⚠️  {index_name} 建立失敗：{e}")
    
    print(f"\n  總計：{created_count} 個索引已建立")
    
    # 3. 分析資料庫（優化查詢計畫）
    print("\n📈 分析資料庫...")
    conn.execute("ANALYZE")
    print("  ✅ 資料庫分析完成")
    
    # 4. 清理空間（VACUUM）
    print("\n🧹 清理資料庫空間...")
    try:
        conn.execute("VACUUM")
        print("  ✅ 資料庫已重組")
    except Exception as e:
        print(f"  ⚠️  重組失敗：{e}")
    
    conn.commit()
    conn.close()
    
    # 5. 顯示資料庫大小
    size = DB_PATH.stat().st_size
    size_mb = size / (1024 * 1024)
    print(f"\n💾 資料庫大小：{size_mb:.2f} MB")
    
    print("\n✅ 資料庫優化完成！")
    print("="*60)

def check_index_usage():
    """檢查索引使用情況"""
    print("\n🔍 檢查索引使用情況...")
    
    conn = sqlite3.connect(DB_PATH)
    
    # 查詢所有索引
    cursor = conn.execute("""
        SELECT name, tbl_name
        FROM sqlite_master
        WHERE type='index'
        ORDER BY tbl_name, name
    """)
    
    indexes = cursor.fetchall()
    
    current_table = None
    for index_name, table_name in indexes:
        if table_name != current_table:
            print(f"\n  {table_name}:")
            current_table = table_name
        print(f"    - {index_name}")
    
    conn.close()
    print()

if __name__ == '__main__':
    optimize_database()
    check_index_usage()
