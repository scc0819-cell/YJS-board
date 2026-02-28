#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
記憶管理系統 - 核心功能
功能：自動採集、索引建立、智能檢索、上下文注入
"""

import json
import os
from pathlib import Path
from datetime import datetime
import re

class MemoryManager:
    def __init__(self):
        self.workspace = Path.home() / '.openclaw' / 'workspace'
        self.memory_dir = self.workspace / 'memory'
        self.index_dir = self.workspace / 'memory-index'
        self.sessions_dir = self.workspace / 'sessions'
        
        # 確保目錄存在
        self.memory_dir.mkdir(exist_ok=True)
        self.index_dir.mkdir(exist_ok=True)
        self.sessions_dir.mkdir(exist_ok=True)
        
        # 載入或建立索引
        self.topics_index = self._load_index('topics.json')
        self.entities_index = self._load_index('entities.json')
        self.sessions_index = self._load_index('sessions.json')
        
    def _load_index(self, filename):
        """載入索引檔案"""
        path = self.index_dir / filename
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"index": {}, "last_updated": None}
    
    def _save_index(self, filename, data):
        """儲存索引檔案"""
        data['last_updated'] = datetime.now().isoformat()
        path = self.index_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def capture_memory(self, content, mem_type='general', topics=None, entities=None, importance=5):
        """
        捕獲單條記憶
        
        Args:
            content: 記憶內容
            mem_type: 類型 (fact/decision/preference/task/relationship)
            topics: 主題列表
            entities: 實體列表
            importance: 重要程度 (1-10)
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d')
        mem_id = f"mem-{date_str}-{timestamp.strftime('%H%M%S')}"
        
        memory = {
            'id': mem_id,
            'type': mem_type,
            'timestamp': timestamp.isoformat(),
            'content': content,
            'topics': topics or [],
            'entities': entities or [],
            'importance': importance,
            'tags': [f'#{t}' for t in (topics or [])]
        }
        
        # 儲存到每日記憶檔案
        daily_file = self.memory_dir / f'{date_str}.md'
        self._append_to_daily(daily_file, memory)
        
        # 更新索引
        self._update_topics_index(topics or [], mem_id)
        self._update_entities_index(entities or [], mem_id)
        
        print(f"✅ 記憶已儲存：{mem_id}")
        return mem_id
    
    def _append_to_daily(self, filepath, memory):
        """添加到每日記憶檔案"""
        date_str = memory['timestamp'][:10]
        
        if not filepath.exists():
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {date_str} 記憶記錄\n\n")
                f.write("## 📋 今日重點\n\n")
                f.write("## 🤝 決策記錄\n\n")
                f.write("## 📊 事實記錄\n\n")
                f.write("## 💡 洞察與學習\n\n")
                f.write("## 🔗 相關 Sessions\n\n")
        
        # 根據類型添加到不同區塊
        section_map = {
            'decision': '## 🤝 決策記錄',
            'fact': '## 📊 事實記錄',
            'preference': '## 💡 洞察與學習',
            'task': '## 📋 今日重點',
            'relationship': '## 💡 洞察與學習',
            'general': '## 💡 洞察與學習'
        }
        
        section = section_map.get(memory['type'], '## 💡 洞察與學習')
        
        entry = f"\n### {memory['id']}\n"
        entry += f"- **時間**: {memory['timestamp'][11:19]}\n"
        entry += f"- **內容**: {memory['content']}\n"
        if memory['topics']:
            entry += f"- **主題**: {', '.join(memory['topics'])}\n"
        if memory['entities']:
            entry += f"- **實體**: {', '.join(memory['entities'])}\n"
        entry += f"- **重要度**: {'⭐' * memory['importance']}\n"
        
        # 讀取檔案並插入到對應區塊
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到區塊位置並插入
        if section in content:
            parts = content.split(section)
            content = parts[0] + section + entry + parts[1]
        else:
            content += entry
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _update_topics_index(self, topics, mem_id):
        """更新主題索引"""
        for topic in topics:
            if topic not in self.topics_index['index']:
                self.topics_index['index'][topic] = []
            self.topics_index['index'][topic].append(mem_id)
        self._save_index('topics.json', self.topics_index)
    
    def _update_entities_index(self, entities, mem_id):
        """更新實體索引"""
        for entity in entities:
            if entity not in self.entities_index['index']:
                self.entities_index['index'][entity] = []
            self.entities_index['index'][entity].append(mem_id)
        self._save_index('entities.json', self.entities_index)
    
    def search(self, query, search_type='all', limit=10):
        """
        搜尋記憶
        
        Args:
            query: 搜尋關鍵字或主題
            search_type: 搜尋類型 (keyword/topic/entity/all)
            limit: 返回結果數量限制
        """
        results = []
        
        if search_type in ['keyword', 'all']:
            # 全文搜尋
            results.extend(self._search_keyword(query, limit))
        
        if search_type in ['topic', 'all']:
            # 主題搜尋
            results.extend(self._search_topic(query, limit))
        
        if search_type in ['entity', 'all']:
            # 實體搜尋
            results.extend(self._search_entity(query, limit))
        
        # 去重並排序
        seen = set()
        unique_results = []
        for r in results:
            if r['id'] not in seen:
                seen.add(r['id'])
                unique_results.append(r)
        
        return unique_results[:limit]
    
    def _search_keyword(self, query, limit):
        """關鍵字搜尋"""
        results = []
        # 搜尋最近的記憶檔案
        date_files = sorted(self.memory_dir.glob('*.md'), reverse=True)[:30]
        
        for filepath in date_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if query.lower() in content.lower():
                    results.append({
                        'id': f'file:{filepath.name}',
                        'type': 'file',
                        'path': str(filepath),
                        'relevance': 0.8
                    })
        
        return results
    
    def _search_topic(self, topic, limit):
        """主題搜尋"""
        if topic in self.topics_index['index']:
            mem_ids = self.topics_index['index'][topic]
            return [{'id': mid, 'type': 'topic', 'relevance': 0.9} for mid in mem_ids[-limit:]]
        return []
    
    def _search_entity(self, entity, limit):
        """實體搜尋"""
        if entity in self.entities_index['index']:
            mem_ids = self.entities_index['index'][entity]
            return [{'id': mid, 'type': 'entity', 'relevance': 0.9} for mid in mem_ids[-limit:]]
        return []
    
    def get_context(self, current_topics, limit=5):
        """
        根據當前主題獲取相關記憶（用於注入到新 Session）
        
        Args:
            current_topics: 當前對話的主題列表
            limit: 每個主題返回的記憶數量
        """
        context = {
            'related_memories': [],
            'suggested_topics': [],
            'important_decisions': []
        }
        
        # 搜尋每個主題的相關記憶
        for topic in current_topics:
            memories = self.search(topic, search_type='topic', limit=limit)
            context['related_memories'].extend(memories)
        
        # 建議相關主題
        for topic in current_topics:
            if topic in self.topics_index['index']:
                # 找到與當前主題共同出現的其他主題
                co_topics = {}
                for mem_id in self.topics_index['index'][topic]:
                    # 簡化：實際應該查詢完整記憶內容
                    pass
                context['suggested_topics'] = list(co_topics.keys())[:5]
        
        return context
    
    def generate_summary(self, date_range='week'):
        """
        生成記憶摘要
        
        Args:
            date_range: 時間範圍 (day/week/month)
        """
        # 實作摘要邏輯
        pass
    
    def list_topics(self):
        """列出所有主題"""
        return list(self.topics_index['index'].keys())
    
    def list_entities(self):
        """列出所有實體"""
        return list(self.entities_index['index'].keys())
    
    def stats(self):
        """顯示統計資訊"""
        return {
            'total_topics': len(self.topics_index['index']),
            'total_entities': len(self.entities_index['index']),
            'memory_files': len(list(self.memory_dir.glob('*.md'))),
            'last_updated': self.topics_index.get('last_updated', 'N/A')
        }


# 命令列介面
if __name__ == '__main__':
    import sys
    
    mm = MemoryManager()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python memory_manager.py add <內容> [類型] [主題1,主題 2]")
        print("  python memory_manager.py search <關鍵字>")
        print("  python memory_manager.py topics")
        print("  python memory_manager.py stats")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'add':
        content = sys.argv[2] if len(sys.argv) > 2 else ""
        mem_type = sys.argv[3] if len(sys.argv) > 3 else 'general'
        topics = sys.argv[4].split(',') if len(sys.argv) > 4 else []
        
        mem_id = mm.capture_memory(content, mem_type, topics)
        print(f"✅ 記憶已儲存：{mem_id}")
    
    elif command == 'search':
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        results = mm.search(query)
        print(f"\n搜尋結果 ({len(results)} 筆):")
        for r in results:
            print(f"  - {r['id']} ({r['type']})")
    
    elif command == 'topics':
        topics = mm.list_topics()
        print(f"\n主題列表 ({len(topics)} 個):")
        for t in sorted(topics):
            print(f"  # {t}")
    
    elif command == 'stats':
        stats = mm.stats()
        print("\n記憶系統統計:")
        for k, v in stats.items():
            print(f"  {k}: {v}")
    
    else:
        print(f"未知命令：{command}")
