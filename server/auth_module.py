#!/usr/bin/env python3
"""
昱金生能源 - 密碼驗證與審計日誌整合模組
用於 app.py 的密碼驗證和審計日誌記錄
"""

import hashlib
import secrets
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

# 密碼政策
PASSWORD_POLICY = {
    'min_length': 8,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_digit': True,
    'require_special': True,
    'expiry_days': 90
}

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


def check_password_strength(password: str) -> tuple:
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
        return False, "密碼需包含特殊字元 (!@#$%^&*等)"
    
    return True, "密碼強度符合要求"


def log_audit(user_id: str, user_name: str, action: str, 
              category: str = None, target_type: str = None, 
              target_id: str = None, details: str = None,
              ip_address: str = None, success: bool = True, 
              error_message: str = None):
    """
    記錄審計日誌
    
    參數:
        user_id: 用戶 ID
        user_name: 用戶名稱
        action: 操作動作（LOGIN, LOGOUT, CREATE, UPDATE, DELETE 等）
        category: 分類（SECURITY, DATA, SYSTEM 等）
        target_type: 目標類型（USER, REPORT, CASE 等）
        target_id: 目標 ID
        details: 詳細資訊（JSON 字串）
        ip_address: IP 位址
        success: 是否成功
        error_message: 錯誤訊息
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO audit_logs (
                user_id, user_name, action, category, target_type, 
                target_id, details, ip_address, success, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            user_name,
            action,
            category,
            target_type,
            target_id,
            details,
            ip_address,
            1 if success else 0,
            error_message
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️  審計日誌記錄失敗：{e}")


def check_password_expiry(password_changed_at: str) -> tuple:
    """
    檢查密碼是否過期
    返回：(是否過期，剩餘天數)
    """
    if not password_changed_at:
        return True, 0  # 從未修改過，已過期
    
    try:
        changed_date = datetime.fromisoformat(password_changed_at)
        expiry_date = changed_date + timedelta(days=PASSWORD_POLICY['expiry_days'])
        days_left = (expiry_date - datetime.now()).days
        
        if days_left <= 0:
            return True, 0  # 已過期
        
        return False, days_left
    except:
        return True, 0


# 測試程式碼
if __name__ == '__main__':
    print("🔐 密碼驗證模組測試")
    print("="*50)
    
    # 測試密碼強度
    test_passwords = [
        '1234',
        'password',
        'Password1',
        'Yjs@2026',
        'Weak1!',
        'StrongP@ssw0rd!'
    ]
    
    for pwd in test_passwords:
        valid, msg = check_password_strength(pwd)
        status = "✅" if valid else "❌"
        print(f"{status} '{pwd}': {msg}")
    
    # 測試雜湊
    print("\n🔐 密碼雜湊測試")
    pwd = 'Yjs@2026'
    hashed = hash_password(pwd)
    print(f"原始密碼：{pwd}")
    print(f"雜湊結果：{hashed}")
    print(f"驗證正確：{verify_password(pwd, hashed)}")
    print(f"驗證錯誤：{verify_password('wrong', hashed)}")
