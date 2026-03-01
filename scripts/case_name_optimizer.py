#!/usr/bin/env python3
"""
昱金生能源 - 案場名稱提取優化
每日執行：掃描郵件、提取案場名稱、更新資料庫
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
import logging
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路徑設定
WORKSPACE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
ATTACHMENTS_DIR = WORKSPACE_DIR.parent / 'daily_report_attachments'
EMAIL_ANALYSIS_DIR = WORKSPACE_DIR.parent / 'email_analysis'

# 案場名稱匹配規則
CASE_NAME_PATTERNS = [
    # 標準格式：02-2999
    (r'(\d{2}-\d{4})', 'standard'),
    # 完整格式：02-2999 屋頂光電
    (r'(\d{2}-\d{4})\s*(.+?)(?:案場|電廠|光電)', 'full'),
    # 地址格式：彰化縣...
    (r'(彰化縣|台中市|台南市|高雄市)[^\n]{10,50}', 'address'),
    # 公司名稱格式：...公司
    (r'([^\n]{5,30}公司)', 'company'),
]

def load_recent_emails(days=90):
    """載入最近 N 天的郵件"""
    emails = []
    
    # 掃描郵件分析目錄
    if EMAIL_ANALYSIS_DIR.exists():
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for file in EMAIL_ANALYSIS_DIR.glob('emails_*.json'):
            try:
                # 從檔名提取日期
                date_str = file.stem.replace('emails_', '')
                file_date = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                
                if file_date >= cutoff_date:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            emails.extend(data)
                        else:
                            emails.append(data)
            except Exception as e:
                logger.warning(f"讀取郵件失敗 {file}: {e}")
    
    logger.info(f"📧 載入 {len(emails)} 封郵件（最近 {days} 天）")
    return emails

def extract_case_names(emails):
    """從郵件中提取案場名稱"""
    case_names = defaultdict(list)
    
    for email in emails:
        # 提取主旨
        subject = email.get('subject', '')
        body = email.get('body', '')
        sender = email.get('sender', '')
        date = email.get('date', '')
        
        # 合併內容進行匹配
        content = f"{subject} {body}"
        
        # 嘗試匹配案場編號
        for pattern, pattern_type in CASE_NAME_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        case_id = match[0]
                        name = match[1] if len(match) > 1 else ''
                    else:
                        case_id = match
                        name = ''
                    
                    # 清理案場編號
                    case_id = case_id.strip()
                    
                    # 儲存提取結果
                    case_names[case_id].append({
                        'name': name.strip() if name else '',
                        'type': pattern_type,
                        'source': 'subject' if pattern_type == 'standard' else 'body',
                        'sender': sender,
                        'date': date
                    })
    
    logger.info(f"🏭 提取到 {len(case_names)} 個案場的案場名稱")
    return case_names

def load_current_database():
    """載入當前案場資料庫"""
    db_path = WORKSPACE_DIR / 'daily_report_server' / 'data' / 'case_database_from_emails.json'
    if db_path.exists():
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def optimize_case_names(current_db, extracted_names):
    """優化案場名稱"""
    optimized = []
    updated_count = 0
    
    for case in current_db:
        case_id = case.get('case_id', case.get('id', ''))
        current_name = case.get('case_name', '')
        
        # 如果已有名稱，保留
        if current_name and len(current_name) > 3:
            case['name_source'] = 'existing'
            optimized.append(case)
            continue
        
        # 嘗試從提取結果中尋找名稱
        if case_id in extracted_names:
            names = extracted_names[case_id]
            
            # 優先使用完整格式名稱
            full_names = [n for n in names if n['type'] == 'full' and n['name']]
            if full_names:
                case['case_name'] = full_names[0]['name']
                case['name_source'] = 'email_extraction'
                case['name_updated'] = datetime.now().isoformat()
                updated_count += 1
            else:
                # 使用標準格式
                case['case_name'] = f"{case_id} 光電案場"
                case['name_source'] = 'auto_generated'
                case['name_updated'] = datetime.now().isoformat()
                updated_count += 1
        else:
            # 沒有名稱，使用預設
            case['case_name'] = f"{case_id} 光電案場"
            case['name_source'] = 'default'
        
        optimized.append(case)
    
    logger.info(f"✅ 優化了 {updated_count} 個案場名稱")
    return optimized

def generate_statistics(optimized_db):
    """生成統計報告"""
    stats = {
        'total_cases': len(optimized_db),
        'with_names': 0,
        'without_names': 0,
        'by_source': defaultdict(int),
        'recently_updated': 0
    }
    
    today = datetime.now().date()
    
    for case in optimized_db:
        name = case.get('case_name', '')
        source = case.get('name_source', 'unknown')
        
        if name and len(name) > 10 and '光電案場' not in name:
            stats['with_names'] += 1
        else:
            stats['without_names'] += 1
        
        stats['by_source'][source] += 1
        
        # 檢查是否為今日更新
        if case.get('name_updated'):
            try:
                update_date = datetime.fromisoformat(case['name_updated']).date()
                if update_date == today:
                    stats['recently_updated'] += 1
            except:
                pass
    
    return stats

def generate_report(stats, optimized_db):
    """生成優化報告"""
    report_md = f"""# 🏭 案場名稱優化報告

**執行時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**掃描範圍**: 最近 90 天郵件

---

## 📊 統計總覽

| 指標 | 數值 | 百分比 |
|------|------|--------|
| 總案場數 | {stats['total_cases']} | 100% |
| 有完整名稱 | {stats['with_names']} | {stats['with_names']/stats['total_cases']*100:.1f}% |
| 無完整名稱 | {stats['without_names']} | {stats['without_names']/stats['total_cases']*100:.1f}% |
| 今日更新 | {stats['recently_updated']} | - |

---

## 📈 名稱來源分佈

| 來源 | 數量 | 說明 |
|------|------|------|
"""
    
    source_descriptions = {
        'existing': '原有名稱',
        'email_extraction': '郵件提取',
        'auto_generated': '自動生成',
        'default': '預設名稱'
    }
    
    for source, count in sorted(stats['by_source'].items(), key=lambda x: -x[1]):
        desc = source_descriptions.get(source, source)
        report_md += f"| {desc} | {count} |\n"
    
    report_md += f"""
---

## 💡 優化建議

"""
    
    coverage = stats['with_names'] / stats['total_cases'] * 100
    
    if coverage < 50:
        report_md += "⚠️ **覆蓋率低** - 僅 {:.1f}% 案場有完整名稱\n".format(coverage)
        report_md += "   - 建議擴大郵件掃描範圍至 180 天\n"
        report_md += "   - 建議手動補充主要案場名稱\n\n"
    elif coverage < 70:
        report_md += "👍 **覆蓋率中等** - {:.1f}% 案場有完整名稱\n".format(coverage)
        report_md += "   - 持續從郵件中提取名稱\n"
        report_md += "   - 定期執行優化腳本\n\n"
    else:
        report_md += "✅ **覆蓋率良好** - {:.1f}% 案場有完整名稱\n".format(coverage)
        report_md += "   - 維持當前優化頻率\n"
        report_md += "   - 定期檢查名稱準確性\n\n"
    
    report_md += """
---

## 📋 執行細節

- **掃描郵件數**: 自動偵測
- **掃描天數**: 90 天
- **匹配規則**: 4 種模式（標準/完整/地址/公司）
- **更新策略**: 優先使用完整格式名稱

---

**下次執行**: 每日 04:30
"""
    
    return report_md

def save_reports(stats, optimized_db, report_md):
    """儲存報告檔案"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = WORKSPACE_DIR / 'daily_report_attachments' / 'case_name_optimization'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 儲存 Markdown 報告
    md_path = output_dir / f'case_optimization_{timestamp}.md'
    md_path.write_text(report_md, encoding='utf-8')
    logger.info(f"📄 已儲存報告：{md_path}")
    
    # 儲存優化後的資料庫
    db_path = output_dir / f'case_database_optimized_{timestamp}.json'
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(optimized_db, f, ensure_ascii=False, indent=2)
    logger.info(f"📊 已儲存資料庫：{db_path}")
    
    # 更新主資料庫
    main_db_path = WORKSPACE_DIR / 'daily_report_server' / 'data' / 'case_database_from_emails.json'
    with open(main_db_path, 'w', encoding='utf-8') as f:
        json.dump(optimized_db, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ 已更新主資料庫")
    
    # 更新最新報告
    latest_md = output_dir / 'case_optimization_latest.md'
    latest_md.write_text(report_md, encoding='utf-8')
    logger.info("📄 已更新最新報告")

def main():
    logger.info("=" * 70)
    logger.info("🏭 昱金生能源 - 案場名稱提取優化")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 載入郵件
    emails = load_recent_emails(days=90)
    if not emails:
        logger.warning("沒有郵件資料，跳過優化")
        return
    
    # 提取案場名稱
    extracted_names = extract_case_names(emails)
    
    # 載入當前資料庫
    current_db = load_current_database()
    if not current_db:
        logger.warning("沒有案場資料庫，跳過優化")
        return
    
    # 優化案場名稱
    optimized_db = optimize_case_names(current_db, extracted_names)
    
    # 生成統計
    stats = generate_statistics(optimized_db)
    
    # 生成報告
    report_md = generate_report(stats, optimized_db)
    
    # 儲存報告
    save_reports(stats, optimized_db, report_md)
    
    # 輸出總結
    logger.info("\n" + "=" * 70)
    logger.info("✅ 案場名稱優化完成！")
    logger.info("=" * 70)
    logger.info(f"總案場：{stats['total_cases']} | "
                f"有名稱：{stats['with_names']} ({stats['with_names']/stats['total_cases']*100:.1f}%) | "
                f"今日更新：{stats['recently_updated']}")

if __name__ == '__main__':
    main()
