#!/usr/bin/env python3
"""測試 IMAP 連線"""

import imaplib

IMAP_SERVER = "mail.yjsenergy.com"
IMAP_PORT = 143
EMAIL_PASSWORD = "Yjs0929176533cdef"

# 測試不同帳號格式
test_accounts = [
    "johnnys",
    "johnnys@yjsenergy.com",
]

for account in test_accounts:
    print(f"\n=== 測試帳號：{account} ===")
    try:
        # 不使用 STARTTLS，直接用明文連線（根據用戶設定）
        mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
        print("✓ 連線成功（無加密）")
        
        mail.login(account, EMAIL_PASSWORD)
        print(f"✓ 登入成功！帳號：{account}")
        
        mail.select("inbox")
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        print(f"✓ 郵箱中有 {len(email_ids)} 封郵件")
        
        # 讀取最近 5 封郵件
        for i, email_id in enumerate(email_ids[-5:]):
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status == "OK":
                print(f"  郵件 {i+1}: 讀取成功")
        
        mail.close()
        mail.logout()
        break
        
    except Exception as e:
        print(f"✗ 失敗：{e}")
