#!/usr/bin/env python3
"""檢查 2/25 郵件 - 版本 2"""

import imaplib
import email
from email.header import decode_header
import json
from datetime import datetime
import re

IMAP_SERVER = "mail.yjsenergy.com"
IMAP_PORT = 143
EMAIL_ACCOUNT = "johnnys"
EMAIL_PASSWORD = "Yjs0929176533cdef"

def decode_mime_words(s):
    if not s:
        return ""
    decoded = ""
    for part in decode_header(s):
        if isinstance(part[0], bytes):
            try:
                decoded += part[0].decode(part[1] or 'utf-8', errors='replace')
            except:
                decoded += part[0].decode('latin-1', errors='replace')
        else:
            decoded += part[0]
    return decoded

def parse_email_date(date_str):
    try:
        # 移除星期
        date_str = re.sub(r'^[A-Za-z]+,\s*', '', date_str)
        
        # 嘗試解析
        formats = [
            "%d %b %Y %H:%M:%S %z",
            "%d %b %Y %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                # 轉換到台灣時間 (UTC+8)
                if dt.tzinfo:
                    from datetime import timezone, timedelta
                    utc = dt.replace(tzinfo=timezone.utc)
                    tw_tz = timezone(timedelta(hours=8))
                    dt = utc.astimezone(tw_tz)
                return dt
            except:
                continue
        return None
    except:
        return None

def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                continue
            if content_type == "text/plain":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body = part.get_payload(decode=True).decode(charset, errors='replace')
                    break
                except:
                    pass
            elif content_type == "text/html":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    html = part.get_payload(decode=True).decode(charset, errors='replace')
                    body = re.sub(r'<[^>]+>', '', html)
                    break
                except:
                    pass
    else:
        try:
            charset = msg.get_content_charset() or 'utf-8'
            body = msg.get_payload(decode=True).decode(charset, errors='replace')
        except:
            body = msg.get_payload()
    return body.strip()

def analyze_email(subject, body, from_addr, date):
    analysis = {
        "subject": subject,
        "from": from_addr,
        "date": date,
        "category": "",
        "priority": "normal",
        "action_required": False,
        "key_points": [],
        "summary": ""
    }
    
    subject_lower = subject.lower()
    body_lower = body.lower()
    
    # 分類
    if any(kw in subject_lower or kw in body_lower for kw in ['投標', '標案', '得標', '招標']):
        analysis["category"] = "📋 投標相關"
        analysis["priority"] = "high"
        analysis["action_required"] = True
    elif any(kw in subject_lower or kw in body_lower for kw in ['維運', '維修', '故障', '異常']):
        analysis["category"] = "🔧 維運管理"
        analysis["priority"] = "high"
        analysis["action_required"] = True
    elif any(kw in subject_lower or kw in body_lower for kw in ['發票', '收款', '付款', '款項', '請款']):
        analysis["category"] = "💰 財務相關"
        analysis["priority"] = "normal"
        analysis["action_required"] = True
    elif any(kw in subject_lower or kw in body_lower for kw in ['合約', '契約', '協議']):
        analysis["category"] = "📄 合約文件"
        analysis["priority"] = "normal"
        analysis["action_required"] = True
    elif any(kw in subject_lower or kw in body_lower for kw in ['會議', '開會', '行程']):
        analysis["category"] = "📅 會議行程"
        analysis["priority"] = "normal"
        analysis["action_required"] = True
    elif any(kw in subject_lower or kw in body_lower for kw in ['設計', '規劃', '圖面']):
        analysis["category"] = "🏗️ 工程設計"
        analysis["priority"] = "normal"
        analysis["action_required"] = False
    elif any(kw in subject_lower or kw in body_lower for kw in ['完工', '掛表', '驗收']):
        analysis["category"] = "✅ 工程進度"
        analysis["priority"] = "high"
        analysis["action_required"] = True
    elif any(kw in subject_lower or kw in body_lower for kw in ['政府', '公標', '機關', '學校']):
        analysis["category"] = "🏛️ 政府標案"
        analysis["priority"] = "high"
        analysis["action_required"] = True
    elif '日報' in subject or '工作' in subject:
        analysis["category"] = "📝 員工日報"
        analysis["priority"] = "low"
        analysis["action_required"] = False
    else:
        analysis["category"] = "📧 一般郵件"
        analysis["priority"] = "low"
        analysis["action_required"] = False
    
    # 提取關鍵點
    if body:
        lines = body.split('\n')
        for line in lines[:30]:
            line = line.strip()
            if line and 10 < len(line) < 150:
                if any(kw in line for kw in ['完成', '進度', '確認', '注意', '重要', '待辦', '需', '已', '將']):
                    analysis["key_points"].append(line)
        analysis["summary"] = body[:500] + "..." if len(body) > 500 else body
    
    return analysis

# 連接伺服器
print("正在連接郵件伺服器...")
mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
mail.select("inbox")

# 抓取最近 100 封郵件
status, messages = mail.search(None, "ALL")
email_ids = messages[0].split()[-100:]

print(f"掃描 {len(email_ids)} 封郵件...")

feb25_emails = []
other_dates = []

for email_id in email_ids:
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    if status != "OK":
        continue
    
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            
            subject = decode_mime_words(msg.get("Subject", ""))
            from_addr = decode_mime_words(msg.get("From", ""))
            date_str = decode_mime_words(msg.get("Date", ""))
            body = get_email_body(msg)
            
            email_date = parse_email_date(date_str)
            
            if email_date:
                date_only = email_date.strftime("%Y-%m-%d")
                if date_only == "2026-02-25":
                    analysis = analyze_email(subject, body, from_addr, date_str)
                    analysis["tw_date"] = email_date.strftime("%Y-%m-%d %H:%M")
                    feb25_emails.append(analysis)
                    print(f"✓ 2/25: {subject[:60]}")
                elif date_only in ["2026-02-24", "2026-02-26", "2026-02-27"]:
                    other_dates.append(date_only)

mail.close()
mail.logout()

print(f"\n2/25 郵件數量：{len(feb25_emails)}")
print(f"其他日期分佈：{set(other_dates)}")

# 輸出結果
result = {
    "status": "success",
    "date": "2026-02-25",
    "total_count": len(feb25_emails),
    "emails": feb25_emails
}

print("\n" + "="*60)
print(json.dumps(result, ensure_ascii=False, indent=2))
