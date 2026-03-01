#!/usr/bin/env python3
"""
昱金生能源 - 案場名稱一次性提取（365 天完整掃描）
執行一次，提取所有案場名稱，寫入資料庫後定稿
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
EMAIL_ANALYSIS_DIR = WORKSPACE_DIR.parent / 'email_analysis'
DATA_DIR = WORKSPACE_DIR / 'daily_report_server' / 'data'

# 案場名稱匹配規則（更精確）
CASE_NAME_PATTERNS = [
    # 完整格式：02-2999 昱金生能源光電案場
    (r'(\d{2}-\d{4})\s*([\u4e00-\u9fa5]{2,30}?(?:案場 | 電廠 | 光電))', 'full'),
    # 公司名稱 + 案場：...公司...案場
    (r'([\u4e00-\u9fa5]{2,}公司)[\u4e00-\u9fa5]{0,10}?(?:案場 | 電廠)', 'company_case'),
    # 地址 + 案場：彰化縣...光電
    (r'(彰化縣 | 台中市 | 台南市 | 高雄市)[\u4e00-\u9fa50-9]{5,30}?(?:光電 | 案場)', 'address_case'),
]

def load_all_emails(days=365):
    """載入所有郵件（365 天）"""
    emails = []
    
    if EMAIL_ANALYSIS_DIR.exists():
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for file in sorted(EMAIL_ANALYSIS_DIR.glob('emails_*.json')):
            try:
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
    
    logger.info(f"📧 載入 {len(emails)} 封郵件（{days} 天）")
    return emails

def extract_case_names_smart(emails):
    """智慧提取案場名稱（優先使用最完整名稱）"""
    case_names = defaultdict(list)
    
    for email in emails:
        subject = email.get('subject', '')
        body = email.get('body', '')
        sender = email.get('sender', '')
        date = email.get('date', '')
        
        content = f"{subject} {body}"
        
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
                    
                    case_id = case_id.strip()
                    
                    # 只儲存有完整名稱的
                    if name and len(name) > 3:
                        case_names[case_id].append({
                            'name': name.strip(),
                            'type': pattern_type,
                            'quality': len(name),
                            'sender': sender,
                            'date': date
                        })
    
    logger.info(f"🏭 提取到 {len(case_names)} 個案場的名稱")
    return case_names

def select_best_name(names):
    """選擇最佳案場名稱"""
    if not names:
        return None
    
    # 優先選擇完整格式（full > company_case > address_case）
    type_priority = {'full': 0, 'company_case': 1, 'address_case': 2}
    
    # 按類型排序，再按長度排序
    sorted_names = sorted(
        names,
        key=lambda x: (type_priority.get(x['type'], 99), -x['quality'])
    )
    
    return sorted_names[0]

def load_current_database():
    """載入當前案場資料庫"""
    db_path = DATA_DIR / 'case_database_from_emails.json'
    if db_path.exists():
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def finalize_case_names(current_db, extracted_names):
    """定稿案場名稱（只更新沒有名稱的）"""
    finalized = []
    updated_count = 0
    skipped_count = 0
    
    for case in current_db:
        case_id = case.get('case_id', case.get('id', ''))
        current_name = case.get('case_name', '')
        
        # 如果已有完整名稱，跳過（不更動）
        if current_name and len(current_name) > 10 and '光電案場' not in current_name:
            case['name_status'] = 'finalized'
            case['name_source'] = 'existing'
            finalized.append(case)
            skipped_count += 1
            continue
        
        # 從提取結果中選擇最佳名稱
        if case_id in extracted_names:
            best = select_best_name(extracted_names[case_id])
            if best:
                case['case_name'] = best['name']
                case['name_status'] = 'finalized'
                case['name_source'] = f"email_{best['type']}"
                case['name_finalized_date'] = datetime.now().isoformat()
                case['name_reference'] = {
                    'sender': best['sender'],
                    'date': best['date']
                }
                updated_count += 1
            else:
                case['case_name'] = f"{case_id} 光電案場"
                case['name_status'] = 'pending'
        else:
            case['case_name'] = f"{case_id} 光電案場"
            case['name_status'] = 'pending'
            case['name_source'] = 'default'
        
        finalized.append(case)
    
    logger.info(f"✅ 定稿完成：更新 {updated_count} 個，跳過 {skipped_count} 個（已有名稱）")
    return finalized

def generate_final_report(stats, finalized_db):
    """生成最終報告"""
    report_md = f"""# 🏭 案場名稱最終報告

**執行時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**掃描範圍**: 最近 365 天郵件
**任務狀態**: ✅ 完成（定稿）

---

## 📊 最終統計

| 指標 | 數值 | 百分比 |
|------|------|--------|
| 總案場數 | {stats['total_cases']} | 100% |
| 有完整名稱 | {stats['with_names']} | {stats['with_names']/stats['total_cases']*100:.1f}% |
| 無完整名稱 | {stats['without_names']} | {stats['without_names']/stats['total_cases']*100:.1f}% |
| 本次更新 | {stats['updated']} | - |
| 本次跳過 | {stats['skipped']} | - |

---

## ✅ 定稿策略

| 狀態 | 說明 | 處理方式 |
|------|------|----------|
| finalized | 已有完整名稱 | 保留，不再更動 |
| finalized (new) | 本次提取完整名稱 | 寫入資料庫，定稿 |
| pending | 無完整名稱 | 使用預設名稱，待手動補充 |

---

## 📈 名稱來源分佈

| 來源 | 數量 | 說明 |
|------|------|------|
"""
    
    source_descriptions = {
        'existing': '原有名稱（已定稿）',
        'email_full': '郵件完整格式',
        'email_company_case': '郵件公司 + 案場',
        'email_address_case': '郵件地址 + 案場',
        'default': '預設名稱（待補充）'
    }
    
    for source, count in sorted(stats['by_source'].items(), key=lambda x: -x[1]):
        desc = source_descriptions.get(source, source)
        report_md += f"| {desc} | {count} |\n"
    
    coverage = stats['with_names'] / stats['total_cases'] * 100
    
    report_md += f"""
---

## 💡 結論

**覆蓋率**: {coverage:.1f}%

"""
    
    if coverage >= 80:
        report_md += "✅ **覆蓋率優秀** - 大多數案場已有完整名稱\n"
        report_md += "   - 建議：手動補充剩餘案場名稱\n\n"
    elif coverage >= 60:
        report_md += "👍 **覆蓋率良好** - 過半數案場有完整名稱\n"
        report_md += "   - 建議：持續從郵件中提取，或手動補充\n\n"
    else:
        report_md += "⚠️ **覆蓋率偏低** - 僅 {:.1f}% 案場有完整名稱\n".format(coverage)
        report_md += "   - 建議：擴大郵件掃描範圍或手動建檔\n\n"
    
    report_md += f"""
---

## 🔒 定稿說明

- ✅ 所有案場名稱已寫入資料庫
- ✅ 已有名稱的案場不會再更動
- ✅ 本次提取的名稱已永久保存
- ✅ 此腳本為一次性任務，完成後可停用

---

## 📋 後續建議

1. **檢視 pending 案場** - 手動補充 {stats['without_names']} 個案場名稱
2. **定期檢查** - 每季檢查是否有新案場需要命名
3. **停用排程** - 此任務已完成，可從 crontab 移除

---

**任務狀態**: ✅ 完成
**下次執行**: 不需要（一次性任務）
"""
    
    return report_md

def save_final_report(stats, finalized_db, report_md):
    """儲存最終報告"""
    output_dir = WORKSPACE_DIR / 'daily_report_attachments' / 'case_name_finalization'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 儲存 Markdown 報告
    md_path = output_dir / f'case_finalization_{timestamp}.md'
    md_path.write_text(report_md, encoding='utf-8')
    logger.info(f"📄 已儲存最終報告：{md_path}")
    
    # 儲存最終資料庫
    db_path = output_dir / f'case_database_finalized_{timestamp}.json'
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(finalized_db, f, ensure_ascii=False, indent=2)
    logger.info(f"📊 已儲存最終資料庫：{db_path}")
    
    # 更新主資料庫
    main_db_path = DATA_DIR / 'case_database_from_emails.json'
    with open(main_db_path, 'w', encoding='utf-8') as f:
        json.dump(finalized_db, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ 已更新主資料庫")
    
    # 儲存摘要
    summary_path = output_dir / 'CASE_NAME_FINALIZATION_COMPLETE.md'
    summary_path.write_text(f"""# ✅ 案場名稱定稿完成

**完成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 最終統計
- 總案場數：{stats['total_cases']}
- 有完整名稱：{stats['with_names']} ({stats['with_names']/stats['total_cases']*100:.1f}%)
- 本次更新：{stats['updated']} 個案場

## 下一步
1. 檢視 pending 案場
2. 手動補充剩餘名稱
3. 停用此排程任務

**任務狀態**: ✅ 完成
""", encoding='utf-8')
    logger.info("📄 已儲存完成摘要")

def main():
    logger.info("=" * 70)
    logger.info("🏭 昱金生能源 - 案場名稱一次性提取（365 天）")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 載入郵件（365 天）
    emails = load_all_emails(days=365)
    if not emails:
        logger.warning("沒有郵件資料")
        return
    
    # 智慧提取案場名稱
    extracted_names = extract_case_names_smart(emails)
    
    # 載入當前資料庫
    current_db = load_current_database()
    if not current_db:
        logger.warning("沒有案場資料庫")
        return
    
    # 定稿案場名稱
    finalized_db = finalize_case_names(current_db, extracted_names)
    
    # 生成統計
    stats = {
        'total_cases': len(finalized_db),
        'with_names': sum(1 for c in finalized_db if c.get('name_status') == 'finalized' and '光電案場' not in c.get('case_name', '')),
        'without_names': sum(1 for c in finalized_db if c.get('name_status') == 'pending'),
        'updated': sum(1 for c in finalized_db if c.get('name_source', '').startswith('email_')),
        'skipped': sum(1 for c in finalized_db if c.get('name_source') == 'existing'),
        'by_source': defaultdict(int)
    }
    
    for case in finalized_db:
        stats['by_source'][case.get('name_source', 'unknown')] += 1
    
    # 生成最終報告
    report_md = generate_final_report(stats, finalized_db)
    
    # 儲存報告
    save_final_report(stats, finalized_db, report_md)
    
    # 輸出總結
    logger.info("\n" + "=" * 70)
    logger.info("✅ 案場名稱定稿完成！")
    logger.info("=" * 70)
    logger.info(f"總案場：{stats['total_cases']} | "
                f"有名稱：{stats['with_names']} ({stats['with_names']/stats['total_cases']*100:.1f}%) | "
                f"本次更新：{stats['updated']} | "
                f"本次跳過：{stats['skipped']}")
    logger.info("\n📄 報告位置：daily_report_attachments/case_name_finalization/")
    logger.info("✅ 此為一次性任務，完成後可停用排程")
    logger.info("\n📋 建議執行命令:")
    logger.info("  python3 /home/yjsclaw/.openclaw/workspace/scripts/case_name_finalization.py")

if __name__ == '__main__':
    main()
