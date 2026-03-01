#!/usr/bin/env python3
"""
昱金生能源 - 郵件分析系統
功能：
1. 掃描 Outlook 郵箱（在職員工 + 江勇毅的郵件）
2. 分析郵件內容，提取案場資訊
3. 建立案場脈絡資料庫
4. 生成 AI 記憶摘要
5. 主動要求員工補充資訊
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3

# ========== 配置 ==========
EMAIL_ACCOUNTS = {
    'outlook': {
        'server': 'outlook.office365.com',
        'port': 993,
        'username': os.environ.get('YJS_EMAIL_USER', ''),
        'password': os.environ.get('YJS_EMAIL_PASS', ''),
    }
}

# 在職員工清單（從人事資料表）
ACTIVE_EMPLOYEES = {
    '宋啓綸': 'admin',
    '李雅婷': 'li_ya_ting',
    '陳明德': 'chen_ming_de',
    '楊宗衛': 'yang_zong_wei',
    '洪淑嫆': 'hong_shu_rong',
    '陳谷濱': 'chen_gu_bin',
    '張億峖': 'zhang_yi_chuan',
    '林坤誼': 'lin_kun_yi',
    '黃振豪': 'huang_zhen_hao',
    '許惠玲': 'xu_hui_ling',
}

# 已離職員工（仍需分析其歷史郵件）
FORMER_EMPLOYEES = {
    '江勇毅': 'jiang_yong_yi',
}

# 案場關鍵字（用於識別郵件中的案場名稱）
CASE_KEYWORDS = [
    '仁豐國小', '馬偕護專', '大城國小', '光復國小', '文山國小',
    # 可從 cases 表動態載入
]

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
EMAIL_ANALYSIS_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/email_analysis')


class EmailAnalyzer:
    """郵件分析器"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.analysis_dir = EMAIL_ANALYSIS_DIR
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # 員工郵件對照表
        self.employee_emails = {}
        for name, emp_id in ACTIVE_EMPLOYEES.items():
            # 假設 email 格式：name@yjsenergy.com
            self.employee_emails[f"{name}@yjsenergy.com"] = emp_id
            self.employee_emails[name] = emp_id
        
        for name, emp_id in FORMER_EMPLOYEES.items():
            self.employee_emails[f"{name}@yjsenergy.com"] = emp_id
            self.employee_emails[name] = emp_id
    
    def connect_outlook(self):
        """連接 Outlook 郵箱"""
        try:
            import imaplib
            import email
            from email.header import decode_header
            
            config = EMAIL_ACCOUNTS['outlook']
            
            if not config['username'] or not config['password']:
                print("⚠️  未設定郵箱帳號密碼，使用模擬模式")
                return None
            
            mail = imaplib.IMAP4_SSL(config['server'], config['port'])
            mail.login(config['username'], config['password'])
            mail.select('INBOX')
            
            print(f"✅ 已連接 Outlook 郵箱：{config['username']}")
            return mail
            
        except Exception as e:
            print(f"❌ 連接郵箱失敗：{e}")
            return None
    
    def fetch_emails(self, mail, days=365):
        """抓取指定天數內的郵件"""
        emails = []
        
        if mail is None:
            # 模擬模式
            print("📧 使用模擬郵件資料（測試用）")
            return self._generate_sample_emails()
        
        try:
            # 計算日期範圍
            since_date = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
            
            # 搜尋收件夾
            status, messages = mail.search(None, f'(SINCE {since_date})')
            
            if status != 'OK':
                print("❌ 搜尋郵件失敗")
                return emails
            
            email_ids = messages[0].split()
            print(f"📬 找到 {len(email_ids)} 封郵件")
            
            for eid in email_ids[:500]:  # 限制最多 500 封
                status, msg_data = mail.fetch(eid, '(RFC822)')
                if status != 'OK':
                    continue
                
                raw_email = msg_data[0][1]
                parsed = self._parse_email(raw_email)
                
                if parsed:
                    emails.append(parsed)
            
            return emails
            
        except Exception as e:
            print(f"❌ 抓取郵件失敗：{e}")
            return emails
    
    def _parse_email(self, raw_email):
        """解析原始郵件"""
        try:
            from email.header import decode_header
            
            msg = email.message_from_bytes(raw_email)
            
            # 寄件者
            sender = self._decode_header(msg.get('From'))
            
            # 收件者
            recipient = self._decode_header(msg.get('To'))
            
            # 主旨
            subject = self._decode_header(msg.get('Subject'))
            
            # 日期
            date_str = msg.get('Date')
            date = self._parse_date(date_str)
            
            # 內容
            body = ''
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass
            
            # 識別員工
            employee_id = self._identify_employee(sender)
            
            # 識別案場
            cases = self._identify_cases(subject + ' ' + body)
            
            return {
                'sender': sender,
                'recipient': recipient,
                'subject': subject,
                'date': date,
                'body': body,
                'employee_id': employee_id,
                'cases': cases,
                'has_attachment': len(msg.get_payload()) > 1 if msg.is_multipart() else False
            }
            
        except Exception as e:
            print(f"❌ 解析郵件失敗：{e}")
            return None
    
    def _decode_header(self, header):
        """解碼郵件標頭"""
        if not header:
            return ''
        
        decoded = decode_header(header)
        result = ''
        for text, encoding in decoded:
            if isinstance(text, bytes):
                try:
                    result += text.decode(encoding or 'utf-8')
                except:
                    result += text.decode('utf-8', errors='ignore')
            else:
                result += str(text)
        return result
    
    def _parse_date(self, date_str):
        """解析日期"""
        if not date_str:
            return datetime.now()
        
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _identify_employee(self, sender):
        """識別寄件員工"""
        for email_addr, emp_id in self.employee_emails.items():
            if email_addr in sender or sender in email_addr:
                return emp_id
        return None
    
    def _identify_cases(self, text):
        """識別案場名稱"""
        found_cases = []
        
        # 從資料庫載入案場清單
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute('SELECT case_id, name FROM cases')
            cases = cursor.fetchall()
            conn.close()
            
            for case_id, name in cases:
                if name in text:
                    found_cases.append({
                        'case_id': case_id,
                        'name': name
                    })
        except:
            pass
        
        return found_cases
    
    def _generate_sample_emails(self):
        """生成模擬郵件（測試用）"""
        now = datetime.now()
        
        samples = [
            {
                'sender': '楊宗衛',
                'subject': '仁豐國小案場進度回報 - 2026/02',
                'date': (now - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S'),
                'body': '''
宋董您好，

仁豐國小案場目前進度如下：

1. 光電板安裝：已完成 80%
2. 變流器安裝：預計下週開始
3. 併聯申請：已送件，等待台電審查

問題：
- 現場施工空間不足，需要協調
- 天氣影響，進度落後 3 天

楊宗衛 敬上
                ''',
                'employee_id': 'yang_zong_wei',
                'cases': [{'case_id': 'RF001', 'name': '仁豐國小'}]
            },
            {
                'sender': '陳谷濱',
                'subject': '馬偕護專案 - 財務請款進度',
                'date': (now - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
                'body': '''
董事長，

馬偕護專案請款進度：

1. 第一期請款：已核銷完成
2. 第二期請款：單據整理中，預計本週送出
3. 第三期請款：待完工後申請

注意：
- 廠商發票有誤，已退回重開
- 需要宋董簽章文件已備妥

陳谷濱 敬上
                ''',
                'employee_id': 'chen_gu_bin',
                'cases': [{'case_id': 'MS001', 'name': '馬偕護專'}]
            },
            {
                'sender': '江勇毅',
                'subject': '大城國小案場 - 施工日誌 2025/12',
                'date': (now - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S'),
                'body': '''
宋董，

大城國小案場施工日誌：

12/01：基礎工程開始
12/05：支架安裝完成 50%
12/10：光電板進場
12/15：因雨天暫停施工
12/20：恢復施工

問題記錄：
- 12/08 發現地下管線，需變更設計
- 12/12 廠商延遲交貨

江勇毅 敬上
                ''',
                'employee_id': 'jiang_yong_yi',
                'cases': [{'case_id': 'DC001', 'name': '大城國小'}]
            },
        ]
        
        return samples
    
    def analyze_emails(self, emails):
        """分析郵件內容"""
        print(f"\n📊 開始分析 {len(emails)} 封郵件...\n")
        
        analysis = {
            'total_emails': len(emails),
            'by_employee': defaultdict(list),
            'by_case': defaultdict(list),
            'timeline': [],
            'key_events': [],
            'pending_questions': []
        }
        
        for email_data in emails:
            if not email_data:
                continue
            
            emp_id = email_data.get('employee_id')
            cases = email_data.get('cases', [])
            
            # 依員工分類
            if emp_id:
                analysis['by_employee'][emp_id].append(email_data)
            
            # 以案場分類
            for case in cases:
                case_id = case['case_id']
                analysis['by_case'][case_id].append(email_data)
                
                # 提取關鍵事件
                event = self._extract_event(email_data, case)
                if event:
                    analysis['key_events'].append(event)
            
            # 建立時間軸
            analysis['timeline'].append({
                'date': email_data['date'],
                'employee': emp_id,
                'subject': email_data['subject'],
                'cases': [c['name'] for c in cases]
            })
        
        # 識別待補充資訊
        analysis['pending_questions'] = self._identify_pending_questions(analysis)
        
        return analysis
    
    def _extract_event(self, email_data, case):
        """從郵件提取事件"""
        body = email_data.get('body', '')
        subject = email_data.get('subject', '')
        
        # 關鍵事件類型
        event_types = {
            'progress': ['完成', '進度', '%'],
            'issue': ['問題', '困難', '需要'],
            'milestone': ['開始', '完工', '掛表', '併聯'],
            'finance': ['請款', '核銷', '發票'],
            'risk': ['延遲', '影響', '風險']
        }
        
        detected_type = 'general'
        for event_type, keywords in event_types.items():
            for kw in keywords:
                if kw in body or kw in subject:
                    detected_type = event_type
                    break
        
        return {
            'date': email_data['date'],
            'case_id': case['case_id'],
            'case_name': case['name'],
            'employee_id': email_data.get('employee_id'),
            'type': detected_type,
            'summary': subject,
            'details': body[:500]  # 限制長度
        }
    
    def _identify_pending_questions(self, analysis):
        """識別需要員工補充的資訊"""
        questions = []
        
        # 檢查每個案場
        for case_id, emails in analysis['by_case'].items():
            # 檢查是否有未解決的問題
            for email_data in emails:
                body = email_data.get('body', '').lower()
                
                if '問題' in body or '需要' in body:
                    # 檢查是否有後續跟進
                    if '已解決' not in body and '完成' not in body:
                        questions.append({
                            'case_id': case_id,
                            'employee_id': email_data.get('employee_id'),
                            'question': f'「{email_data.get("subject")}」中提到的問題是否已解決？',
                            'date': email_data['date']
                        })
        
        return questions[:20]  # 限制數量
    
    def save_analysis(self, analysis):
        """儲存分析結果"""
        # 儲存 JSON
        json_path = self.analysis_dir / 'email_analysis.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        # 寫入資料庫
        self._save_to_database(analysis)
        
        # 生成摘要報告
        self._generate_summary(analysis)
        
        print(f"\n✅ 分析結果已儲存至：{self.analysis_dir}")
    
    def _save_to_database(self, analysis):
        """寫入資料庫"""
        conn = sqlite3.connect(self.db_path)
        
        # 建立郵件分析表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS email_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_date TEXT,
                sender TEXT,
                subject TEXT,
                employee_id TEXT,
                case_id TEXT,
                event_type TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入關鍵事件
        for event in analysis.get('key_events', []):
            conn.execute('''
                INSERT INTO email_analysis 
                (email_date, sender, subject, employee_id, case_id, event_type, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event['date'],
                event.get('employee_id', ''),
                event['summary'],
                event['employee_id'],
                event['case_id'],
                event['type'],
                event['details'][:1000]
            ))
        
        conn.commit()
        conn.close()
        
        print(f"  ✅ 已寫入 {len(analysis.get('key_events', []))} 筆事件至資料庫")
    
    def _generate_summary(self, analysis):
        """生成摘要報告"""
        summary_path = self.analysis_dir / 'analysis_summary.md'
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# 📧 郵件分析摘要報告\n\n")
            f.write(f"**分析時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(f"**總郵件數**: {analysis['total_emails']}\n\n")
            
            # 依員工統計
            f.write("## 📊 依員工統計\n\n")
            for emp_id, emails in analysis['by_employee'].items():
                name = ACTIVE_EMPLOYEES.get(emp_id, FORMER_EMPLOYEES.get(emp_id, emp_id))
                f.write(f"- **{name}**: {len(emails)} 封\n")
            
            # 依案場統計
            f.write("\n## 🏭 依案場統計\n\n")
            for case_id, emails in analysis['by_case'].items():
                case_name = emails[0]['cases'][0]['name'] if emails else case_id
                f.write(f"- **{case_name}**: {len(emails)} 封\n")
            
            # 關鍵事件
            f.write("\n## ⚡ 關鍵事件（最近 20 筆）\n\n")
            for event in analysis['key_events'][-20:]:
                f.write(f"- {event['date']} | {event['case_name']} | {event['type']} | {event['summary']}\n")
            
            # 待補充資訊
            f.write("\n## ❓ 需要員工補充的資訊\n\n")
            for q in analysis['pending_questions'][:10]:
                emp_name = ACTIVE_EMPLOYEES.get(q['employee_id'], q['employee_id'])
                f.write(f"- **{emp_name}**: {q['question']}\n")
        
        print(f"  ✅ 已生成摘要報告：{summary_path}")
    
    def run(self, days=365):
        """執行完整分析流程"""
        print("="*60)
        print("📧 昱金生能源 - 郵件分析系統")
        print("="*60)
        
        # 連接郵箱
        mail = self.connect_outlook()
        
        # 抓取郵件
        emails = self.fetch_emails(mail, days)
        
        # 分析郵件
        analysis = self.analyze_emails(emails)
        
        # 儲存結果
        self.save_analysis(analysis)
        
        # 生成 AI 記憶注入
        self._generate_ai_memory(analysis)
        
        # 生成員工補充請求
        self._generate_employee_requests(analysis)
        
        print("\n" + "="*60)
        print("✅ 郵件分析完成！")
        print("="*60)
        
        return analysis
    
    def _generate_ai_memory(self, analysis):
        """生成 AI 記憶注入"""
        memory_path = self.analysis_dir / 'ai_memory_injection.md'
        
        with open(memory_path, 'w', encoding='utf-8') as f:
            f.write("# 🧠 AI 記憶注入 - 案場脈絡\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("> 這些資訊已從歷史郵件提取，用於 AI 快速理解案場脈絡\n\n")
            
            # 每個案場的完整脈絡
            for case_id, emails in analysis['by_case'].items():
                case_name = emails[0]['cases'][0]['name'] if emails else case_id
                
                f.write(f"## 🏭 {case_name}\n\n")
                
                # 時間軸
                f.write("### 時間軸\n\n")
                sorted_emails = sorted(emails, key=lambda x: x['date'])
                for email in sorted_emails:
                    f.write(f"- **{email['date']}**: {email['subject']} ({email.get('employee_id', '未知')})\n")
                
                # 關鍵事件
                f.write("\n### 關鍵事件\n\n")
                case_events = [e for e in analysis['key_events'] if e['case_id'] == case_id]
                for event in case_events:
                    f.write(f"- {event['date']} [{event['type']}]: {event['summary']}\n")
                
                # 待解決問題
                f.write("\n### 待解決問題\n\n")
                case_questions = [q for q in analysis['pending_questions'] if q['case_id'] == case_id]
                if case_questions:
                    for q in case_questions:
                        f.write(f"- ❓ {q['question']}\n")
                else:
                    f.write("- ✅ 無待解決問題\n")
                
                f.write("\n---\n\n")
        
        print(f"  ✅ 已生成 AI 記憶注入：{memory_path}")
    
    def _generate_employee_requests(self, analysis):
        """生成員工補充請求（含董事長副本通知）"""
        request_path = self.analysis_dir / 'employee_requests.md'
        chairman_copy_path = self.analysis_dir / 'chairman_copy.md'
        
        # 依員工分組
        by_employee = defaultdict(list)
        for q in analysis['pending_questions']:
            by_employee[q['employee_id']].append(q)
        
        # 員工請求文件
        with open(request_path, 'w', encoding='utf-8') as f:
            f.write("# 📬 員工資訊補充請求\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("> 以下問題需要相關員工補充資訊，以完善 AI 記憶\n\n")
            f.write("**請注意**：本請求已副本通知董事長\n\n")
            
            for emp_id, questions in by_employee.items():
                emp_name = ACTIVE_EMPLOYEES.get(emp_id, FORMER_EMPLOYEES.get(emp_id, emp_id))
                f.write(f"## 👤 {emp_name}\n\n")
                
                for i, q in enumerate(questions, 1):
                    f.write(f"### {i}. {q['question']}\n")
                    f.write(f"- **案場**: {q.get('case_id', 'N/A')}\n")
                    f.write(f"- **來源郵件**: {q.get('subject', 'N/A')}\n")
                    f.write(f"- **日期**: {q.get('date', 'N/A')}\n")
                    f.write(f"- **狀態**: ⏳ 等待員工回覆\n")
                    f.write(f"- **董事長判斷**: ⏳ 待確認\n")
                    f.write(f"- **期限**: {q.get('due_date', '3 天內')}\n\n")
        
        # 董事長副本通知
        with open(chairman_copy_path, 'w', encoding='utf-8') as f:
            f.write("# 📋 員工補充請求 - 董事長副本通知\n\n")
            f.write(f"**通知時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("> 以下補充請求已發送給員工，請您審閱是否需要。\n")
            f.write("> - 如您判斷**不需要**：請回覆「不需要」，AI 將僅當作知識記憶\n")
            f.write("> - 如您判斷**需要**：請回覆「需要」，AI 將追蹤員工回覆\n")
            f.write("> - 如員工**逾期未回覆**：AI 將提醒您協助要求\n\n")
            
            total_questions = len(analysis['pending_questions'])
            f.write(f"**總計**: {total_questions} 個問題需要員工補充\n\n")
            
            for emp_id, questions in by_employee.items():
                emp_name = ACTIVE_EMPLOYEES.get(emp_id, FORMER_EMPLOYEES.get(emp_id, emp_id))
                f.write(f"## 👤 {emp_name} ({len(questions)} 個問題)\n\n")
                
                for i, q in enumerate(questions, 1):
                    f.write(f"{i}. **{q['question']}**\n")
                    f.write(f"   - 案場：{q.get('case_id', 'N/A')}\n")
                    f.write(f"   - 來源：{q.get('subject', 'N/A')}\n")
                    f.write(f"   - 期限：{q.get('due_date', '3 天內')}\n")
                    f.write(f"   - 您的回覆：[需要 / 不需要]\n\n")
        
        print(f"  ✅ 已生成員工補充請求：{request_path}")
        print(f"  ✅ 已生成董事長副本通知：{chairman_copy_path}")


if __name__ == '__main__':
    import sys
    
    analyzer = EmailAnalyzer()
    
    # 分析天數（預設 365 天）
    days = 365
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except:
            pass
    
    # 執行分析
    analysis = analyzer.run(days)
    
    print(f"\n📊 分析摘要:")
    print(f"  總郵件數：{analysis['total_emails']}")
    print(f"  員工人數：{len(analysis['by_employee'])}")
    print(f"  案場數量：{len(analysis['by_case'])}")
    print(f"  關鍵事件：{len(analysis['key_events'])}")
    print(f"  待補充問題：{len(analysis['pending_questions'])}")
