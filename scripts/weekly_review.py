#!/usr/bin/env python3
"""
昱金生能源 - 每週回顧與記憶彙整
每週一 09:00 執行，彙整上週記憶到 MEMORY.md
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路徑設定
MEMORY_DIR = Path('/home/yjsclaw/.openclaw/workspace/memory')
WORKSPACE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
MEMORY_MD = WORKSPACE_DIR / 'MEMORY.md'

def get_last_week_dates():
    """取得上週的日期範圍"""
    today = datetime.now()
    # 計算上週一和上週日
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    return last_monday, last_sunday

def load_daily_memories(start_date, end_date):
    """載入指定日期範圍的每日記憶"""
    memories = []
    current = start_date
    while current <= end_date:
        date_str = current.strftime('%Y-%m-%d')
        memory_file = MEMORY_DIR / f'{date_str}.md'
        if memory_file.exists():
            content = memory_file.read_text(encoding='utf-8')
            memories.append({
                'date': date_str,
                'content': content,
                'file': memory_file
            })
        current += timedelta(days=1)
    return memories

def extract_key_insights(memories):
    """從每日記憶中提取關鍵洞察"""
    insights = {
        'decisions': [],
        'people': [],
        'projects': [],
        'lessons': [],
        'metrics': []
    }
    
    keywords = {
        'decisions': ['決策', '決定', '採用', '選擇', '同意'],
        'people': ['員工', '負責人', '經理', '董事長', '部門'],
        'projects': ['案場', '專案', '系統', '電廠', '日報'],
        'lessons': ['教訓', '注意', '問題', '錯誤', '修正'],
        'metrics': ['統計', '數量', '完成率', '效率', '提升']
    }
    
    for memory in memories:
        content = memory['content']
        date = memory['date']
        
        for category, kw_list in keywords.items():
            for kw in kw_list:
                if kw in content:
                    # 提取包含關鍵字的段落
                    lines = content.split('\n')
                    for line in lines:
                        if kw in line and len(line) > 10:
                            insights[category].append({
                                'date': date,
                                'content': line.strip(),
                                'keyword': kw
                            })
    
    return insights

def generate_weekly_summary(insights, start_date, end_date):
    """生成每週摘要"""
    summary = f"""# 每週回顧 ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})

**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 本週統計

| 指標 | 數值 |
|------|------|
| 記憶檔案數 | {len(insights.get('metrics', []))} |
| 重要決策 | {len(insights.get('decisions', []))} |
| 人員相關 | {len(insights.get('people', []))} |
| 專案進度 | {len(insights.get('projects', []))} |
| 經驗教訓 | {len(insights.get('lessons', []))} |

---

## 🎯 重要決策

"""
    
    # 彙總決策（去重）
    decisions_seen = set()
    for item in insights.get('decisions', [])[:10]:
        key = item['content'][:50]
        if key not in decisions_seen:
            decisions_seen.add(key)
            summary += f"- [{item['date']}] {item['content']}\n"
    
    summary += """
---

## 👥 人員與組織

"""
    
    for item in insights.get('people', [])[:10]:
        summary += f"- [{item['date']}] {item['content']}\n"
    
    summary += """
---

## 🏭 專案進度

"""
    
    for item in insights.get('projects', [])[:10]:
        summary += f"- [{item['date']}] {item['content']}\n"
    
    summary += """
---

## 💡 經驗教訓

"""
    
    for item in insights.get('lessons', [])[:10]:
        summary += f"- [{item['date']}] {item['content']}\n"
    
    summary += """
---

## 📈 建議行動

1. 檢視重要決策是否需要寫入 MEMORY.md
2. 更新專案進度追蹤
3. 落實經驗教訓到工作流程
4. 清理過期臨時檔案

---

**下次回顧**: 下週一 09:00
"""
    
    return summary

def update_memory_md(weekly_summary, start_date, end_date):
    """更新 MEMORY.md，加入每週回顧"""
    if not MEMORY_MD.exists():
        logger.warning("MEMORY.md 不存在")
        return
    
    content = MEMORY_MD.read_text(encoding='utf-8')
    
    # 檢查是否已有每週回顧區塊
    weekly_section = f"## 每週回顧 ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})"
    
    if weekly_section in content:
        logger.info("本週回顧已存在，跳過更新")
        return
    
    # 在文件末尾加入每週回顧
    new_content = content.rstrip() + "\n\n---\n\n" + weekly_summary
    
    MEMORY_MD.write_text(new_content, encoding='utf-8')
    logger.info("已更新 MEMORY.md")

def save_weekly_report(summary, start_date, end_date):
    """儲存每週報告檔案"""
    output_dir = WORKSPACE_DIR / 'weekly_reports'
    output_dir.mkdir(exist_ok=True)
    
    filename = f"weekly_review_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.md"
    output_file = output_dir / filename
    
    output_file.write_text(summary, encoding='utf-8')
    logger.info(f"已儲存每週報告：{output_file}")

def main():
    logger.info("=" * 70)
    logger.info("🔄 昱金生能源 - 每週回顧與記憶彙整")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 取得上週日期
    start_date, end_date = get_last_week_dates()
    logger.info(f"📅 回顧範圍：{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    
    # 載入每日記憶
    memories = load_daily_memories(start_date, end_date)
    logger.info(f"📚 載入 {len(memories)} 個每日記憶檔案")
    
    if not memories:
        logger.warning("沒有找到記憶檔案")
        return
    
    # 提取關鍵洞察
    insights = extract_key_insights(memories)
    logger.info(f"💡 提取洞察：決策={len(insights['decisions'])}, 人員={len(insights['people'])}, "
                f"專案={len(insights['projects'])}, 教訓={len(insights['lessons'])}")
    
    # 生成每週摘要
    summary = generate_weekly_summary(insights, start_date, end_date)
    
    # 儲存每週報告
    save_weekly_report(summary, start_date, end_date)
    
    # 更新 MEMORY.md
    update_memory_md(summary, start_date, end_date)
    
    # 建立記憶索引
    create_memory_index(memories, insights)
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ 每週回顧完成！")
    logger.info("=" * 70)

def create_memory_index(memories, insights):
    """建立記憶索引檔案"""
    index = {
        'last_updated': datetime.now().isoformat(),
        'total_files': len(memories),
        'categories': {
            'decisions': [],
            'people': [],
            'projects': [],
            'lessons': []
        }
    }
    
    # 從洞察中建立索引
    for category, items in insights.items():
        if category in index['categories']:
            for item in items[:20]:  # 每個類別最多 20 筆
                index['categories'][category].append({
                    'date': item['date'],
                    'snippet': item['content'][:100],
                    'file': f"memory/{item['date']}.md"
                })
    
    # 儲存索引
    index_file = MEMORY_DIR / 'index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    logger.info(f"📑 已建立記憶索引：{index_file}")

if __name__ == '__main__':
    main()
