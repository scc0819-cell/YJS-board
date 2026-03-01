#!/usr/bin/env python3
"""
昱金生能源 - Session 管理器
管理子代理 Session 的生命週期、記憶保存與延續
"""

import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路徑設定
WORKSPACE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
SESSION_MEMORY_DIR = WORKSPACE_DIR / 'session_memory'
SESSION_MEMORY_DIR.mkdir(parents=True, exist_ok=True)

class SessionManager:
    """Session 管理器"""
    
    def __init__(self):
        self.active_sessions = {}
        self.session_history = []
    
    def should_spawn_new_session(self, context_length_estimate, max_context_tokens=100000):
        """
        判斷是否需要新開 Session
        
        判斷標準：
        1. 上下文長度超過閾值
        2. 任務類型改變（從對話轉為執行）
        3. 需要長時間運行的任務
        4. 需要獨立記憶的任務
        """
        # 估算上下文長度（簡化版）
        estimated_tokens = context_length_estimate * 4  # 粗略估計：1 中文字 ≈ 4 tokens
        
        if estimated_tokens > max_context_tokens:
            logger.info(f"⚠️ 上下文過長 ({estimated_tokens} tokens > {max_context_tokens})")
            return True
        
        return False
    
    def save_session_context(self, session_key, context_data):
        """
        保存 Session 上下文到記憶
        
        保存內容：
        - 任務描述
        - 執行結果
        - 重要決策
        - 相關檔案路徑
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        memory_file = SESSION_MEMORY_DIR / f"{session_key}_{timestamp}.json"
        
        memory_data = {
            'session_key': session_key,
            'timestamp': datetime.now().isoformat(),
            'context': context_data,
            'summary': self._generate_summary(context_data),
            'key_decisions': self._extract_decisions(context_data),
            'related_files': self._extract_files(context_data)
        }
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 已保存 Session 記憶：{memory_file}")
        return memory_file
    
    def load_session_memory(self, session_key):
        """
        載入 Session 記憶
        
        用於新 Session 延續之前的討論
        """
        # 尋找最新的記憶檔案
        pattern = f"{session_key}_*.json"
        memory_files = list(SESSION_MEMORY_DIR.glob(pattern))
        
        if not memory_files:
            logger.warning(f"⚠️ 未找到 Session 記憶：{session_key}")
            return None
        
        # 取最新的檔案
        latest_file = max(memory_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            memory_data = json.load(f)
        
        logger.info(f"✅ 已載入 Session 記憶：{latest_file}")
        return memory_data
    
    def _generate_summary(self, context_data):
        """生成摘要"""
        if isinstance(context_data, dict):
            return context_data.get('summary', '無摘要')
        return str(context_data)[:200]
    
    def _extract_decisions(self, context_data):
        """提取重要決策"""
        decisions = []
        if isinstance(context_data, dict):
            decisions = context_data.get('decisions', [])
        return decisions
    
    def _extract_files(self, context_data):
        """提取相關檔案"""
        files = []
        if isinstance(context_data, dict):
            files = context_data.get('files', [])
        return files
    
    def create_spawn_config(self, task, agent_id, mode='run', need_memory=False, memory_key=None):
        """
        建立 Spawn 配置
        
        參數：
        - task: 任務描述
        - agent_id: Agent ID
        - mode: 'run' (一次性) 或 'session' (持續對話)
        - need_memory: 是否需要載入記憶
        - memory_key: 記憶鍵值
        """
        config = {
            'task': task,
            'label': f"{task[:30]}_{agent_id}",
            'runtime': 'subagent',
            'agentId': agent_id,
            'mode': mode,
            'timeout': 1800  # 30 分鐘
        }
        
        # 如果需要記憶延續
        if need_memory and memory_key:
            memory_data = self.load_session_memory(memory_key)
            if memory_data:
                # 在任務開頭注入記憶
                config['task'] = f"""
【記憶延續】
任務背景：{memory_data.get('summary', '無')}
重要決策：{memory_data.get('key_decisions', [])}
相關檔案：{memory_data.get('related_files', [])}

【新任務】
{task}
"""
        
        return config
    
    def classify_task_for_telegram(self, task_type, urgency='normal'):
        """
        分類任務以便透過 Telegram 回報
        
        分類規則：
        1. 緊急任務 → 立即通知董事長
        2. 系統異常 → 通知 + 要求確認
        3. 任務完成 → 彙整報告
        4. 常規進度 → 定時彙整
        """
        classification = {
            'critical': {
                'types': ['system_down', 'security_alert', 'data_loss'],
                'notify': True,
                'channel': 'direct',
                'format': 'immediate'
            },
            'high': {
                'types': ['task_failed', 'anomaly_detected', 'deadline_approaching'],
                'notify': True,
                'channel': 'direct',
                'format': 'detailed'
            },
            'normal': {
                'types': ['task_completed', 'report_generated', 'data_updated'],
                'notify': True,
                'channel': 'digest',
                'format': 'summary'
            },
            'low': {
                'types': ['routine_check', 'status_update', 'log_entry'],
                'notify': False,
                'channel': 'log',
                'format': 'minimal'
            }
        }
        
        # 根據緊急程度調整
        if urgency == 'urgent':
            return classification['high']
        elif urgency == 'critical':
            return classification['critical']
        
        # 根據任務類型分類
        for level, config in classification.items():
            if task_type in config['types']:
                return config
        
        return classification['low']
    
    def format_telegram_message(self, task_result, classification):
        """
        格式化 Telegram 訊息
        
        根據分類產生不同格式的訊息
        """
        if classification['format'] == 'immediate':
            # 緊急通知格式
            return f"""
🚨 **緊急通知**

**任務**: {task_result.get('task_name', '未知')}
**狀態**: ❌ 異常
**時間**: {task_result.get('timestamp', '未知')}

**詳情**:
{task_result.get('details', '無詳細資訊')}

**建議行動**:
{task_result.get('recommendation', '請立即檢查')}
"""
        
        elif classification['format'] == 'detailed':
            # 詳細報告格式
            return f"""
📊 **任務完成報告**

**任務**: {task_result.get('task_name', '未知')}
**執行 Agent**: {task_result.get('agent', '未知')}
**狀態**: ✅ 完成
**時間**: {task_result.get('timestamp', '未知')}
**耗時**: {task_result.get('duration', '未知')}

**執行結果**:
{task_result.get('result', '無結果')}

**關鍵發現**:
{task_result.get('findings', '無')}

**後續建議**:
{task_result.get('recommendations', '無')}
"""
        
        elif classification['format'] == 'summary':
            # 摘要格式
            return f"""
✅ **{task_result.get('task_name', '任務')}**

狀態：完成
Agent: {task_result.get('agent', '未知')}
時間：{task_result.get('timestamp', '未知')}

摘要：{task_result.get('summary', '無')}
"""
        
        else:
            # 最小格式（僅記錄）
            return f"[{task_result.get('timestamp', '')}] {task_result.get('task_name', '任務')}: {task_result.get('status', '完成')}"
    
    def should_send_to_telegram(self, classification):
        """判斷是否應該發送到 Telegram"""
        return classification['notify']
    
    def get_telegram_channel(self, classification):
        """取得 Telegram 頻道"""
        if classification['channel'] == 'direct':
            return 'telegram:8540722112'  # 董事長私人頻道
        elif classification['channel'] == 'digest':
            return 'telegram:8540722112'  # 彙整頻道（目前同私人）
        else:
            return None  # 僅記錄，不發送

def main():
    """測試 Session 管理器"""
    logger.info("=" * 70)
    logger.info("🔄 Session 管理器測試")
    logger.info("=" * 70)
    
    manager = SessionManager()
    
    # 測試 1: 判斷是否需要新 Session
    logger.info("\n📊 測試 1: Session 長度判斷")
    test_cases = [
        (50000, "短對話"),
        (100000, "中等對話"),
        (200000, "長對話"),
        (500000, "超長對話")
    ]
    
    for length, desc in test_cases:
        need_new = manager.should_spawn_new_session(length)
        status = "✅ 需要新 Session" if need_new else "⚠️ 可继续使用"
        logger.info(f"  {desc} ({length} 字元): {status}")
    
    # 測試 2: 任務分類
    logger.info("\n📊 測試 2: Telegram 任務分類")
    task_tests = [
        ('system_down', 'critical'),
        ('task_completed', 'normal'),
        ('anomaly_detected', 'high'),
        ('routine_check', 'low')
    ]
    
    for task_type, urgency in task_tests:
        classification = manager.classify_task_for_telegram(task_type, urgency)
        should_send = manager.should_send_to_telegram(classification)
        channel = manager.get_telegram_channel(classification)
        
        logger.info(f"  {task_type} ({urgency}):")
        logger.info(f"    通知：{'✅ 是' if should_send else '❌ 否'}")
        logger.info(f"    頻道：{channel or '僅記錄'}")
        logger.info(f"    格式：{classification['format']}")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ Session 管理器測試完成！")
    logger.info("=" * 70)

if __name__ == '__main__':
    main()
