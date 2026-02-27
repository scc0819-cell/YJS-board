#!/usr/bin/env python3
"""
昱金生能源集團郵件檢查腳本
連接 IMAP 伺服器讀取郵件並進行摘要分析
"""

import imaplib
import email
from email.header import decode_header
import json
from datetime import datetime, timedelta
import sys
import re

# 郵件伺服器設定
IMAP_SERVER = "mail.yjsenergy.com"
IMAP_PORT = 143  # 無加密
EMAIL_ACCOUNT = "johnnys"  # 只用帳號名稱，不用完整郵件地址
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

def get_email_body(msg):
    """提取郵件正文"""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # 跳過附件
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
                    # 簡單移除 HTML 標籤
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
    """分析郵件內容並提供摘要和建議"""
    analysis = {
        "subject": subject,
        "from": from_addr,
        "date": date,
        "summary": "",
        "category": "",
        "priority": "normal",
        "action_required": False,
        "suggestions": []
    }
    
    # 關鍵字分類
    subject_lower = subject.lower()
    body_lower = body.lower()
    
    # 分類邏輯
    if any(kw in subject_lower or kw in body_lower for kw in ['投標', '標案', '得標', '招標', 'bid', 'tender']):
        analysis["category"] = "📋 投標相關"
        analysis["priority"] = "high"
        analysis["action_required"] = True
        analysis["suggestions"].append("確認投標截止日期")
        analysis["suggestions"].append("檢視標案規格文件")
    elif any(kw in subject_lower or kw in body_lower for kw in ['維運', '維修', '故障', '異常', 'error', 'maintenance']):
        analysis["category"] = "🔧 維運管理"
        analysis["priority"] = "high"
        analysis["action_required"] = True
        analysis["suggestions"].append("安排技術人員處理")
        analysis["suggestions"].append("記錄故障原因")
    elif any(kw in subject_lower or kw in body_lower for kw in ['發票', '收款', '付款', '款項', '請款', 'invoice', 'payment']):
        analysis["category"] = "💰 財務相關"
        analysis["priority"] = "normal"
        analysis["action_required"] = True
        analysis["suggestions"].append("確認款項金額")
        analysis["suggestions"].append("安排請款或付款流程")
    elif any(kw in subject_lower or kw in body_lower for kw in ['合約', '契約', '協議', 'contract', 'agreement']):
        analysis["category"] = "📄 合約文件"
        analysis["priority"] = "normal"
        analysis["action_required"] = True
        analysis["suggestions"].append("審閱合約條款")
        analysis["suggestions"].append("確認簽約時程")
    elif any(kw in subject_lower or kw in body_lower for kw in ['會議', '開會', '行程', 'meeting', 'schedule']):
        analysis["category"] = "📅 會議行程"
        analysis["priority"] = "normal"
        analysis["action_required"] = True
        analysis["suggestions"].append("確認會議時間地點")
        analysis["suggestions"].append("準備會議資料")
    elif any(kw in subject_lower or kw in body_lower for kw in ['設計', '規劃', '圖面', 'design', 'plan']):
        analysis["category"] = "🏗️ 工程設計"
        analysis["priority"] = "normal"
        analysis["action_required"] = False
    elif any(kw in subject_lower or kw in body_lower for kw in ['完工', '掛表', '驗收', 'completion', 'inspection']):
        analysis["category"] = "✅ 工程進度"
        analysis["priority"] = "high"
        analysis["action_required"] = True
        analysis["suggestions"].append("安排驗收作業")
        analysis["suggestions"].append("確認完工文件")
    elif any(kw in subject_lower or kw in body_lower for kw in ['政府', '公標', '機關', '學校']):
        analysis["category"] = "🏛️ 政府標案"
        analysis["priority"] = "high"
        analysis["action_required"] = True
        analysis["suggestions"].append("確認標案進度")
        analysis["suggestions"].append("追蹤政府機關回覆")
    else:
        analysis["category"] = "📧 一般郵件"
        analysis["priority"] = "low"
        analysis["action_required"] = False
    
    # 生成摘要
    if body:
        # 取前 300 字作為摘要
        analysis["summary"] = body[:300] + "..." if len(body) > 300 else body
    else:
        analysis["summary"] = "(無內文)"
    
    return analysis

def check_emails(unread_only=True, limit=20):
    """檢查郵件並返回分析結果"""
    try:
        # 連接 IMAP 伺服器
        print(f"正在連接郵件伺服器：{IMAP_SERVER}:{IMAP_PORT}...")
        mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        print("✓ 登入成功")
        
        mail.select("inbox")
        
        # 搜尋郵件
        if unread_only:
            status, messages = mail.search(None, "UNSEEN")
            search_type = "未讀郵件"
        else:
            status, messages = mail.search(None, "ALL")
            search_type = "所有郵件"
        
        email_ids = messages[0].split()
        
        if not email_ids:
            print(f"✅ 沒有{search_type}")
            return {"status": "success", "search_type": search_type, "unread_count": 0, "emails": []}
        
        print(f"找到 {len(email_ids)} 封{search_type}")
        
        emails_data = []
        
        # 讀取郵件（最多 limit 封）
        fetch_count = min(limit, len(email_ids))
        for i, email_id in enumerate(email_ids[-fetch_count:]):
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # 提取資訊
                    subject = decode_mime_words(msg.get("Subject", ""))
                    from_addr = decode_mime_words(msg.get("From", ""))
                    date_str = decode_mime_words(msg.get("Date", ""))
                    body = get_email_body(msg)
                    
                    # 分析郵件
                    analysis = analyze_email(subject, body, from_addr, date_str)
                    analysis["body_preview"] = body[:500] if len(body) > 500 else body
                    emails_data.append(analysis)
                    print(f"✓ 已分析：{subject[:50]}...")
        
        mail.close()
        mail.logout()
        
        return {
            "status": "success",
            "search_type": search_type,
            "total_count": len(email_ids),
            "analyzed_count": len(emails_data),
            "emails": emails_data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "unread_count": 0,
            "emails": []
        }

if __name__ == "__main__":
    # 檢查最近郵件（包括已讀）
    result = check_emails(unread_only=False, limit=20)
    print("\n" + "="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
