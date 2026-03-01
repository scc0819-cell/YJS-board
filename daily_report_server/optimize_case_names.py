#!/usr/bin/env python3
"""
昱金生能源 - 案場名稱優化提取
從郵件內容、附件、歷史資料中提取完整案場名稱
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import logging

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

# 案場代碼模式
CASE_ID_PATTERN = re.compile(r'\b(\d{1,4}-\d{1,6})\b')

# 常見案場名稱關鍵字
CASE_NAME_KEYWORDS = [
    '國小', '國中', '高中', '學校', '幼兒園',
    '停車場', '球場', '體育館', '活動中心',
    '醫院', '診所', '衛生所',
    '公所', '市政府', '區公所',
    '大樓', '大廈', '社區',
    '工廠', '廠房', '倉庫',
    '車站', '捷運', '台鐵',
    '公園', '綠地', '廣場'
]

def load_existing_case_db():
    """載入現有案場資料庫"""
    case_db_file = OUTPUT_DIR / 'case_database_from_emails.json'
    if case_db_file.exists():
        with open(case_db_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('cases', {})
    return {}

def extract_case_name_from_subject(subject, case_id):
    """從郵件主旨提取案場名稱"""
    # 模式 1: 「案場代碼 - 案場名稱」
    pattern1 = re.compile(rf'{re.escape(case_id)}[\s\-:：]+([^\n]+?)(?:日報 | 工作 | 進度 | 報告|$)')
    match = pattern1.search(subject)
    if match:
        name = match.group(1).strip()
        # 過濾太短或無意義的名稱
        if len(name) > 2 and not any(x in name for x in ['日報', '工作', '進度']):
            return name
    
    # 模式 2: 「案場名稱 + 案場代碼」
    pattern2 = re.compile(rf'([^\n\d]{{2,20}}?)[\s\-:：]*{re.escape(case_id)}')
    match = pattern2.search(subject)
    if match:
        name = match.group(1).strip()
        if len(name) > 2:
            return name
    
    return None

def extract_case_name_from_body(body, case_id):
    """從郵件內文提取案場名稱"""
    # 尋找案場代碼附近的文字
    pattern = re.compile(rf'([^\n\d]{{2,30}}?)[\s\-:：，,]*{re.escape(case_id)}')
    matches = pattern.findall(body[:1000])  # 只搜尋前 1000 字
    
    for match in matches:
        name = match.strip()
        # 檢查是否包含案場關鍵字
        if any(kw in name for kw in CASE_NAME_KEYWORDS):
            return name
    
    return None

def load_case_name_hints():
    """從知識掃描結果載入案場名稱提示"""
    hints = {}
    
    # 讀取 knowledge_z_drive.md
    knowledge_file = MEMORY_DIR / 'knowledge_z_drive.md'
    if knowledge_file.exists():
        content = knowledge_file.read_text(encoding='utf-8')
        # 提取案場名稱（簡單模式匹配）
        for line in content.split('\n'):
            if ':' in line and any(kw in line for kw in CASE_NAME_KEYWORDS):
                parts = line.split(':')
                if len(parts) >= 2:
                    # 嘗試提取案場代碼和名稱
                    potential_id = re.search(r'\d{1,4}-\d{1,6}', parts[0])
                    if potential_id:
                        case_id = potential_id.group()
                        case_name = parts[1].strip()
                        if case_name and len(case_name) > 2:
                            hints[case_id] = case_name
    
    return hints

def optimize_case_names(case_db):
    """優化案場名稱"""
    logger.info("開始優化案場名稱...")
    
    # 載入提示
    hints = load_case_name_hints()
    logger.info(f"載入 {len(hints)} 個案場名稱提示")
    
    optimized = 0
    
    for case_id, data in case_db.items():
        if data.get('case_name') != '未知':
            continue  # 已有名稱，跳過
        
        # 嘗試從提示中找到名稱
        if case_id in hints:
            data['case_name'] = hints[case_id]
            optimized += 1
            logger.info(f"  {case_id}: {hints[case_id]} (從知識庫)")
            continue
        
        # 嘗試從郵件主旨/內文提取
        for report in data.get('reports', [])[:5]:  # 只檢查前 5 封郵件
            subject = report.get('subject', '')
            if subject:
                name = extract_case_name_from_subject(subject, case_id)
                if name:
                    data['case_name'] = name
                    optimized += 1
                    logger.info(f"  {case_id}: {name} (從主旨)")
                    break
    
    logger.info(f"優化完成：{optimized} 個案場獲得名稱")
    return optimized

def save_optimized_db(case_db, stats):
    """儲存優化後的資料庫"""
    output_file = OUTPUT_DIR / 'case_database_optimized.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'total_cases': len(case_db),
            'cases_with_names': sum(1 for d in case_db.values() if d.get('case_name') != '未知'),
            'cases': case_db
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"已儲存到：{output_file}")
    
    # 儲存報告
    report_file = OUTPUT_DIR / 'case_name_optimization_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("🏭 案場名稱優化報告\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("=== 統計 ===\n")
        f.write(f"總案場數：{len(case_db)}\n")
        f.write(f"有名稱：{stats['cases_with_names']}\n")
        f.write(f"無名稱（未知）: {len(case_db) - stats['cases_with_names']}\n\n")
        
        f.write("=== 有名稱的案場 ===\n")
        for case_id, data in sorted(case_db.items()):
            if data.get('case_name') != '未知':
                f.write(f"{case_id}: {data['case_name']}\n")
    
    logger.info(f"已儲存報告到：{report_file}")

def main():
    logger.info("=" * 70)
    logger.info("🚀 昱金生能源 - 案場名稱優化")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 載入現有資料庫
    case_db = load_existing_case_db()
    if not case_db:
        logger.warning("沒有找到案場資料庫")
        return
    
    # 優化名稱
    optimized = optimize_case_names(case_db)
    
    # 統計
    stats = {
        'total': len(case_db),
        'cases_with_names': sum(1 for d in case_db.values() if d.get('case_name') != '未知')
    }
    
    # 儲存
    save_optimized_db(case_db, stats)
    
    # 輸出總結
    logger.info("\n" + "=" * 70)
    logger.info("📊 優化總結")
    logger.info("=" * 70)
    logger.info(f"總案場數：{stats['total']}")
    logger.info(f"有名稱：{stats['cases_with_names']}")
    logger.info(f"無名稱：{stats['total'] - stats['cases_with_names']}")
    logger.info("=" * 70)

if __name__ == '__main__':
    main()
