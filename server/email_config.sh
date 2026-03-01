#!/bin/bash
# 設定郵件系統環境變數
export YJS_EMAIL_USER="johnnys@yjsenergy.com"
export YJS_EMAIL_PASS="Yjs0929176533cdef"
export YJS_EMAIL_SERVER="mail.yjsenergy.com"
export YJS_EMAIL_PORT="143"
export YJS_EMAIL_SMTP_SERVER="mail.yjsenergy.com"
export YJS_EMAIL_SMTP_PORT="25"

echo "✅ 郵件環境變數已設定"
echo "帳號：$YJS_EMAIL_USER"
echo "伺服器：$YJS_EMAIL_SERVER:$YJS_EMAIL_PORT"
