#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session 記憶注入器
功能：在新 Session 開始時自動載入相關記憶
"""

import json
from pathlib import Path
from datetime import datetime

class SessionMemoryInjector:
    def __init__(self):
        self.workspace = Path.home() / '.openclaw' / 'workspace'
        self.memory_dir = self.workspace / 'memory'
        self.index_dir = self.workspace / 'memory-index'
        
    def build_context_prompt(self, current_session_topics=None):
        """
        建立上下文注入提示
        
        這個函數會在每個新 Session 開始時被調用，
        自動載入相關的歷史記憶到上下文中
        """
        context = []
        
        # 1. 載入用戶基本資訊
        context.append(self._load_user_profile())
        
        # 2. 載入最近的重要決策
        context.append(self._load_recent_decisions())
        
        # 3. 載入進行中的任務
        context.append(self._load_active_tasks())
        
        # 4. 如果提供了當前主題，載入相關記憶
        if current_session_topics:
            context.append(self._load_related_memories(current_session_topics))
        
        # 5. 載入最近 3 天的重點摘要
        context.append(self._load_recent_summary(days=3))
        
        return '\n\n'.join(context)
    
    def _load_user_profile(self):
        """載入用戶基本資訊"""
        profile_path = self.workspace / 'USER.md'
        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"## 👤 用戶資訊\n{content}"
        return ""
    
    def _load_recent_decisions(self, limit=5):
        """載入最近的重要決策"""
        decisions = []
        
        # 搜尋最近的記憶檔案
        date_files = sorted(self.memory_dir.glob('*.md'), reverse=True)[:7]
        
        for filepath in date_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取決策區塊
                if '## 🤝 決策記錄' in content:
                    section = content.split('## 🤝 決策記錄')[1]
                    if '##' in section:
                        section = section.split('##')[0]
                    decisions.append(section.strip())
        
        if decisions:
            return f"## 🤝 最近決策\n\n" + '\n\n'.join(decisions[:limit])
        return ""
    
    def _load_active_tasks(self):
        """載入進行中的任務"""
        task_board = self.workspace / 'task-board.json'
        if task_board.exists():
            with open(task_board, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tasks = data.get('tasks', [])
            active = [t for t in tasks if t.get('status') in ['running', 'pending']]
            
            if active:
                task_list = '\n'.join([
                    f"- [{t.get('status', 'pending').upper()}] {t.get('name', 'Unnamed')} (Agent: {t.get('agent', 'unknown')})"
                    for t in active[:10]
                ])
                return f"## 📋 進行中任務\n\n{task_list}"
        
        return ""
    
    def _load_related_memories(self, topics, limit=3):
        """載入與當前主題相關的記憶"""
        # 這裡應該使用 memory_manager.py 的搜尋功能
        # 簡化版本：直接搜尋主題關鍵字
        
        related = []
        date_files = sorted(self.memory_dir.glob('*.md'), reverse=True)[:14]
        
        for topic in topics:
            for filepath in date_files:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if topic.lower() in content.lower():
                        related.append(f"主題 #{topic}: {filepath.name}")
                        break
        
        if related:
            return f"## 🔗 相關記憶\n\n" + '\n'.join(related[:limit*len(topics)])
        return ""
    
    def _load_recent_summary(self, days=3):
        """載入最近幾天的重點摘要"""
        summary = []
        date_files = sorted(self.memory_dir.glob('*.md'), reverse=True)[:days]
        
        for filepath in date_files:
            date_str = filepath.stem
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取今日重點
                if '## 📋 今日重點' in content:
                    section = content.split('## 📋 今日重點')[1]
                    if '##' in section:
                        section = section.split('##')[0]
                    summary.append(f"**{date_str}**:{section.strip()[:200]}...")
        
        if summary:
            return f"## 📅 近期摘要\n\n" + '\n\n'.join(summary)
        return ""


# 測試
if __name__ == '__main__':
    injector = SessionMemoryInjector()
    
    # 測試載入上下文
    context = injector.build_context_prompt(['自動化系統', '任務管理'])
    
    print("=" * 60)
    print("Session 上下文注入預覽")
    print("=" * 60)
    print(context)
    print("=" * 60)
