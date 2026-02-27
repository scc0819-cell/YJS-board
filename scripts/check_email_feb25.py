#!/usr/bin/env python3
"""
昱金生能源集團郵件檢查腳本 - 專門分析 2/25 郵件
"""

import imaplib
import email
from email.header import decode_header
import json
from datetime import datetime, timedelta
import re

# 郵件伺服器設定
IMAP_SERVER = "mail.yjsenergy.com"
IMAP_PORT = 143
EMAIL_ACCOUNT = "johnnys"
EMAIL_PASSWORD = "Yjs0929176533cdef"

def decode_mime_words(s):
    """解碼 MIME 編碼的字串"""
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
    """解析郵件日期"""
    try:
        # 常見格式：Thu, 27 Feb 2026 18:37:00 +0000
        date_str = date_str.split(',')[0]  # 移除星期
        date_str = date_str.strip()
        
        # 嘗試多種格式
        formats = [
            "%d %b %Y %H:%M:%S %z",
            "%d %b %Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        return None
    except:
        return None

def get_email_body(msg):
    """提取郵件正文"""
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
    """分析郵件內容"""
    analysis = {
        "subject": subject,
        "from": from_addr,
        "date": date,
        "summary": "",
        "category": "",
        "priority": "normal",
        "action_required": False,
        "suggestions": [],
        "key_points": []
    }
    
    subject_lower = subject.lower()
    body_lower = body.lower()
    
    # 分類邏輯
    if any(kw in subject_lower or kw in body_lower for kw in ['投標', '標案', '得標', '招標', 'bid', 'tender']):
        analysis["category"] = "📋 投標相關"
        analysis["priority"] = "high"
        analysis["action_required"] = True
    elif any(kw in subject_lower or kw in body_lower for kw in ['維運', '維修', '故障', '異常', 'maintenance']):
        analysis["category"] = "🔧 維運管理"
        analysis["priority"] = "high"
        analysis["action_required"] = True
    elif any(kw in subject_lower or kw in body_lower for kw in ['發票', '收款', '付款', '款項', '請款', 'invoice', 'payment']):
        analysis["category"] = "💰 財務相關"
        analysis["priority"] = "normal"
        analysis["action_required"] = True
    elif any(kw in subject_lower or kw in body_lower for kw in ['合約', '契約', '協議', 'contract']):
        analysis["category"] = "📄 合約文件"
        analysis["priority"] = "normal"
        analysis["action_required"] = True
    elif any(kw in subject_lower or kw in body_lower for kw in ['會議', '開會', '行程', 'meeting']):
        analysis["category"] = "📅 會議行程"
        analysis["priority"] = "normal"
        analysis["action_required"] = True
    elif any(kw in subject_lower or kw in body_lower for kw in ['設計', '規劃', '圖面', 'design']):
        analysis["category"] = "🏗️ 工程設計"
        analysis["priority"] = "normal"
        analysis["action_required"] = False
    elif any(kw in subject_lower or kw in body_lower for kw in ['完工', '掛表', '驗收', 'completion']):
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
        for line in lines[:20]:
            line = line.strip()
            if line and len(line) > 5 and len(line) < 200:
                if any(kw in line for kw in ['完成', '進度', '確認', '注意', '重要', '待辦', '需']):
                    analysis["key_points"].append(line)
        
        analysis["summary"] = body[:400] + "..." if len(body) > 400 else body
    
    return analysis

def check_feb25_emails():
    """檢查 2/25 當天的郵件"""
    try:
        print("正在連接郵件伺服器...")
        mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        print("✓ 登入成功")
        
        mail.select("inbox")
        
        # 搜尋 2/25 的郵件（使用日期範圍）
        # IMAP 日期格式：DD-Feb-YYYY
        status, messages = mail.search(None, '(ON "25-Feb-2026")')
        
        if status != "OK":
            print("搜尋失敗，改用 ALL 然後過濾")
            status, messages = mail.search(None, "ALL")
        
        email_ids = messages[0].split()
        print(f"找到 {len(email_ids)} 封郵件")
        
        feb25_emails = []
        
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
                    
                    # 解析日期
                    email_date = parse_email_date(date_str)
                    
                    # 過濾 2/25 的郵件
                    if email_date and email_date.strftime("%Y-%m-%d") == "2026-02-25":
                        analysis = analyze_email(subject, body, from_addr, date_str)
                        analysis["body_full"] = body
                        feb25_emails.append(analysis)
                        print(f"✓ 2/25: {subject[:50]}...")
        
        mail.close()
        mail.logout()
        
        # 分類統計
        stats = {}
        for e in feb25_emails:
            cat = e["category"]
            stats[cat] = stats.get(cat, 0) + 1
        
        return {
            "status": "success",
            "date": "2026-02-25",
            "total_count": len(feb25_emails),
            "stats": stats,
            "emails": feb25_emails
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "emails": []
        }

if __name__ == "__main__":
    result = check_feb25_emails()
    print("\n" + "="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
