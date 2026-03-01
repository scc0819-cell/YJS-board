#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重設 admin 密碼為 Welcome2026!
"""

import json
import hashlib
import os
from pathlib import Path

USERS_FILE = Path('/home/yjsclaw/.openclaw/workspace/daily_report_server/data/users.json')

def hash_password(password):
    """使用 scrypt 加密密碼（與 app.py 相同邏輯）"""
    # 生成隨機 salt
    salt = os.urandom(16).hex()
    # 使用 scrypt 加密
    hash_obj = hashlib.scrypt(
        password.encode('utf-8'),
        salt=salt.encode('utf-8'),
        n=32768,
        r=8,
        p=1,
        dklen=64
    )
    hash_hex = hash_obj.hex()
    # 格式：scrypt:32768:8:1$salt$hash
    return f"scrypt:32768:8:1${salt}${hash_hex}"

def main():
    print("="*70)
    print("🔐 重設 admin 密碼")
    print("="*70)
    
    # 載入 users.json
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    # 檢查 admin 是否存在
    if 'admin' not in users:
        print("❌ admin 帳號不存在！")
        return
    
    # 重設密碼
    new_password = 'Welcome2026!'
    password_hash = hash_password(new_password)
    
    users['admin']['password_hash'] = password_hash
    users['admin']['password_temp'] = False  # 設為 false，讓用戶可以自行修改
    
    # 儲存
    tmp_file = USERS_FILE.with_suffix('.json.tmp')
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    tmp_file.replace(USERS_FILE)
    
    print(f"✅ admin 密碼已重設為：{new_password}")
    print(f"\n📁 檔案：{USERS_FILE}")
    
    # 驗證
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    print(f"\n✅ admin 帳號資訊:")
    print(f"   ID: {users['admin']['id']}")
    print(f"   姓名：{users['admin']['name']}")
    print(f"   角色：{users['admin']['role']}")
    print(f"   密碼臨時：{users['admin']['password_temp']}")
    print(f"   啟用：{users['admin']['enabled']}")
    
    print("\n" + "="*70)
    print("✅ 密碼重設完成！")
    print("="*70)
    print("\n🌐 立即登入：http://localhost:5000")
    print("   帳號：admin")
    print("   密碼：Welcome2026!")
    print("="*70)

if __name__ == "__main__":
    main()
