#!/usr/bin/env python3
"""
昱金生能源 - Telegram 分類回報系統
根據任務類型和緊急程度，分類發送報告到 Telegram
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
TELEGRAM_REPORTS_DIR = WORKSPACE_DIR / 'daily_report_attachments' / 'telegram_reports'
TELEGRAM_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

class TelegramReporter:
    """Telegram 分類回報器"""
    
    def __init__(self):
        # 董事長 Telegram ID（從 inbound context 取得）
        self.chairman_chat_id = 'telegram:8540722112'
        
        # 任務分類配置
        self.classifications = {
            'critical': {
                'types': ['system_down', 'security_alert', 'data_loss', 'service_crash'],
                'notify': True,
                'priority': 'high',
                'format': 'immediate',
                'sound': True,
                'description': '🚨 緊急告警 - 立即通知'
            },
            'high': {
                'types': ['task_failed', 'anomaly_detected', 'deadline_approaching', 'error_critical'],
                'notify': True,
                'priority': 'high',
                'format': 'detailed',
                'sound': True,
                'description': '⚠️ 重要通知 - 詳細報告'
            },
            'normal': {
                'types': ['task_completed', 'report_generated', 'data_updated', 'scan_completed'],
                'notify': True,
                'priority': 'normal',
                'format': 'summary',
                'sound': False,
                'description': '✅ 任務完成 - 摘要報告'
            },
            'low': {
                'types': ['routine_check', 'status_update', 'log_entry', 'heartbeat_ok'],
                'notify': False,
                'priority': 'low',
                'format': 'minimal',
                'sound': False,
                'description': '📝 常規記錄 - 不發送'
            }
        }
        
        # Agent 分類映射（用於子代理回報）
        self.agent_categories = {
            'argus': 'monitoring',    # 監控類
            'scribe': 'report',       # 報告類
            'chronos': 'schedule',    # 排程類
            'athena': 'analysis',     # 分析類
            'hermes': 'communication',# 通訊類
            'jenny': 'general'        # 綜合類
        }
    
    def classify_task(self, task_type, agent=None, urgency='normal'):
        """
        分類任務
        
        參數：
        - task_type: 任務類型（如 'task_completed', 'anomaly_detected'）
        - agent: 執行 Agent（用於輔助分類）
        - urgency: 緊急程度（'critical', 'high', 'normal', 'low'）
        """
        # 如果指定了緊急程度，直接調整
        if urgency in self.classifications:
            base_config = self.classifications[urgency].copy()
            base_config['urgency_override'] = True
            return base_config
        
        # 根據任務類型分類
        for level, config in self.classifications.items():
            if task_type in config['types']:
                return config.copy()
        
        # 預設為 low
        return self.classifications['low'].copy()
    
    def format_message(self, task_name, agent, status, details, classification):
        """
        格式化 Telegram 訊息
        
        根據分類產生不同格式
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 狀態對應
        status_emoji = {
            'completed': '✅',
            'failed': '❌',
            'running': '🔄',
            'pending': '⏳',
            'warning': '⚠️',
            'critical': '🚨'
        }
        
        emoji = status_emoji.get(status, '📋')
        
        if classification['format'] == 'immediate':
            # 緊急通知格式
            message = f"""
{emoji} **緊急告警**

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
🔔 此為緊急通知，請立即處理
"""
        
        elif classification['format'] == 'detailed':
            # 詳細報告格式
            message = f"""
{emoji} **任務報告**

**任務**: {task_name}
**執行 Agent**: {agent}
**時間**: {timestamp}
**狀態**: {status.upper()}

━━━━━━━━━━━━━━━━━━━━

**執行結果**:
{details.get('result', '無結果')}

**關鍵發現**:
{details.get('findings', '無')}

**數據摘要**:
{details.get('summary', '無')}

**後續建議**:
{details.get('recommendations', '無')}

━━━━━━━━━━━━━━━━━━━━
📊 詳細報告已儲存至系統
"""
        
        elif classification['format'] == 'summary':
            # 摘要格式
            message = f"""
{emoji} **{task_name}**

🤖 Agent: {agent}
⏰ 時間：{timestamp}
📊 狀態：{status.upper()}

{details.get('summary', details.get('result', '無'))}

✅ 任務已完成
"""
        
        else:
            # 最小格式（僅記錄）
            message = f"[{timestamp}] {task_name} ({agent}): {status}"
        
        return message
    
    def should_send(self, classification):
        """判斷是否應該發送"""
        return classification['notify']
    
    def get_priority(self, classification):
        """取得發送優先級"""
        return classification['priority']
    
    def save_report(self, task_name, agent, status, details, classification):
        """保存報告到檔案"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = TELEGRAM_REPORTS_DIR / f"{task_name}_{timestamp}.json"
        
        report = {
            'task_name': task_name,
            'agent': agent,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'classification': classification,
            'details': details,
            'message_preview': self.format_message(task_name, agent, status, details, classification)
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 已保存報告：{report_file}")
        return report_file
    
    def create_digest_report(self, reports):
        """
        建立彙整報告
        
        參數：
        - reports: 報告列表 [{task_name, agent, status, details}, ...]
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 統計
        total = len(reports)
        completed = sum(1 for r in reports if r['status'] == 'completed')
        failed = sum(1 for r in reports if r['status'] == 'failed')
        running = sum(1 for r in reports if r['status'] == 'running')
        
        message = f"""
📊 **每日任務彙整報告**

⏰ 時間：{timestamp}

━━━━━━━━━━━━━━━━━━━━

**統計**:
✅ 完成：{completed}
❌ 失敗：{failed}
🔄 執行中：{running}
📋 總計：{total}

━━━━━━━━━━━━━━━━━━━━

**完成任務**:
"""
        
        for report in reports:
            if report['status'] == 'completed':
                message += f"\n✅ {report['task_name']} ({report['agent']})"
        
        if failed > 0:
            message += "\n\n**失敗任務**:\n"
            for report in reports:
                if report['status'] == 'failed':
                    message += f"\n❌ {report['task_name']} ({report['agent']})"
        
        if running > 0:
            message += "\n\n**執行中任務**:\n"
            for report in reports:
                if report['status'] == 'running':
                    message += f"\n🔄 {report['task_name']} ({report['agent']})"
        
        message += "\n\n━━━━━━━━━━━━━━━━━━━━\n"
        message += "📋 詳細報告請查看系統檔案\n"
        
        return message

def demo():
    """示範用法"""
    logger.info("=" * 70)
    logger.info("📱 Telegram 分類回報系統示範")
    logger.info("=" * 70)
    
    reporter = TelegramReporter()
    
    # 示範 1: 緊急告警
    logger.info("\n🚨 示範 1: 緊急告警")
    classification = reporter.classify_task('system_down', urgency='critical')
    logger.info(f"  分類：{classification['description']}")
    logger.info(f"  發送：{'✅ 是' if reporter.should_send(classification) else '❌ 否'}")
    logger.info(f"  格式：{classification['format']}")
    
    details = {
        'description': '日報服務當機，無法回應請求',
        'impact': '員工無法提交日報，系統功能中斷',
        'action': '立即重啟服務並檢查日誌'
    }
    
    message = reporter.format_message(
        '系統異常：日報服務當機',
        'Argus',
        'critical',
        details,
        classification
    )
    logger.info(f"\n  訊息預覽:\n{message}")
    
    # 示範 2: 任務完成
    logger.info("\n✅ 示範 2: 任務完成")
    classification = reporter.classify_task('task_completed', agent='scribe')
    logger.info(f"  分類：{classification['description']}")
    logger.info(f"  發送：{'✅ 是' if reporter.should_send(classification) else '❌ 否'}")
    
    details = {
        'result': '已掃描 365 天郵件，提取 401 個案場名稱',
        'summary': '完成案場名稱定稿，建立對照表',
        'recommendations': '可停用 case_name_finalization.py 排程'
    }
    
    message = reporter.format_message(
        '案場名稱定稿',
        'Scribe',
        'completed',
        details,
        classification
    )
    logger.info(f"\n  訊息預覽:\n{message}")
    
    # 示範 3: 常規檢查
    logger.info("\n📝 示範 3: 常規檢查")
    classification = reporter.classify_task('routine_check', agent='chronos')
    logger.info(f"  分類：{classification['description']}")
    logger.info(f"  發送：{'✅ 是' if reporter.should_send(classification) else '❌ 否'}")
    
    # 示範 4: 彙整報告
    logger.info("\n📊 示範 4: 彙整報告")
    reports = [
        {'task_name': 'AUO 掃描', 'agent': 'Argus', 'status': 'completed', 'details': {}},
        {'task_name': '案場名稱定稿', 'agent': 'Scribe', 'status': 'completed', 'details': {}},
        {'task_name': '上下文監控', 'agent': 'Chronos', 'status': 'running', 'details': {}}
    ]
    
    digest = reporter.create_digest_report(reports)
    logger.info(f"\n  彙整報告預覽:\n{digest}")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ Telegram 分類回報系統示範完成！")
    logger.info("=" * 70)

if __name__ == '__main__':
    demo()
