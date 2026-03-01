#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
昱金生能源 - 郵件完整解析系統
執行：完整解析所有郵件 + 建立案場資料庫 + 員工績效分析 + 生成報告
"""

import imaplib
import email
import json
import ssl
import re
from email.header import decode_header
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import openpyxl
from docx import Document

# ========== 配置 ==========
EMAIL_CONFIG = {
    'user': 'johnnys',
    'password': 'Yjs0929176533cdef',
    'server': 'mail.yjsenergy.com',
    'port': 143,
}

OUTPUT_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/full_email_analysis')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 員工姓名對照
EMPLOYEE_MAP = {
    'YJS_呂宜芹': {'name': '呂宜芹', 'id': 'lu_yi_qin', 'dept': '行政部'},
    'YJS_陳谷濱': {'name': '陳谷濱', 'id': 'chen_gu_bin', 'dept': '工程部'},
    'YJS_林玉凰': {'name': '林玉凰', 'id': 'lin_yu_huang', 'dept': '未知'},
    'YJS_楊宗衛': {'name': '楊宗衛', 'id': 'yang_zong_wei', 'dept': '工程部'},
    'YJS_張億峖': {'name': '張億峖', 'id': 'zhang_yi_chuan', 'dept': '工程部'},
    'YJS_陳明德': {'name': '陳明德', 'id': 'chen_ming_de', 'dept': '工程部'},
    'YJS_陳靜儒': {'name': '陳靜儒', 'id': 'chen_jing_ru', 'dept': '維運部'},
    'YJS_林天睛': {'name': '林天睛', 'id': 'lin_tian_jing', 'dept': '行政部'},
    'YJS_顏呈晞': {'name': '顏呈晞', 'id': 'yan_cheng_xi', 'dept': '設計部'},
    'YJS_高竹妤': {'name': '高竹妤', 'id': 'gao_zhu_yu', 'dept': '設計部'},
}

# 案場關鍵字
CASE_PATTERNS = [
    r'(\d+-\d+)',  # 案場編號如 12-1
    r'(仁豐國小 | 馬偕護專 | 大城國小 | 光復國小 | 文山國小)',
    r'(新庄國小 | 漢寶國小 | 中正國小 | 鳳霞國小 | 西港國小)',
    r'(村東國小 | 大園 | 竹塘 | 線西國中 | 線西國小)',
    r'(高雄仁愛之家 | 金田畜牧場 | 草屯 | 彰化)',
    r'(彰化縣公有學校聯合標租案)',
]


def decode_mime_words(s):
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


def extract_cases(text):
    """從文字提取案場資訊"""
    cases = []
    for pattern in CASE_PATTERNS:
        matches = re.findall(pattern, text)
        cases.extend(matches)
    return list(set(cases))


def connect_mail():
    """連接郵件伺服器"""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    mail = imaplib.IMAP4(EMAIL_CONFIG['server'], EMAIL_CONFIG['port'])
    mail.starttls(ssl_context=ssl_context)
    mail.login(EMAIL_CONFIG['user'], EMAIL_CONFIG['password'])
    mail.select('INBOX')
    return mail


def parse_all_emails(mail):
    """解析所有郵件"""
    print("="*70)
    print("📧 開始解析所有郵件")
    print("="*70)
    
    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split()
    total = len(email_ids)
    
    print(f"📊 總郵件數：{total} 封\n")
    
    all_emails = []
    daily_reports = []
    employee_emails = defaultdict(list)
    case_emails = defaultdict(list)
    
    for i, email_id in enumerate(email_ids):
        try:
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # 基本資訊
                    subject_raw = msg.get('Subject', '')
                    subject = decode_mime_words(subject_raw)
                    
                    from_raw = msg.get('From', '')
                    from_name = decode_mime_words(from_raw)
                    
                    date_raw = msg.get('Date', '')
                    
                    # 提取內文
                    body = ''
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                try:
                                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')[:2000]
                                except:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode('utf-8', errors='replace')[:2000]
                        except:
                            pass
                    
                    # 附件
                    attachments = []
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_disposition() == 'attachment':
                                filename = part.get_filename()
                                if filename:
                                    filename = decode_mime_words(filename)
                                    attachments.append(filename)
                    
                    # 判斷日報
                    is_daily = '日報' in subject or '日报' in subject or '工作日報' in subject
                    
                    # 提取案場
                    cases = extract_cases(subject + ' ' + body)
                    
                    # 識別員工
                    emp_key = None
                    for key in EMPLOYEE_MAP.keys():
                        if key in from_name:
                            emp_key = key
                            break
                    
                    email_data = {
                        'id': email_id.decode(),
                        'subject': subject,
                        'from': from_name,
                        'employee_key': emp_key,
                        'date': date_raw,
                        'body': body[:500],
                        'attachments': attachments,
                        'is_daily_report': is_daily,
                        'cases': cases,
                    }
                    
                    all_emails.append(email_data)
                    
                    if is_daily:
                        daily_reports.append(email_data)
                    
                    if emp_key:
                        employee_emails[emp_key].append(email_data)
                    
                    for case in cases:
                        case_emails[case].append(email_data)
                    
                    # 進度顯示
                    if (i + 1) % 500 == 0:
                        print(f"  已處理：{i+1}/{total} 封")
        
        except Exception as e:
            continue
    
    return {
        'total': total,
        'all_emails': all_emails,
        'daily_reports': daily_reports,
        'employee_emails': dict(employee_emails),
        'case_emails': dict(case_emails),
    }


def analyze_employee_performance(data):
    """員工績效分析"""
    print("\n" + "="*70)
    print("👥 員工績效分析")
    print("="*70)
    
    performance = {}
    
    for emp_key, emails in data['employee_emails'].items():
        emp_info = EMPLOYEE_MAP.get(emp_key, {'name': emp_key, 'dept': '未知'})
        
        daily_count = sum(1 for e in emails if e['is_daily_report'])
        att_count = sum(len(e['attachments']) for e in emails)
        cases = set()
        for e in emails:
            cases.update(e['cases'])
        
        # 日期範圍
        dates = [e['date'] for e in emails if e['date']]
        
        performance[emp_key] = {
            'name': emp_info.get('name', emp_key),
            'dept': emp_info.get('dept', '未知'),
            'total_emails': len(emails),
            'daily_reports': daily_count,
            'attachments': att_count,
            'cases': list(cases),
            'case_count': len(cases),
        }
    
    # 排序
    sorted_perf = sorted(performance.values(), key=lambda x: x['total_emails'], reverse=True)
    
    for emp in sorted_perf:
        print(f"\n📋 {emp['name']} ({emp['dept']})")
        print(f"   總郵件：{emp['total_emails']} 封")
        print(f"   日報：{emp['daily_reports']} 封")
        print(f"   附件：{emp['attachments']} 個")
        print(f"   負責案場：{emp['case_count']} 個")
        if emp['cases'][:5]:
            print(f"   主要案場：{', '.join(emp['cases'][:5])}")
    
    return performance


def analyze_cases(data):
    """案場分析"""
    print("\n" + "="*70)
    print("🏭 案場分析")
    print("="*70)
    
    case_stats = {}
    
    for case, emails in data['case_emails'].items():
        daily_count = sum(1 for e in emails if e['is_daily_report'])
        employees = set()
        for e in emails:
            if e['employee_key']:
                emp_info = EMPLOYEE_MAP.get(e['employee_key'], {})
                employees.add(emp_info.get('name', e['from']))
        
        case_stats[case] = {
            'name': case,
            'total_emails': len(emails),
            'daily_reports': daily_count,
            'employees': list(employees),
            'employee_count': len(employees),
        }
    
    # 排序
    sorted_cases = sorted(case_stats.values(), key=lambda x: x['total_emails'], reverse=True)
    
    print(f"\n📊 總案場數：{len(sorted_cases)} 個\n")
    
    for i, case in enumerate(sorted_cases[:20], 1):
        print(f"  {i}. {case['name']}")
        print(f"     郵件：{case['total_emails']} 封 | 日報：{case['daily_reports']} 封 | 負責人：{case['employee_count']} 位")
    
    return case_stats


def generate_report(data, performance, cases):
    """生成完整報告"""
    print("\n" + "="*70)
    print("📊 生成完整報告")
    print("="*70)
    
    report = {
        'report_date': datetime.now().isoformat(),
        'summary': {
            'total_emails': data['total'],
            'parsed_emails': len(data['all_emails']),
            'daily_reports': len(data['daily_reports']),
            'total_employees': len(data['employee_emails']),
            'total_cases': len(data['case_emails']),
        },
        'employee_performance': performance,
        'case_analysis': cases,
        'daily_reports_sample': data['daily_reports'][:20],
    }
    
    # 儲存報告
    report_file = OUTPUT_DIR / f'full_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 報告已儲存：{report_file}")
    
    # 生成文字摘要
    summary_file = OUTPUT_DIR / f'analysis_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("昱金生能源郵件完整解析報告\n")
        f.write("="*70 + "\n\n")
        f.write(f"解析時間：{report['report_date']}\n\n")
        
        f.write("📊 總覽\n")
        f.write("-"*50 + "\n")
        f.write(f"總郵件數：{report['summary']['total_emails']} 封\n")
        f.write(f"解析郵件：{report['summary']['parsed_emails']} 封\n")
        f.write(f"日報郵件：{report['summary']['daily_reports']} 封\n")
        f.write(f"員工總數：{report['summary']['total_employees']} 位\n")
        f.write(f"案場總數：{report['summary']['total_cases']} 個\n\n")
        
        f.write("👥 員工績效排行\n")
        f.write("-"*50 + "\n")
        sorted_emp = sorted(performance.values(), key=lambda x: x['total_emails'], reverse=True)
        for i, emp in enumerate(sorted_emp, 1):
            f.write(f"{i}. {emp['name']} ({emp['dept']})\n")
            f.write(f"   郵件：{emp['total_emails']} | 日報：{emp['daily_reports']} | 案場：{emp['case_count']}\n")
        
        f.write("\n🏭 案場排行（前 20）\n")
        f.write("-"*50 + "\n")
        sorted_cases = sorted(cases.values(), key=lambda x: x['total_emails'], reverse=True)
        for i, case in enumerate(sorted_cases[:20], 1):
            f.write(f"{i}. {case['name']}\n")
            f.write(f"   郵件：{case['total_emails']} | 日報：{case['daily_reports']} | 負責人：{case['employee_count']}\n")
    
    print(f"✅ 摘要已儲存：{summary_file}")
    
    return report


def main():
    """主函數"""
    print("="*70)
    print("昱金生能源 - 郵件完整解析系統")
    print("="*70)
    print(f"\n開始時間：{datetime.now().isoformat()}")
    print(f"輸出目錄：{OUTPUT_DIR}\n")
    
    try:
        # 1. 連接郵件
        print("🔌 連接郵件伺服器...")
        mail = connect_mail()
        print("✅ 連接成功！\n")
        
        # 2. 解析所有郵件
        data = parse_all_emails(mail)
        
        # 3. 員工績效分析
        performance = analyze_employee_performance(data)
        
        # 4. 案場分析
        cases = analyze_cases(data)
        
        # 5. 生成報告
        report = generate_report(data, performance, cases)
        
        # 6. 建立案場資料庫
        print("\n" + "="*70)
        print("🏭 建立案場資料庫")
        print("="*70)
        
        case_db = {}
        for case, emails in data['case_emails'].items():
            case_db[case] = {
                'timeline': [],
                'employees': set(),
                'issues': [],
                'progress': [],
            }
            
            for e in emails:
                case_db[case]['timeline'].append({
                    'date': e['date'],
                    'subject': e['subject'],
                    'from': e['from'],
                    'is_daily': e['is_daily_report'],
                })
                
                if e['employee_key']:
                    emp_info = EMPLOYEE_MAP.get(e['employee_key'], {})
                    case_db[case]['employees'].add(emp_info.get('name', e['from']))
                
                # 提取問題
                if '問題' in e['body'] or '異常' in e['body'] or '故障' in e['body']:
                    case_db[case]['issues'].append({
                        'date': e['date'],
                        'description': e['body'][:200],
                    })
            
            case_db[case]['employees'] = list(case_db[case]['employees'])
        
        # 儲存案場資料庫
        case_db_file = OUTPUT_DIR / 'case_database.json'
        with open(case_db_file, 'w', encoding='utf-8') as f:
            # 簡化儲存（移除過長的 timeline）
            simplified_db = {}
            for case, info in case_db.items():
                simplified_db[case] = {
                    'employees': info['employees'],
                    'issue_count': len(info['issues']),
                    'timeline_count': len(info['timeline']),
                    'issues_sample': info['issues'][:5],
                }
            json.dump(simplified_db, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 案場資料庫已儲存：{case_db_file}")
        print(f"   案場數：{len(case_db)} 個")
        
        # 7. 建立員工資料庫
        print("\n" + "="*70)
        print("👥 建立員工資料庫")
        print("="*70)
        
        emp_db = {}
        for emp_key, emails in data['employee_emails'].items():
            emp_info = EMPLOYEE_MAP.get(emp_key, {'name': emp_key, 'dept': '未知'})
            
            emp_db[emp_key] = {
                'name': emp_info.get('name', emp_key),
                'dept': emp_info.get('dept', '未知'),
                'total_emails': len(emails),
                'daily_reports': sum(1 for e in emails if e['is_daily_report']),
                'cases': list(set(c for e in emails for c in e['cases'])),
                'attachments': sum(len(e['attachments']) for e in emails),
                'work_history': [],
            }
            
            for e in emails:
                emp_db[emp_key]['work_history'].append({
                    'date': e['date'],
                    'subject': e['subject'],
                    'is_daily': e['is_daily_report'],
                    'cases': e['cases'],
                })
        
        # 儲存員工資料庫
        emp_db_file = OUTPUT_DIR / 'employee_database.json'
        with open(emp_db_file, 'w', encoding='utf-8') as f:
            json.dump(emp_db, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 員工資料庫已儲存：{emp_db_file}")
        print(f"   員工數：{len(emp_db)} 位")
        
        mail.logout()
        
        # 最終總結
        print("\n" + "="*70)
        print("✅✅✅ 完整解析完成！")
        print("="*70)
        print(f"\n📁 輸出檔案:")
        print(f"   {OUTPUT_DIR}/")
        print(f"   ├── full_analysis_report_*.json  # 完整分析報告")
        print(f"   ├── analysis_summary_*.txt       # 文字摘要")
        print(f"   ├── case_database.json           # 案場資料庫")
        print(f"   └── employee_database.json       # 員工資料庫")
        
        print(f"\n📊 最終統計:")
        print(f"   總郵件：{data['total']} 封")
        print(f"   日報：{len(data['daily_reports'])} 封")
        print(f"   員工：{len(data['employee_emails'])} 位")
        print(f"   案場：{len(data['case_emails'])} 個")
        
        print(f"\n結束時間：{datetime.now().isoformat()}")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ 錯誤：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
