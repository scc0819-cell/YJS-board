#!/usr/bin/env python3
"""
昱金生能源 - 子代理 Telegram 回報流程設計
實作統一管理 + 緊急越級機制
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

class SubAgentTelegramFlow:
    """子代理 Telegram 回報流程"""
    
    def __init__(self):
        self.chairman_chat_id = 'telegram:8540722112'
        self.jenny_status = 'active'  # active, timeout, down
        self.last_jenny_heartbeat = datetime.now()
        
        # 分類配置
        self.classifications = {
            'critical': {'level': 4, 'bypass': True, 'format': 'immediate'},
            'high': {'level': 3, 'bypass': True, 'format': 'detailed'},
            'normal': {'level': 2, 'bypass': False, 'format': 'summary'},
            'low': {'level': 1, 'bypass': False, 'format': 'minimal'}
        }
    
    def check_jenny_health(self):
        """檢查 Jenny 健康狀態"""
        now = datetime.now()
        time_diff = (now - self.last_jenny_heartbeat).total_seconds()
        
        if time_diff > 300:  # 5 分鐘無心跳
            self.jenny_status = 'down'
            logger.warning("⚠️ Jenny 已超過 5 分鐘無回應")
        elif time_diff > 60:  # 1 分鐘無心跳
            self.jenny_status = 'timeout'
            logger.warning("⏰ Jenny 回應超時")
        else:
            self.jenny_status = 'active'
        
        return self.jenny_status
    
    def jenny_heartbeat(self):
        """更新 Jenny 心跳"""
        self.last_jenny_heartbeat = datetime.now()
        self.jenny_status = 'active'
        logger.info("💓 Jenny 心跳更新")
    
    def should_bypass_jenny(self, classification_level, task_result):
        """
        判斷是否應該越級發送
        
        條件：
        1. Jenny 狀態異常（down/timeout）
        2. 任務等級為 critical 或 high
        3. 緊急情況需要立即通知
        """
        if classification_level not in ['critical', 'high']:
            return False
        
        if self.jenny_status in ['down', 'timeout']:
            logger.warning(f"🚨 啟動越級機制：{task_result.get('task_name', '未知任務')}")
            return True
        
        return False
    
    def format_message(self, task_result, classification, bypass=False):
        """
        格式化 Telegram 訊息
        
        統一格式，標註來源
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        agent = task_result.get('agent', 'Unknown')
        task_name = task_result.get('task_name', '未知任務')
        status = task_result.get('status', 'unknown')
        details = task_result.get('details', {})
        
        # 狀態對應
        status_emoji = {
            'completed': '✅',
            'failed': '❌',
            'running': '🔄',
            'critical': '🚨',
            'warning': '⚠️'
        }
        emoji = status_emoji.get(status, '📋')
        
        # 越級標註
        bypass_header = "【🚨越級通知】\n\n" if bypass else ""
        
        # 根據分類選擇格式
        if classification == 'critical':
            message = f"""
{bypass_header}{emoji} **緊急告警**

**任務**: {task_name}
**執行 Agent**: {agent}
**時間**: {timestamp}
**狀態**: {status.upper()}

━━━━━━━━━━━━━━━━━━━━

**詳細情況**:
{details.get('description', '無詳細資訊')}

**影響範圍**:
{details.get('impact', '未知')}

**建議立即行動**:
{details.get('action', '請立即檢查系統')}

━━━━━━━━━━━━━━━━━━━━
{'🔔 越級通知：Jenny 無回應，直接發送' if bypass else '🔔 此為緊急通知，請立即處理'}
"""
        
        elif classification == 'high':
            message = f"""
{bypass_header}{emoji} **重要報告**

**任務**: {task_name}
**執行 Agent**: {agent}
**時間**: {timestamp}

━━━━━━━━━━━━━━━━━━━━

**執行結果**:
{details.get('result', '無結果')}

**關鍵發現**:
{details.get('findings', '無')}

**後續建議**:
{details.get('recommendations', '無')}

━━━━━━━━━━━━━━━━━━━━
{'⚠️ 越級通知：Jenny 暫時無法回應' if bypass else '📊 詳細報告'}
"""
        
        elif classification == 'normal':
            message = f"""
{emoji} **{task_name}**

🤖 Agent: {agent}
⏰ 時間：{timestamp}
📊 狀態：{status.upper()}

{details.get('summary', details.get('result', '無'))}

✅ 任務已完成
"""
        
        else:  # low
            message = f"[{timestamp}] {task_name} ({agent}): {status}"
        
        return message
    
    def send_via_jenny(self, task_result, classification):
        """
        透過 Jenny 發送（常規流程）
        
        流程：
        1. 檢查 Jenny 狀態
        2. 格式化訊息
        3. 發送給 Jenny
        4. Jenny 統一發送
        """
        # 更新心跳
        self.jenny_heartbeat()
        
        # 格式化訊息
        message = self.format_message(task_result, classification)
        
        logger.info(f"📤 常規發送：{task_result.get('task_name', '未知')} → Jenny")
        
        # 這裡會調用 message 工具發送
        # 由於這是參考腳本，實際執行需要在 main agent 中進行
        
        return {
            'method': 'via_jenny',
            'message': message,
            'status': 'queued'
        }
    
    def send_direct(self, task_result, classification):
        """
        直接發送（越級流程）
        
        流程：
        1. 判斷是否滿足越級條件
        2. 格式化訊息（標註越級）
        3. 直接發送給董事長
        4. 記錄日誌
        """
        if not self.should_bypass_jenny(classification, task_result):
            logger.warning("⚠️ 不滿足越級條件，改為常規發送")
            return self.send_via_jenny(task_result, classification)
        
        # 格式化訊息（越級版本）
        message = self.format_message(task_result, classification, bypass=True)
        
        logger.info(f"🚨 越級發送：{task_result.get('task_name', '未知')} → Telegram")
        
        # 這裡會調用 message 工具直接發送
        # 由於這是參考腳本，實際執行需要在 main agent 中進行
        
        return {
            'method': 'direct',
            'message': message,
            'status': 'sent',
            'reason': f'Jenny {self.jenny_status}'
        }
    
    def send(self, task_result, classification):
        """
        統一發送接口
        
        自動判斷使用常規或越級流程
        """
        # 檢查 Jenny 健康
        self.check_jenny_health()
        
        # 判斷是否越級
        if self.should_bypass_jenny(classification, task_result):
            return self.send_direct(task_result, classification)
        else:
            return self.send_via_jenny(task_result, classification)
    
    def create_flowchart(self):
        """生成流程圖"""
        flowchart = """
# 📊 子代理 Telegram 回報流程圖

## 常規流程

```mermaid
graph TD
    A[子代理執行任務] --> B[生成報告]
    B --> C{判斷分類}
    C -->|Low| D[僅記錄，不發送]
    C -->|Normal| E[發送給 Jenny]
    C -->|High| F[發送給 Jenny]
    C -->|Critical| G[發送給 Jenny]
    E --> H[Jenny 彙整]
    F --> I[Jenny 立即發送]
    G --> J[Jenny 緊急發送]
    H --> K[定時彙整報告]
    I --> L[詳細報告]
    J --> M[緊急告警]
```

## 越級流程

```mermaid
graph TD
    A[子代理偵測 Critical/High] --> B[嘗試發送給 Jenny]
    B --> C{Jenny 回應？}
    C -->|是 | D[Jenny 正常發送]
    C -->|否 超時 30 秒 | E{是否緊急？}
    E -->|是 Critical/High| F[啟動越級機制]
    E -->|否 Normal/Low| G[記錄並等待]
    F --> H[直接發送 Telegram]
    H --> I[標註【越級通知】]
    I --> J[發送給董事長]
    G --> K[等待 Jenny 恢復]
```

## 完整決策流程

```mermaid
graph TD
    A[任務完成] --> B[生成報告]
    B --> C{分類等級？}
    C -->|Low| D[僅記錄]
    C -->|Normal| E[常規發送]
    C -->|High| F[檢查 Jenny]
    C -->|Critical| F
    F --> G{Jenny 狀態？}
    G -->|active| H[Jenny 發送]
    G -->|timeout| I{是否緊急？}
    G -->|down| I
    I -->|是 | J[越級發送]
    I -->|否 | K[等待並記錄]
    H --> L[完成]
    J --> L
    K --> L
    D --> L
    E --> L
```

## 狀態轉換

```mermaid
stateDiagram-v2
    [*] --> Active: 系統啟動
    Active --> Timeout: 60 秒無回應
    Timeout --> Active: 收到心跳
    Timeout --> Down: 300 秒無回應
    Down --> Active: 服務恢復
    Down --> [*]: 系統關閉
```
"""
        return flowchart

def demo():
    """示範流程"""
    logger.info("=" * 70)
    logger.info("📊 子代理 Telegram 回報流程示範")
    logger.info("=" * 70)
    
    flow = SubAgentTelegramFlow()
    
    # 示範 1: 常規任務完成
    logger.info("\n✅ 示範 1: 任務完成（Normal）")
    task_result = {
        'task_name': '案場名稱定稿',
        'agent': 'Scribe',
        'status': 'completed',
        'details': {
            'summary': '完成 365 天郵件掃描，提取 401 個案場'
        }
    }
    result = flow.send(task_result, 'normal')
    logger.info(f"  發送方式：{result['method']}")
    logger.info(f"  狀態：{result['status']}")
    
    # 示範 2: 緊急告警（Jenny 正常）
    logger.info("\n🚨 示範 2: 緊急告警（Jenny 正常）")
    flow.jenny_heartbeat()  # 更新心跳
    task_result = {
        'task_name': '系統異常：日報服務當機',
        'agent': 'Argus',
        'status': 'critical',
        'details': {
            'description': '日報服務當機，無法回應',
            'impact': '員工無法提交日報',
            'action': '立即重啟服務'
        }
    }
    result = flow.send(task_result, 'critical')
    logger.info(f"  發送方式：{result['method']}")
    logger.info(f"  狀態：{result['status']}")
    
    # 示範 3: 緊急告警（Jenny 異常，觸發越級）
    logger.info("\n🚨 示範 3: 緊急告警（Jenny 異常，越級）")
    flow.jenny_status = 'down'  # 模擬 Jenny 異常
    result = flow.send(task_result, 'critical')
    logger.info(f"  發送方式：{result['method']}")
    logger.info(f"  狀態：{result['status']}")
    logger.info(f"  越級原因：{result.get('reason', '無')}")
    
    # 顯示流程圖
    logger.info("\n📊 流程圖已生成")
    flowchart = flow.create_flowchart()
    logger.info(f"  字元數：{len(flowchart)}")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ 流程示範完成！")
    logger.info("=" * 70)

if __name__ == '__main__':
    demo()
