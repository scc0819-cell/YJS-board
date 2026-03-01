#!/usr/bin/env python3
"""
昱金生能源 - 員工離職處理腳本
功能：員工離職時快速停用帳號並轉移任務/資料
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

def get_user_info(user_id):
    """取得用戶資訊"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_tasks(user_id):
    """取得用戶的任務清單"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT id, title, status, case_id, due_date, priority
        FROM tasks
        WHERE owner_id = ? AND status != 'closed'
    """, (user_id,))
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks

def get_user_risks(user_id):
    """取得用戶的風險項目清單"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT id, title, status, case_id, risk_level, due_date
        FROM risk_items
        WHERE owner_id = ? AND status != 'closed'
    """, (user_id,))
    risks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return risks

def get_user_reports(user_id):
    """取得用戶的日報清單"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT id, report_date, case_id, created_at
        FROM reports
        WHERE employee_id = ?
        ORDER BY report_date DESC
        LIMIT 100
    """, (user_id,))
    reports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reports

def transfer_tasks(from_user_id, to_user_id):
    """轉移任務"""
    conn = sqlite3.connect(DB_PATH)
    
    cursor = conn.execute("""
        UPDATE tasks
        SET owner_id = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE owner_id = ? AND status != 'closed'
    """, (to_user_id, from_user_id))
    
    count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return count

def transfer_risks(from_user_id, to_user_id):
    """轉移風險項目"""
    conn = sqlite3.connect(DB_PATH)
    
    cursor = conn.execute("""
        UPDATE risk_items
        SET owner_id = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE owner_id = ? AND status != 'closed'
    """, (to_user_id, from_user_id))
    
    count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return count

def disable_user(user_id, reason='離職'):
    """停用用戶帳號"""
    conn = sqlite3.connect(DB_PATH)
    
    conn.execute("""
        UPDATE users
        SET enabled = 0,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (user_id,))
    
    conn.commit()
    conn.close()

def generate_handover_report(user_id, to_user_id=None):
    """生成交接報告"""
    user = get_user_info(user_id)
    tasks = get_user_tasks(user_id)
    risks = get_user_risks(user_id)
    reports = get_user_reports(user_id)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'employee': user,
        'reason': '離職',
        'handover_to': to_user_id,
        'summary': {
            'active_tasks': len(tasks),
            'active_risks': len(risks),
            'total_reports': len(reports)
        },
        'tasks': tasks,
        'risks': risks,
        'recent_reports': reports[:20]
    }
    
    return report

def process_resignation(user_id, to_user_id=None, disable=True):
    """
    處理員工離職
    
    參數:
        user_id: 離職員工 ID
        to_user_id: 接手員工 ID（可選）
        disable: 是否停用帳號
    """
    print("\n🔄 處理員工離職")
    print("="*60)
    
    # 1. 取得用戶資訊
    user = get_user_info(user_id)
    if not user:
        print(f"❌ 找不到用戶：{user_id}")
        return None
    
    print(f"\n👤 離職員工：{user.get('name')} ({user.get('employee_code')})")
    print(f"   部門：{user.get('department')}")
    print(f"   職稱：{user.get('title')}")
    
    # 2. 取得任務和風險
    tasks = get_user_tasks(user_id)
    risks = get_user_risks(user_id)
    reports = get_user_reports(user_id)
    
    print(f"\n📊 目前狀態：")
    print(f"   進行中任務：{len(tasks)}")
    print(f"   進行中風險：{len(risks)}")
    print(f"   歷史日報：{len(reports)}")
    
    # 3. 轉移任務
    if to_user_id and tasks:
        print(f"\n📋 轉移任務到 {to_user_id}...")
        task_count = transfer_tasks(user_id, to_user_id)
        print(f"   ✅ 已轉移 {task_count} 個任務")
    
    # 4. 轉移風險
    if to_user_id and risks:
        print(f"\n⚠️  轉移風險項目到 {to_user_id}...")
        risk_count = transfer_risks(user_id, to_user_id)
        print(f"   ✅ 已轉移 {risk_count} 個風險項目")
    
    # 5. 停用帳號
    if disable:
        print(f"\n🔒 停用帳號...")
        disable_user(user_id, reason='離職')
        print(f"   ✅ 帳號已停用")
    
    # 6. 生成交接報告
    print(f"\n📄 生成交接報告...")
    report = generate_handover_report(user_id, to_user_id)
    
    report_path = Path(f'/mnt/c/Users/YJSClaw/Documents/Openclaw/handover_reports/{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ 交接報告：{report_path}")
    
    # 7. 記錄審計日誌
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO audit_logs (
            user_id, user_name, action, category,
            details, success
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        user.get('name'),
        'RESIGNATION_PROCESS',
        'HR',
        json.dumps({
            'handover_to': to_user_id,
            'tasks_transferred': len(tasks),
            'risks_transferred': len(risks),
            'account_disabled': disable
        }, ensure_ascii=False),
        1
    ))
    conn.commit()
    conn.close()
    
    print(f"\n✅ 離職處理完成！")
    print("="*60)
    
    return report

def list_active_users():
    """列出所有啟用中的用戶"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT id, employee_code, name, department, title, role
        FROM users
        WHERE enabled = 1
        ORDER BY employee_code
    """)
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("📋 昱金生能源 - 員工離職處理腳本")
        print("用法：")
        print("  python3 process_resignation.py <離職員工 ID> [接手員工 ID]")
        print("")
        print("範例：")
        print("  python3 process_resignation.py chen_ming_de")
        print("  python3 process_resignation.py chen_ming_de wang_xiao_ming")
        print("")
        print("目前啟用中的用戶：")
        users = list_active_users()
        for u in users:
            print(f"  {u['employee_code']:15} | {u['name']:10} | {u['department']:10} | {u['role']}")
        print("")
        sys.exit(0)
    
    user_id = sys.argv[1]
    to_user_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_resignation(user_id, to_user_id)
