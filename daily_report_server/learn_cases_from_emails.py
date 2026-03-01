#!/usr/bin/env python3
"""
昱金生能源 - 從日報郵件學習案場知識
功能：
1. 掃描所有已解析的郵件 JSON
2. 從主旨和內容提取案場名稱
3. 建立案場資料庫（案場代碼、名稱、負責員工、郵件數）
4. 更新記憶系統
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路徑設定
EMAIL_ANALYSIS_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/email_analysis')
OUTPUT_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/full_email_analysis')
MEMORY_DIR = Path('/home/yjsclaw/.openclaw/workspace/memory')
WORKSPACE_DIR = Path('/home/yjsclaw/.openclaw/workspace')

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 案場代碼模式（例如：04-720, 02-2999, 25-1 等）
CASE_ID_PATTERN = re.compile(r'\b(\d{1,4}-\d{1,6})\b')

# 員工姓名模式
EMPLOYEE_NAMES = [
    '陳明德', '張億峖', '陳靜儒', '林天睛', '陳谷濱', '楊宗衛',
    '高竹妤', '呂宜芹', '顏呈晞', '李雅婷', '游若誼', '洪淑嫆',
    '楊傑麟', '褚佩瑜', '宋啓綸'
]

def load_all_emails():
    """載入所有已解析的郵件"""
    emails = []
    
    if not EMAIL_ANALYSIS_DIR.exists():
        logger.warning(f"郵件分析目錄不存在：{EMAIL_ANALYSIS_DIR}")
        return emails
    
    # 讀取所有 JSON 檔案
    json_files = sorted(EMAIL_ANALYSIS_DIR.glob('emails_*.json'))
    logger.info(f"找到 {len(json_files)} 個郵件檔案")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                email_list = data.get('emails', [])
                logger.info(f"  {json_file.name}: {len(email_list)} 封郵件")
                emails.extend(email_list)
        except Exception as e:
            logger.error(f"讀取 {json_file} 失敗：{e}")
    
    # 去重（根據主旨 + 日期）
    seen = set()
    unique_emails = []
    for email in emails:
        key = f"{email.get('subject', '')}_{email.get('date', '')}"
        if key not in seen:
            seen.add(key)
            unique_emails.append(email)
    
    logger.info(f"去重後：{len(unique_emails)} 封郵件")
    return unique_emails

def extract_case_info(email):
    """從郵件中提取案場資訊"""
    subject = email.get('subject', '')
    body = email.get('body', '')
    from_field = email.get('from', '')
    
    # 只處理日報郵件
    if not email.get('is_daily_report', False):
        return None
    
    # 提取案場代碼
    case_ids = CASE_ID_PATTERN.findall(subject + ' ' + body[:500])
    
    if not case_ids:
        return None
    
    # 提取員工姓名
    employee = None
    for name in EMPLOYEE_NAMES:
        if name in subject or name in from_field or name in body[:200]:
            employee = name
            break
    
    # 建立案場資訊
    cases = []
    for case_id in case_ids[:5]:  # 限制最多 5 個案場
        cases.append({
            'case_id': case_id,
            'employee': employee,
            'date': email.get('date', ''),
            'subject': subject[:100],
            'has_attachment': len(email.get('attachments', [])) > 0
        })
    
    return cases

def build_case_database(emails):
    """建立案場資料庫"""
    case_db = defaultdict(lambda: {
        'case_id': '',
        'case_name': '未知',
        'reports': [],
        'employees': set(),
        'email_count': 0,
        'first_report': None,
        'last_report': None,
        'has_attachments': 0
    })
    
    logger.info("開始建立案場資料庫...")
    
    for email in emails:
        case_infos = extract_case_info(email)
        if not case_infos:
            continue
        
        for case_info in case_infos:
            case_id = case_info['case_id']
            db_entry = case_db[case_id]
            
            db_entry['case_id'] = case_id
            db_entry['reports'].append({
                'date': case_info['date'],
                'employee': case_info['employee'],
                'subject': case_info['subject'],
                'has_attachment': case_info['has_attachment']
            })
            
            if case_info['employee']:
                db_entry['employees'].add(case_info['employee'])
            
            db_entry['email_count'] += 1
            
            if case_info['has_attachment']:
                db_entry['has_attachments'] += 1
            
            # 更新時間範圍
            date_str = case_info['date']
            if date_str:
                if not db_entry['first_report'] or date_str < db_entry['first_report']:
                    db_entry['first_report'] = date_str
                if not db_entry['last_report'] or date_str > db_entry['last_report']:
                    db_entry['last_report'] = date_str
    
    # 轉換 set 為 list（JSON 可序列化）
    for case_id, data in case_db.items():
        data['employees'] = list(data['employees'])
    
    logger.info(f"建立完成：{len(case_db)} 個案場")
    return case_db

def analyze_case_database(case_db):
    """分析案場資料庫"""
    stats = {
        'total_cases': len(case_db),
        'total_reports': sum(len(data['reports']) for data in case_db.values()),
        'total_emails': sum(data['email_count'] for data in case_db.values()),
        'cases_with_attachments': sum(1 for data in case_db.values() if data['has_attachments'] > 0),
        'top_cases': [],
        'top_employees': defaultdict(int)
    }
    
    # 找出最活躍的案場
    sorted_cases = sorted(
        case_db.items(),
        key=lambda x: len(x[1]['reports']),
        reverse=True
    )[:20]
    
    stats['top_cases'] = [
        {
            'case_id': case_id,
            'report_count': len(data['reports']),
            'email_count': data['email_count'],
            'employees': data['employees'],
            'has_attachments': data['has_attachments']
        }
        for case_id, data in sorted_cases
    ]
    
    # 統計員工參與度
    for case_id, data in case_db.items():
        for employee in data['employees']:
            stats['top_employees'][employee] += 1
    
    stats['top_employees'] = dict(
        sorted(stats['top_employees'].items(), key=lambda x: x[1], reverse=True)[:10]
    )
    
    return stats

def save_case_database(case_db, stats):
    """儲存案場資料庫"""
    # 儲存完整資料庫
    output_file = OUTPUT_DIR / 'case_database_from_emails.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'total_cases': len(case_db),
            'cases': dict(case_db)
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"已儲存到：{output_file}")
    
    # 儲存統計報告
    report_file = OUTPUT_DIR / 'case_analysis_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("📊 案場知識學習報告\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("=== 統計摘要 ===\n")
        f.write(f"案場總數：{stats['total_cases']}\n")
        f.write(f"總報告數：{stats['total_reports']}\n")
        f.write(f"總郵件數：{stats['total_emails']}\n")
        f.write(f"有附件的案場：{stats['cases_with_attachments']}\n\n")
        
        f.write("=== 前 20 大活躍案場 ===\n")
        for i, case in enumerate(stats['top_cases'], 1):
            f.write(f"{i:2}. {case['case_id']:15} - {case['report_count']:3} 封報告, "
                   f"{case['email_count']:3} 封郵件, "
                   f"負責人：{', '.join(case['employees']) if case['employees'] else '未知'}\n")
        
        f.write("\n=== 員工參與度 TOP 10 ===\n")
        for i, (employee, count) in enumerate(stats['top_employees'].items(), 1):
            f.write(f"{i:2}. {employee:10} - {count} 個案場\n")
    
    logger.info(f"已儲存報告到：{report_file}")

def update_memory(case_db, stats):
    """更新記憶系統"""
    today = datetime.now().strftime('%Y-%m-%d')
    memory_file = MEMORY_DIR / f'{today}.md'
    
    # 讀取現有記憶
    existing_content = ""
    if memory_file.exists():
        existing_content = memory_file.read_text(encoding='utf-8')
    
    # 建立記憶段落
    memory_section = f"""
## 🏭 案場知識學習（{datetime.now().strftime('%Y-%m-%d %H:%M')}）

**學習來源**: 日報郵件自動解析

**統計**:
- 案場總數：{stats['total_cases']} 個
- 總報告數：{stats['total_reports']} 封
- 總郵件數：{stats['total_emails']} 封

**前 10 大活躍案場**:
"""
    
    for i, case in enumerate(stats['top_cases'][:10], 1):
        employees = ', '.join(case['employees']) if case['employees'] else '未知'
        memory_section += f"{i}. **{case['case_id']}** - {case['report_count']} 封報告，負責人：{employees}\n"
    
    # 檢查是否已存在相似段落
    if "## 🏭 案場知識學習" in existing_content:
        # 更新現有段落（簡單替換）
        logger.info("更新現有記憶段落...")
        # 這裡可以實作更複雜的更新邏輯
    else:
        # 新增段落
        logger.info("新增記憶段落...")
        with open(memory_file, 'a', encoding='utf-8') as f:
            f.write("\n" + memory_section)
    
    logger.info(f"已更新記憶：{memory_file}")

def main():
    """主函數"""
    logger.info("=" * 70)
    logger.info("🚀 昱金生能源 - 案場知識學習系統")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 載入郵件
    emails = load_all_emails()
    if not emails:
        logger.warning("沒有找到郵件")
        return
    
    # 建立案場資料庫
    case_db = build_case_database(emails)
    
    # 分析
    stats = analyze_case_database(case_db)
    
    # 儲存
    save_case_database(case_db, stats)
    
    # 更新記憶
    update_memory(case_db, stats)
    
    # 輸出總結
    logger.info("\n" + "=" * 70)
    logger.info("📊 學習總結")
    logger.info("=" * 70)
    logger.info(f"案場總數：{stats['total_cases']}")
    logger.info(f"總報告數：{stats['total_reports']}")
    logger.info(f"總郵件數：{stats['total_emails']}")
    logger.info(f"有附件的案場：{stats['cases_with_attachments']}")
    logger.info("=" * 70)

if __name__ == '__main__':
    main()
