#!/usr/bin/env python3
"""
昱金生能源 - IMAP 郵件提取系統
使用正確的郵件伺服器設定
"""

import imaplib
import email
import json
from pathlib import Path
from datetime import datetime, timedelta
from email.header import decode_header
import os

# ========== 郵件伺服器設定 ==========
EMAIL_CONFIG = {
    'username': 'johnnys',
    'email': 'johnnys@yjsenergy.com',
    'password': 'Yjs0929176533cdef',
    'imap_server': 'mail.yjsenergy.com',
    'imap_port': 143,
    'smtp_server': 'mail.yjsenergy.com',
    'smtp_port': 25,
}

# 輸出目錄
OUTPUT_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/email_analysis')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def decode_mime_words(s):
    """解碼 MIME 編碼的字串"""
    if not s:
        return ''
    decoded = []
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(encoding or 'utf-8', errors='ignore'))
            except:
                decoded.append(part.decode('latin-1', errors='ignore'))
        else:
            decoded.append(part)
    return ''.join(decoded)

def connect_imap():
    """連接 IMAP 伺服器"""
    print("=" * 70)
    print("📧 昱金生能源 - IMAP 郵件提取")
    print("=" * 70)
    print(f"\n📧 帳號：{EMAIL_CONFIG['email']}")
    print(f"🌐 伺服器：{EMAIL_CONFIG['imap_server']}:{EMAIL_CONFIG['imap_port']}")
    print()
    
    try:
        # 連接伺服器
        print("🔌 連接 IMAP 伺服器...")
        mail = imaplib.IMAP4(EMAIL_CONFIG['imap_server'], EMAIL_CONFIG['imap_port'])
        
        # 登入
        print("🔑 登入...")
        mail.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
        
        print("✅ IMAP 連接成功！\n")
        return mail
        
    except Exception as e:
        print(f"❌ 連接失敗：{e}")
        return None

def fetch_emails(mail, days=30):
    """提取郵件"""
    print(f"📅 讀取範圍：過去 {days} 天")
    print()
    
    # 選擇收件匣
    mail.select('INBOX')
    
    # 計算日期
    date_from = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
    
    # 搜尋郵件
    print(f"📥 搜尋 {date_from} 之後的郵件...")
    result, data = mail.search(None, '(SINCE', date_from + ')')
    
    if result != 'OK':
        print("❌ 搜尋失敗")
        return []
    
    email_ids = data[0].split()
    print(f"✅ 找到 {len(email_ids)} 封郵件\n")
    
    emails = []
    processed = 0
    
    for eid in email_ids[:1000]:  # 限制處理 1000 封
        try:
            processed += 1
            if processed % 20 == 0:
                print(f"   已處理 {processed}/{len(email_ids)} 封...")
            
            result, msg_data = mail.fetch(eid, '(RFC822)')
            if result != 'OK':
                continue
            
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # 提取資訊
            subject = decode_mime_words(msg.get('Subject', ''))
            from_field = decode_mime_words(msg.get('From', ''))
            date_str = msg.get('Date', '')
            
            # 提取內容
            body = ''
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            body = part.get_payload(decode=True).decode('latin-1', errors='ignore')
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    body = msg.get_payload(decode=True).decode('latin-1', errors='ignore')
            
            # 檢查是否為日報
            is_daily_report = '日報' in subject or '日报' in subject or '日報' in body[:500]
            
            email_data = {
                'id': processed,
                'subject': subject,
                'from': from_field,
                'date': date_str,
                'body': body[:2000],
                'is_daily_report': is_daily_report,
                'attachments': []
            }
            
            # 處理附件
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    
                    filename = part.get_filename()
                    if filename:
                        filename = decode_mime_words(filename)
                        email_data['attachments'].append({
                            'filename': filename,
                            'size': len(part.get_payload(decode=True) or b'')
                        })
            
            emails.append(email_data)
            
            # 顯示日報或有附件的郵件
            if is_daily_report or email_data['attachments']:
                print(f"\n{'='*70}")
                print(f"📧 日報郵件 #{processed}")
                print(f"主旨：{subject}")
                print(f"寄件者：{from_field}")
                print(f"日期：{date_str}")
                if email_data['attachments']:
                    print(f"附件：{len(email_data['attachments'])} 個")
                    for att in email_data['attachments']:
                        print(f"  - {att['filename']} ({att['size']} bytes)")
        
        except Exception as e:
            print(f"⚠️ 處理郵件失敗：{e}")
            continue
    
    return emails

def save_emails(emails):
    """儲存郵件"""
    output_file = OUTPUT_DIR / f'emails_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'extracted_at': datetime.now().isoformat(),
            'total_emails': len(emails),
            'daily_reports': len([e for e in emails if e['is_daily_report']]),
            'emails': emails
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已儲存到：{output_file}")
    return output_file

def main():
    """主函數"""
    print("=" * 70)
    print("🚀 昱金生能源 - IMAP 郵件提取系統")
    print(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # 連接 IMAP
    mail = connect_imap()
    if not mail:
        return
    
    try:
        # 提取郵件
        emails = fetch_emails(mail, days=30)
        
        # 儲存結果
        if emails:
            save_emails(emails)
            
            print("\n" + "=" * 70)
            print("📊 提取總結")
            print("=" * 70)
            print(f"總郵件數：{len(emails)}")
            print(f"日報郵件：{len([e for e in emails if e['is_daily_report']])}")
            print(f"有附件：{len([e for e in emails if e['attachments']])}")
            print("=" * 70)
        else:
            print("\n⚠️  沒有找到郵件")
    
    finally:
        # 關閉連接
        mail.close()
        mail.logout()
        print("\n✅ IMAP 連接已關閉")

if __name__ == '__main__':
    main()
