#!/usr/bin/env python3
"""測試 IMAP 連線"""

import imaplib

IMAP_SERVER = "mail.yjsenergy.com"
IMAP_PORT = 143
EMAIL_ACCOUNT = "johnnys@yjsenergy.com"
EMAIL_PASSWORD = "Yjs0929176533cdef"

print(f"測試連線到 {IMAP_SERVER}:{IMAP_PORT}...")

try:
    # 建立連線
    mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
    print("✅ 連線成功")
    
    # 查看伺服器能力
    print(f"\n伺服器能力：{mail.capabilities}")
    
    # 嘗試登入
    print(f"\n嘗試登入帳號：{EMAIL_ACCOUNT}...")
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    print("✅ 登入成功！")
    
    # 列出信箱
    status, folders = mail.list()
    print(f"\n可用信箱：")
    for f in folders:
        print(f"  - {f}")
    
    # 選擇收件匣
    mail.select("inbox")
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()
    print(f"\n收件匣總共 {len(email_ids)} 封郵件")
    
    mail.logout()
    
except Exception as e:
    print(f"❌ 錯誤：{e}")
