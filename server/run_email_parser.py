#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
昱金生能源 - 郵件解析系統執行腳本
帳號：johnnys@yjsenergy.com
伺服器：mail.yjsenergy.com:143
"""

import os
import sys
import json
import email
import imaplib
import base64
import re
from pathlib import Path
from datetime import datetime, timedelta
from email.header import decode_header
import chardet

# ========== 配置 ==========
EMAIL_CONFIG = {
    'user': 'johnnys@yjsenergy.com',
    'password': 'Yjs0929176533cdef',
    'server': 'mail.yjsenergy.com',
    'port': 143,
}

# 員工姓名對照表
EMPLOYEE_NAMES = {
    '宋啓綸': 'admin',
    '游若誼': 'you_ruo_yi',
    '洪淑嫆': 'hong_shu_rong',
    '楊傑麟': 'yang_jie_lin',
    '褚佩瑜': 'chu_pei_yu',
    '楊宗衛': 'yang_zong_wei',
    '張億峖': 'zhang_yi_chuan',
    '陳明德': 'chen_ming_de',
    '李雅婷': 'li_ya_ting',
    '陳谷濱': 'chen_gu_bin',
    '陳靜儒': 'chen_jing_ru',
    '林天睛': 'lin_tian_jing',
    '呂宜芹': 'lu_yi_qin',
    '顏呈晞': 'yan_cheng_xi',
    '高竹妤': 'gao_zhu_yu',
}

# 案場關鍵字
CASE_KEYWORDS = [
    '仁豐國小', '馬偕護專', '大城國小', '光復國小', '文山國小',
    '公標案', '屋頂', '停車場', '風雨球場', '光電', '太陽能'
]

# 輸出目錄
OUTPUT_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/email_analysis')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

(OUTPUT_DIR / 'attachments').mkdir(exist_ok=True)
(OUTPUT_DIR / 'ocr_results').mkdir(exist_ok=True)


def decode_mime_words(s):
    """解碼 MIME 編碼的字串"""
    if not s:
        return ''
    
    decoded = []
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(encoding or 'utf-8', errors='replace'))
            except:
                decoded.append(part.decode('utf-8', errors='replace'))
        else:
            decoded.append(part)
    return ''.join(decoded)


def get_email_body(msg):
    """提取郵件內文"""
    body = []
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition") or "")
            
            # 跳過附件
            if "attachment" in content_disposition:
                continue
            
            if content_type == "text/plain":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        body.append(payload.decode(charset, errors='replace'))
                except:
                    pass
            elif content_type == "text/html":
                # 簡單移除 HTML 標籤
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        html = payload.decode(charset, errors='replace')
                        # 移除 HTML 標籤
                        text = re.sub(r'<[^>]+>', ' ', html)
                        body.append(text)
                except:
                    pass
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            payload = msg.get_payload(decode=True)
            if payload:
                body.append(payload.decode(charset, errors='replace'))
        except:
            pass
    
    return '\n'.join(body)


def save_attachments(msg, email_id):
    """儲存並分析附件"""
    attachments = []
    
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition") or "")
        
        if "attachment" not in content_disposition:
            continue
        
        filename = part.get_filename()
        if not filename:
            continue
        
        filename = decode_mime_words(filename)
        
        # 跳過空附件
        if not filename.strip():
            continue
        
        # 儲存附件
        att_dir = OUTPUT_DIR / 'attachments' / str(datetime.now().date())
        att_dir.mkdir(parents=True, exist_ok=True)
        
        att_path = att_dir / f"{email_id}_{filename}"
        
        try:
            payload = part.get_payload(decode=True)
            if payload:
                att_path.write_bytes(payload)
                
                att_info = {
                    'filename': filename,
                    'path': str(att_path),
                    'size': len(payload),
                    'type': part.get_content_type(),
                }
                
                # 如果是圖片，標記需要 OCR
                if att_info['type'].startswith('image/'):
                    att_info['needs_ocr'] = True
                
                attachments.append(att_info)
                print(f"  📎 已儲存附件：{filename} ({len(payload)} bytes)")
        except Exception as e:
            print(f"  ⚠️  附件儲存失敗：{filename} - {e}")
    
    return attachments


def extract_case_info(text):
    """從郵件內容提取案場資訊"""
    cases = []
    
    for keyword in CASE_KEYWORDS:
        if keyword in text:
            cases.append(keyword)
    
    return list(set(cases))


def identify_sender(from_header):
    """識別寄件人"""
    from_header = decode_mime_words(from_header)
    
    # 嘗試匹配員工姓名
    for name, emp_id in EMPLOYEE_NAMES.items():
        if name in from_header or emp_id in from_header:
            return {'name': name, 'id': emp_id}
    
    # 嘗試從 email 提取
    match = re.search(r'<([^>]+)>', from_header)
    if match:
        email_addr = match.group(1)
        username = email_addr.split('@')[0]
        return {'name': username, 'email': email_addr, 'id': username}
    
    return {'name': from_header, 'id': 'unknown'}


def parse_emails(days=30):
    """解析郵件"""
    print("=" * 70)
    print("📧 昱金生能源郵件解析系統")
    print("=" * 70)
    print(f"\n📅 解析範圍：過去 {days} 天")
    print(f"👤 帳號：{EMAIL_CONFIG['user']}")
    print(f"🖥️  伺服器：{EMAIL_CONFIG['server']}:{EMAIL_CONFIG['port']}")
    print(f"📁 輸出目錄：{OUTPUT_DIR}")
    print()
    
    # 連接郵件伺服器
    print("🔌 連接郵件伺服器...")
    try:
        mail = imaplib.IMAP4(EMAIL_CONFIG['server'], EMAIL_CONFIG['port'])
        mail.login(EMAIL_CONFIG['user'], EMAIL_CONFIG['password'])
        mail.select('INBOX')
        print("✅ 連接成功！\n")
    except Exception as e:
        print(f"❌ 連接失敗：{e}")
        print("\n嘗試使用 IMAPS (port 993)...")
        try:
            mail = imaplib.IMAP4_SSL(EMAIL_CONFIG['server'], 993)
            mail.login(EMAIL_CONFIG['user'], EMAIL_CONFIG['password'])
            mail.select('INBOX')
            print("✅ IMAPS 連接成功！\n")
        except Exception as e2:
            print(f"❌ IMAPS 也失敗：{e2}")
            return
    
    # 計算日期範圍
    date_from = datetime.now() - timedelta(days=days)
    date_str = date_from.strftime('%d-%b-%Y')
    
    print(f"📅 搜尋條件：SINCE {date_str}")
    
    # 搜尋郵件
    try:
        status, messages = mail.search(None, f'(SINCE "{date_str}")')
        email_ids = messages[0].split()
        print(f"📊 找到 {len(email_ids)} 封郵件\n")
    except Exception as e:
        print(f"❌ 搜尋失敗：{e}")
        # 嘗試搜尋所有郵件
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        print(f"📊 找到所有郵件：{len(email_ids)} 封\n")
    
    # 解析每封郵件
    parsed_emails = []
    total_processed = 0
    
    for i, email_id in enumerate(email_ids):
        try:
            total_processed += 1
            if total_processed > 100:  # 限制處理數量
                print("\n⚠️  已處理 100 封郵件，暫停...")
                break
            
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # 提取基本資訊
                    subject = decode_mime_words(msg.get('Subject', ''))
                    from_header = msg.get('From', '')
                    date_header = msg.get('Date', '')
                    
                    # 識別寄件人
                    sender = identify_sender(from_header)
                    
                    # 提取內文
                    body = get_email_body(msg)
                    
                    # 提取案場資訊
                    cases = extract_case_info(subject + ' ' + body)
                    
                    # 解析附件
                    attachments = save_attachments(msg, email_id.decode())
                    
                    # 建立記錄
                    email_record = {
                        'id': email_id.decode(),
                        'date': date_header,
                        'from': sender,
                        'subject': subject,
                        'body': body[:2000],  # 限制長度
                        'cases': cases,
                        'attachments': attachments,
                        'is_daily_report': '日報' in subject or '日报' in subject,
                    }
                    
                    # 如果是日報或包含案場資訊，詳細顯示
                    if email_record['is_daily_report'] or cases:
                        print(f"\n{'='*70}")
                        print(f"📧 郵件 #{total_processed}")
                        print(f"📅 日期：{date_header}")
                        print(f"👤 寄件人：{sender['name']} ({sender.get('email', 'N/A')})")
                        print(f"📝 主旨：{subject}")
                        if cases:
                            print(f"🏭 案場：{', '.join(cases)}")
                        if attachments:
                            print(f"📎 附件：{len(attachments)} 個")
                            for att in attachments:
                                print(f"   - {att['filename']} ({att['type']}, {att['size']} bytes)")
                        print(f"📄 內文預覽：{body[:200]}...")
                    
                    parsed_emails.append(email_record)
                    
        except Exception as e:
            print(f"⚠️  解析郵件失敗：{e}")
            continue
    
    # 儲存結果
    print("\n" + "="*70)
    print("💾 儲存解析結果...")
    
    result_file = OUTPUT_DIR / f'parsed_emails_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'parse_date': datetime.now().isoformat(),
            'email_account': EMAIL_CONFIG['user'],
            'days_scanned': days,
            'total_emails': len(parsed_emails),
            'daily_reports': len([e for e in parsed_emails if e['is_daily_report']]),
            'emails_with_cases': len([e for e in parsed_emails if e['cases']]),
            'emails_with_attachments': len([e for e in parsed_emails if e['attachments']]),
            'emails': parsed_emails
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已儲存到：{result_file}")
    
    # 生成統計報告
    print("\n" + "="*70)
    print("📊 解析統計")
    print("="*70)
    print(f"總郵件數：{len(parsed_emails)}")
    print(f"日報郵件：{len([e for e in parsed_emails if e['is_daily_report']])}")
    print(f"包含案場：{len([e for e in parsed_emails if e['cases']])}")
    print(f"包含附件：{len([e for e in parsed_emails if e['attachments']])}")
    
    # 附件統計
    total_attachments = sum(len(e['attachments']) for e in parsed_emails)
    image_attachments = sum(1 for e in parsed_emails for a in e['attachments'] if a['type'].startswith('image/'))
    excel_attachments = sum(1 for e in parsed_emails for a in e['attachments'] if 'excel' in a['type'] or 'spreadsheet' in a['type'])
    word_attachments = sum(1 for e in parsed_emails for a in e['attachments'] if 'word' in a['type'])
    
    print(f"\n附件統計:")
    print(f"  總附件數：{total_attachments}")
    print(f"  圖片檔：{image_attachments}")
    print(f"  Excel 檔：{excel_attachments}")
    print(f"  Word 檔：{word_attachments}")
    
    # 案場統計
    case_count = {}
    for e in parsed_emails:
        for case in e['cases']:
            case_count[case] = case_count.get(case, 0) + 1
    
    if case_count:
        print(f"\n案場分佈:")
        for case, count in sorted(case_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {case}: {count} 封郵件")
    
    print("\n" + "="*70)
    print("✅ 郵件解析完成！")
    print("="*70)
    
    # 登出
    mail.logout()


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    parse_emails(days)
