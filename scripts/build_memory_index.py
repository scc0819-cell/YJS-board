#!/usr/bin/env python3
"""
昱金生能源 - 記憶索引建立器
建立記憶檢索索引，加速查詢速度
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
MEMORY_DIR = Path('/home/yjsclaw/.openclaw/workspace/memory')
WORKSPACE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
MEMORY_MD = WORKSPACE_DIR / 'MEMORY.md'

def scan_memory_files():
    """掃描所有記憶檔案"""
    files = []
    
    # 掃描每日記憶
    if MEMORY_DIR.exists():
        for file in MEMORY_DIR.glob('*.md'):
            if file.name != 'index.md':
                files.append({
                    'path': str(file.relative_to(WORKSPACE_DIR)),
                    'type': 'daily',
                    'date': file.stem
                })
    
    # 加入長期記憶
    if MEMORY_MD.exists():
        files.append({
            'path': 'MEMORY.md',
            'type': 'strategy',
            'date': 'permanent'
        })
    
    return files

def extract_content_metadata(file_path):
    """提取檔案內容的元數據"""
    full_path = WORKSPACE_DIR / file_path
    if not full_path.exists():
        return None
    
    content = full_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    metadata = {
        'total_lines': len(lines),
        'sections': [],
        'topics': defaultdict(list),
        'line_count': 0
    }
    
    # 提取章節標題
    section_pattern = re.compile(r'^(#{1,3})\s+(.+)$')
    current_section = None
    
    for i, line in enumerate(lines, 1):
        match = section_pattern.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            metadata['sections'].append({
                'title': title,
                'level': level,
                'line': i
            })
            current_section = title
        
        # 提取關鍵字
        keywords = ['決策', '決定', '員工', '案場', '系統', '教訓', '注意', '問題']
        for kw in keywords:
            if kw in line and len(line) > 20:
                metadata['topics'][kw].append({
                    'line': i,
                    'content': line.strip()[:100],
                    'section': current_section
                })
    
    metadata['line_count'] = len(lines)
    return metadata

def build_search_index(files):
    """建立搜尋索引"""
    index = {
        'generated_at': datetime.now().isoformat(),
        'total_files': len(files),
        'files': [],
        'topic_index': defaultdict(list),
        'section_index': []
    }
    
    for file_info in files:
        metadata = extract_content_metadata(file_info['path'])
        if metadata:
            file_entry = {
                'path': file_info['path'],
                'type': file_info['type'],
                'date': file_info['date'],
                'lines': metadata['line_count'],
                'sections': len(metadata['sections']),
                'topics': {k: len(v) for k, v in metadata['topics'].items()}
            }
            index['files'].append(file_entry)
            
            # 建立主題索引
            for topic, items in metadata['topics'].items():
                for item in items:
                    index['topic_index'][topic].append({
                        'file': file_info['path'],
                        'line': item['line'],
                        'content': item['content'],
                        'section': item['section']
                    })
            
            # 建立章節索引
            for section in metadata['sections']:
                index['section_index'].append({
                    'file': file_info['path'],
                    'title': section['title'],
                    'level': section['level'],
                    'line': section['line']
                })
    
    # 轉換 defaultdict 為普通 dict
    index['topic_index'] = dict(index['topic_index'])
    
    return index

def save_index(index):
    """儲存索引檔案"""
    index_file = MEMORY_DIR / 'index.json'
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f"✅ 已儲存索引：{index_file}")
    
    # 同時儲存人類可讀版本
    readable_file = MEMORY_DIR / 'index.md'
    with open(readable_file, 'w', encoding='utf-8') as f:
        f.write("# 📑 記憶索引\n\n")
        f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**總檔案數**: {index['total_files']}\n\n")
        
        f.write("## 📁 檔案列表\n\n")
        for file in index['files'][:20]:
            f.write(f"- `{file['path']}` ({file['type']}) - {file['lines']} 行\n")
        
        f.write("\n## 🏷️ 主題索引\n\n")
        for topic, items in sorted(index['topic_index'].items(), key=lambda x: -len(x[1]))[:10]:
            f.write(f"### {topic} ({len(items)} 筆)\n\n")
            for item in items[:5]:
                f.write(f"- [{item['file']}#L{item['line']}] {item['content']}\n")
            f.write("\n")
    
    logger.info(f"✅ 已儲存可讀索引：{readable_file}")

def main():
    logger.info("=" * 70)
    logger.info("📑 昱金生能源 - 記憶索引建立器")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 掃描記憶檔案
    files = scan_memory_files()
    logger.info(f"📚 掃描到 {len(files)} 個記憶檔案")
    
    # 建立搜尋索引
    index = build_search_index(files)
    logger.info(f"🔍 建立索引：{len(index['topic_index'])} 個主題，{len(index['section_index'])} 個章節")
    
    # 儲存索引
    save_index(index)
    
    # 輸出統計
    logger.info("\n" + "=" * 70)
    logger.info("📊 索引統計")
    logger.info("=" * 70)
    logger.info(f"總檔案數：{index['total_files']}")
    logger.info(f"主題數：{len(index['topic_index'])}")
    logger.info(f"章節數：{len(index['section_index'])}")
    
    # 顯示熱門主題
    logger.info("\n🏷️ 熱門主題 TOP 5:")
    sorted_topics = sorted(index['topic_index'].items(), key=lambda x: -len(x[1]))[:5]
    for topic, items in sorted_topics:
        logger.info(f"  {topic}: {len(items)} 筆")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ 記憶索引建立完成！")
    logger.info("=" * 70)

if __name__ == '__main__':
    main()
