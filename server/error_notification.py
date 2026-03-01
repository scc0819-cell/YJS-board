#!/usr/bin/env python3
"""
昱金生能源 - 錯誤通知系統
功能：系統錯誤時發送 Telegram/Email 通知
"""

import sqlite3
import json
import smtplib
import requests
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
CONFIG_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/config.json')

# 通知設定（可從 config.json 讀取）
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'  # 從 BotFather 取得
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'      # 管理員群組 ID
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'your_email@gmail.com'
SMTP_PASSWORD = 'your_app_password'
ALERT_EMAILS = ['admin@yjsenergy.com', 'it@yjsenergy.com']

def load_config():
    """載入設定"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def log_error_to_db(user_id, error_type, error_message, stack_trace=None):
    """記錄錯誤到資料庫"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO audit_logs (
                user_id, user_name, action, category, 
                details, success, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id or 'system',
            'System',
            'ERROR',
            'SYSTEM',
            json.dumps({
                'type': error_type,
                'stack': stack_trace
            }, ensure_ascii=False),
            0,
            error_message
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 記錄錯誤失敗：{e}")
        return False

def send_telegram_notification(title, message, severity='high'):
    """發送 Telegram 通知"""
    try:
        # 依嚴重性選擇 emoji
        emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}.get(severity, '⚠️')
        
        formatted_message = f"""
{emoji} *{title}*

{message}

📍 系統：昱金生能源日報系統
🕐 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': formatted_message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Telegram 通知已發送")
            return True
        else:
            print(f"❌ Telegram 通知失敗：{response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram 通知異常：{e}")
        return False

def send_email_notification(title, message, severity='high'):
    """發送 Email 通知"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = ', '.join(ALERT_EMAILS)
        msg['Subject'] = f"[{severity.upper()}] {title} - 昱金生能源日報系統"
        
        # Email 內容
        body = f"""
{title}

詳細資訊：
{message}

──────────────────
系統：昱金生能源日報系統
時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
嚴重性：{severity.upper()}

--
此為系統自動發送的通知，請勿回覆。
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 發送
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email 通知已發送至 {len(ALERT_EMAILS)} 個信箱")
        return True
        
    except Exception as e:
        print(f"❌ Email 通知異常：{e}")
        return False

def send_alert(error_type, error_message, user_id=None, stack_trace=None, severity='high'):
    """
    發送錯誤警報
    
    參數:
        error_type: 錯誤類型（如：Database Error, Upload Failed）
        error_message: 錯誤訊息
        user_id: 相關用戶 ID（可選）
        stack_trace: 堆疊追蹤（可選）
        severity: 嚴重性（critical/high/medium/low）
    """
    print(f"\n🚨 錯誤警報：{error_type}")
    print(f"   嚴重性：{severity}")
    print(f"   訊息：{error_message}")
    
    # 1. 記錄到資料庫
    log_error_to_db(user_id, error_type, error_message, stack_trace)
    
    # 2. 發送通知
    title = f"{error_type}"
    message = f"**錯誤類型**: {error_type}\n\n**詳細資訊**:\n{error_message}"
    
    if stack_trace:
        message += f"\n\n**堆疊追蹤**:\n```\n{stack_trace[:500]}...\n```"
    
    # 發送 Telegram
    telegram_success = send_telegram_notification(title, message, severity)
    
    # 發送 Email（僅 critical 和 high）
    email_success = False
    if severity in ['critical', 'high']:
        email_success = send_email_notification(title, message, severity)
    
    # 3. 返回結果
    success = telegram_success or email_success
    
    if success:
        print(f"✅ 警報已發送")
    else:
        print(f"❌ 警報發送失敗")
    
    return success

# ========== 整合到 Flask app.py 的範例 ==========

def setup_error_handlers(app):
    """
    設定 Flask 錯誤處理器
    
    使用方式：
    from error_notification import setup_error_handlers
    setup_error_handlers(app)
    """
    
    @app.errorhandler(404)
    def not_found(error):
        send_alert(
            error_type='404 Not Found',
            error_message=str(error),
            severity='low'
        )
        return '頁面未找到', 404
    
    @app.errorhandler(500)
    def internal_error(error):
        send_alert(
            error_type='500 Internal Server Error',
            error_message=str(error),
            severity='critical'
        )
        return '伺服器內部錯誤', 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        send_alert(
            error_type='Unhandled Exception',
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            severity='high'
        )
        return '系統錯誤', 500

# ========== 測試 ==========

if __name__ == '__main__':
    print("🧪 錯誤通知系統測試")
    print("="*50)
    
    # 測試 Telegram
    print("\n📱 測試 Telegram 通知...")
    send_telegram_notification(
        title='系統測試',
        message='這是一則測試訊息',
        severity='medium'
    )
    
    # 測試 Email
    print("\n📧 測試 Email 通知...")
    send_email_notification(
        title='系統測試',
        message='這是一則測試訊息',
        severity='medium'
    )
    
    # 測試完整警報
    print("\n🚨 測試完整警報...")
    send_alert(
        error_type='測試錯誤',
        error_message='這是一個測試錯誤訊息',
        severity='high'
    )
    
    print("\n✅ 測試完成")
