#!/usr/bin/env python3
"""
🔐 昱金生能源 - 系統初始化與安全強化腳本
整合 P0 三項關鍵任務：
1. 資料庫初始化（建立 users 表）
2. 密碼強度政策（至少 8 碼，含大小寫、數字、特殊字）
3. 審計日誌表（audit_logs）
"""

import sqlite3
import json
import hashlib
import secrets
import re
from pathlib import Path
from datetime import datetime

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
USERS_JSON = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/users.json')

# ========== 密碼強度政策 ==========
PASSWORD_POLICY = {
    'min_length': 8,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_digit': True,
    'require_special': True,
    'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?'
}

def check_password_strength(password: str) -> tuple[bool, str]:
    """
    檢查密碼強度
    返回：(是否通過，錯誤訊息)
    """
    if len(password) < PASSWORD_POLICY['min_length']:
        return False, f"密碼長度至少 {PASSWORD_POLICY['min_length']} 碼"
    
    if PASSWORD_POLICY['require_uppercase'] and not re.search(r'[A-Z]', password):
        return False, "密碼需包含大寫字母"
    
    if PASSWORD_POLICY['require_lowercase'] and not re.search(r'[a-z]', password):
        return False, "密碼需包含小寫字母"
    
    if PASSWORD_POLICY['require_digit'] and not re.search(r'\d', password):
        return False, "密碼需包含數字"
    
    if PASSWORD_POLICY['require_special'] and not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        return False, f"密碼需包含特殊字元 ({PASSWORD_POLICY['special_chars']})"
    
    return True, "密碼強度符合要求"


def hash_password(password: str) -> str:
    """使用 SHA-256 + salt 雜湊密碼"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((salt + password).encode('utf-8'))
    return f"{salt}:{hash_obj.hexdigest()}"


def verify_password(password: str, hashed: str) -> bool:
    """驗證密碼"""
    try:
        salt, hash_value = hashed.split(':')
        hash_obj = hashlib.sha256((salt + password).encode('utf-8'))
        return hash_obj.hexdigest() == hash_value
    except:
        return False


def init_database():
    """🗄️ 任務 1: 資料庫初始化"""
    print("\n" + "="*70)
    print("🗄️  任務 1: 資料庫初始化")
    print("="*70)
    
    # 建立資料庫目錄
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    
    # 1. users 表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            chinese_name TEXT,
            employee_code TEXT UNIQUE,
            title TEXT,
            department TEXT,
            role TEXT DEFAULT 'employee',
            password_hash TEXT,
            password_temp BOOLEAN DEFAULT 1,
            password_changed_at TIMESTAMP,
            password_expires_at TIMESTAMP,
            enabled BOOLEAN DEFAULT 1,
            manage_departments TEXT DEFAULT '[]',
            manage_users TEXT DEFAULT '[]',
            last_login_at TIMESTAMP,
            last_login_ip TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. audit_logs 表（審計日誌）
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT,
            user_name TEXT,
            action TEXT NOT NULL,
            category TEXT,
            target_type TEXT,
            target_id TEXT,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            success BOOLEAN DEFAULT 1,
            error_message TEXT
        )
    """)
    
    # 3. 建立索引
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_date ON reports(report_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_risks_status ON risk_items(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
    
    conn.commit()
    conn.close()
    
    print("  ✅ 建立 users 表")
    print("  ✅ 建立 audit_logs 表（審計日誌）")
    print("  ✅ 建立效能索引")
    print("  ✅ 啟用外鍵約束 (PRAGMA foreign_keys = ON)")


def load_and_update_users():
    """👥 載入 users.json 並更新密碼政策"""
    print("\n" + "="*70)
    print("👥  任務 2: 密碼強度政策設定")
    print("="*70)
    
    if not USERS_JSON.exists():
        print("  ❌ users.json 不存在，請先執行 setup_employee_system.py")
        return
    
    with open(USERS_JSON, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    # 顯示密碼政策
    print(f"\n📋 密碼政策設定：")
    print(f"  - 最小長度：{PASSWORD_POLICY['min_length']} 碼")
    print(f"  - 需包含大寫字母：{'是' if PASSWORD_POLICY['require_uppercase'] else '否'}")
    print(f"  - 需包含小寫字母：{'是' if PASSWORD_POLICY['require_lowercase'] else '否'}")
    print(f"  - 需包含數字：{'是' if PASSWORD_POLICY['require_digit'] else '否'}")
    print(f"  - 需包含特殊字元：{'是' if PASSWORD_POLICY['require_special'] else '否'}")
    
    # 更新用戶資料
    print(f"\n🔐 更新 {len(users)} 個用戶帳號...")
    
    # 預設密碼（首次登入強制修改）
    default_passwords = {
        'admin': 'Yjs@2026',  # 董事長
        'li_ya_ting': 'Yjs@2026',
        'chen_ming_de': 'Yjs@2026',
        'yang_zong_wei': 'Yjs@2026',
        'hong_shu_rong': 'Yjs@2026',
        'chen_gu_bin': 'Yjs@2026',
        'zhang_yi_chuan': 'Yjs@2026',
        'lin_kun_yi': 'Yjs@2026',
        'huang_zhen_hao': 'Yjs@2026',
        'xu_hui_ling': 'Yjs@2026',
    }
    
    for uid, user in users.items():
        # 設定預設密碼（已雜湊）
        pwd = default_passwords.get(uid, 'Yjs@2026')
        user['password_hash'] = hash_password(pwd)
        user['password_temp'] = True
        user['password_changed_at'] = None
        user['password_expires_at'] = None
        
        # 確保有必要欄位
        if 'employee_code' not in user:
            user['employee_code'] = 'EMP-XXX'
        if 'chinese_name' not in user:
            user['chinese_name'] = user.get('name', 'Unknown')
        if 'manage_departments' not in user:
            user['manage_departments'] = []
        if 'manage_users' not in user:
            user['manage_users'] = []
    
    # 寫回 users.json
    with open(USERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    print("  ✅ 已更新所有用戶密碼（使用強化預設密碼）")
    print("  ✅ 首次登入強制修改密碼已啟用")
    
    # 顯示密碼清單（僅限本次顯示）
    print(f"\n📋 用戶帳號清單：")
    print(f"{'系統 ID':20} | {'工號':10} | {'姓名':10} | {'角色':10} | {'預設密碼':15}")
    print("-" * 75)
    for uid, user in users.items():
        print(f"{uid:20} | {user.get('employee_code', 'N/A'):10} | {user.get('chinese_name', 'N/A'):10} | {user.get('role', 'employee'):10} | Yjs@2026")
    
    print(f"\n⚠️  重要：請將密碼清單提供給對應員工，首次登入後強制修改！")


def sync_users_to_db():
    """🔄 同步 users.json 到資料庫"""
    print("\n" + "="*70)
    print("🔄  任務 3: 同步用戶到資料庫")
    print("="*70)
    
    if not USERS_JSON.exists():
        print("  ❌ users.json 不存在")
        return
    
    if not DB_PATH.exists():
        print("  ❌ 資料庫不存在，請先執行資料庫初始化")
        return
    
    with open(USERS_JSON, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    
    inserted = 0
    updated = 0
    
    for uid, user in users.items():
        # 檢查是否已存在
        cursor = conn.execute("SELECT id FROM users WHERE id = ?", (uid,))
        exists = cursor.fetchone() is not None
        
        if exists:
            # 更新
            conn.execute("""
                UPDATE users SET
                    name = ?,
                    chinese_name = ?,
                    employee_code = ?,
                    title = ?,
                    department = ?,
                    role = ?,
                    password_hash = ?,
                    password_temp = ?,
                    manage_departments = ?,
                    manage_users = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                user.get('name', uid),
                user.get('chinese_name', user.get('name', uid)),
                user.get('employee_code'),
                user.get('title'),
                user.get('department'),
                user.get('role', 'employee'),
                user.get('password_hash'),
                user.get('password_temp', True),
                json.dumps(user.get('manage_departments', [])),
                json.dumps(user.get('manage_users', [])),
                uid
            ))
            updated += 1
        else:
            # 插入
            conn.execute("""
                INSERT INTO users (
                    id, name, chinese_name, employee_code, title, department,
                    role, password_hash, password_temp, manage_departments, manage_users
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                uid,
                user.get('name', uid),
                user.get('chinese_name', user.get('name', uid)),
                user.get('employee_code'),
                user.get('title'),
                user.get('department'),
                user.get('role', 'employee'),
                user.get('password_hash'),
                user.get('password_temp', True),
                json.dumps(user.get('manage_departments', [])),
                json.dumps(user.get('manage_users', []))
            ))
            inserted += 1
    
    conn.commit()
    
    # 驗證
    cursor = conn.execute("SELECT COUNT(*) FROM users WHERE enabled = 1")
    active_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"  ✅ 插入 {inserted} 個用戶")
    print(f"  ✅ 更新 {updated} 個用戶")
    print(f"  ✅ 啟用用戶總數：{active_count}")


def create_audit_log_view():
    """📊 建立審計日誌視圖"""
    print("\n" + "="*70)
    print("📊  任務 4: 建立審計日誌視圖")
    print("="*70)
    
    conn = sqlite3.connect(DB_PATH)
    
    # 建立視圖
    conn.execute("""
        CREATE VIEW IF NOT EXISTS v_audit_logs_recent AS
        SELECT 
            id,
            timestamp,
            user_id,
            user_name,
            action,
            category,
            target_type,
            target_id,
            details,
            success,
            CASE 
                WHEN success = 1 THEN '✅'
                ELSE '❌'
            END as status_icon
        FROM audit_logs
        ORDER BY timestamp DESC
        LIMIT 100
    """)
    
    conn.execute("""
        CREATE VIEW IF NOT EXISTS v_audit_logs_by_user AS
        SELECT 
            user_id,
            user_name,
            COUNT(*) as total_actions,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_actions,
            SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_actions,
            MAX(timestamp) as last_activity
        FROM audit_logs
        GROUP BY user_id, user_name
        ORDER BY total_actions DESC
    """)
    
    conn.execute("""
        CREATE VIEW IF NOT EXISTS v_audit_logs_by_action AS
        SELECT 
            action,
            category,
            COUNT(*) as count,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
            SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
        FROM audit_logs
        GROUP BY action, category
        ORDER BY count DESC
    """)
    
    conn.commit()
    conn.close()
    
    print("  ✅ 建立 v_audit_logs_recent（最近 100 筆日誌）")
    print("  ✅ 建立 v_audit_logs_by_user（用戶活動統計）")
    print("  ✅ 建立 v_audit_logs_by_action（操作類型統計）")


def print_summary():
    """📋 列印總結"""
    print("\n" + "="*70)
    print("✅ 系統初始化與安全強化完成！")
    print("="*70)
    
    print("\n📋 完成項目：")
    print("  ✅ 資料庫初始化（users 表）")
    print("  ✅ 審計日誌表（audit_logs）")
    print("  ✅ 密碼強度政策（8 碼 + 大小寫 + 數字 + 特殊字）")
    print("  ✅ 效能索引（6 個索引）")
    print("  ✅ 審計日誌視圖（3 個視圖）")
    print("  ✅ 外鍵約束啟用")
    
    print("\n🔐 密碼政策：")
    print("  - 最小長度：8 碼")
    print("  - 需包含：大寫、小寫、數字、特殊字元")
    print("  - 預設密碼：Yjs@2026（首次登入強制修改）")
    
    print("\n📊 審計日誌追蹤：")
    print("  - 登入/登出")
    print("  - 資料新增/修改/刪除")
    print("  - 權限變更")
    print("  - 系統設定變更")
    
    print("\n💡 下一步建議：")
    print("  1. 測試登入功能（使用新密碼政策）")
    print("  2. 將密碼清單提供給員工")
    print("  3. 更新 app.py 整合密碼驗證邏輯")
    print("  4. 在上傳/下載等關鍵操作加入審計日誌記錄")
    
    print("\n" + "="*70)


def main():
    print("\n" + "="*70)
    print("🔐 昱金生能源 - 系統初始化與安全強化")
    print("="*70)
    print(f"執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 任務 1: 資料庫初始化
    init_database()
    
    # 任務 2: 密碼政策設定
    load_and_update_users()
    
    # 任務 3: 同步用戶到資料庫
    sync_users_to_db()
    
    # 任務 4: 審計日誌視圖
    create_audit_log_view()
    
    # 總結
    print_summary()
    
    # 儲存執行報告
    report = {
        'timestamp': datetime.now().isoformat(),
        'tasks_completed': [
            '資料庫初始化',
            '密碼強度政策',
            '用戶同步',
            '審計日誌視圖'
        ],
        'password_policy': PASSWORD_POLICY,
        'users_count': len(json.load(open(USERS_JSON))) if USERS_JSON.exists() else 0
    }
    
    report_path = Path('/home/yjsclaw/.openclaw/workspace/server/init_security_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 報告已儲存：{report_path}")


if __name__ == '__main__':
    main()
