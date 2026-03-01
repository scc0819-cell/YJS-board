#!/usr/bin/env python3
"""
昱金生能源 - 子代理任務執行器
執行 A+B+C 計劃並透過 Telegram 分類回報
"""

import json
from pathlib import Path
from datetime import datetime
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路徑設定
WORKSPACE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
TASK_REPORT_DIR = WORKSPACE_DIR / 'daily_report_attachments' / 'subagent_reports'
TASK_REPORT_DIR.mkdir(parents=True, exist_ok=True)

class SubAgentExecutor:
    """子代理任務執行器"""
    
    def __init__(self):
        self.tasks = []
        self.results = []
    
    def spawn_auo_scanner(self):
        """Spawn Argus 執行 AUO 完整掃描"""
        task_config = {
            'task': '''
【任務：AUO 友達電廠完整掃描】

請執行以下步驟：
1. 使用 browser 工具登入 AUO 系統
   - 網址：https://gms.auo.com/MvcWebPortal
   - 帳號：johnnys@yjsenergy.com
   - 密碼：5295Song!

2. 掃描所有 9 頁案場
   - 第 1 頁已完成（10 個案場）
   - 需要掃描第 2-9 頁（約 80-90 個案場）

3. 提取每個案場的詳細數據：
   - 案場名稱
   - 裝置容量 (kW)
   - 異常數量
   - DR 編號
   - 最後回報時間
   - 縣市
   - 發電量（如有）
   - PR 值（如有）

4. 生成深度分析報告：
   - 案場總覽（總數、總容量）
   - 異常案場清單（需立即處理）
   - 縣市分佈統計
   - TOP 10 大容量案場
   - 發電績效分析
   - 建議行動（立即/本週/長期）

5. 輸出檔案：
   - Markdown 報告：`auo_analysis_YYYYMMDD.md`
   - JSON 數據：`auo_cases_YYYYMMDD.json`
   - 存放位置：`daily_report_attachments/auo_monitoring/`

6. 回報方式：
   - 完成後透過 Telegram 發送詳細報告
   - 包含關鍵數據摘要
   - 標註需要立即處理的異常案場

請開始執行！
''',
            'label': 'AUO 完整掃描_Argus',
            'runtime': 'subagent',
            'agentId': 'argus',
            'mode': 'run',
            'timeout': 1800  # 30 分鐘
        }
        
        return task_config
    
    def spawn_case_finalization(self):
        """Spawn Scribe 執行案場名稱定稿"""
        task_config = {
            'task': '''
【任務：案場名稱一次性定稿】

請執行以下步驟：
1. 掃描 365 天郵件歷史
   - 路徑：`daily_report_server/email_cache/`
   - 時間範圍：2025-03-01 至 2026-03-01

2. 提取所有案場名稱變體
   - 使用模糊匹配
   - 識別同一案場的不同命名方式
   - 例如：「雲林東勢_金田畜牧場」vs「金田畜牧場（雲林東勢）」

3. 建立案場名稱對照表
   - 標準名稱（選擇最完整/最常用的）
   - 別名列表（所有變體）
   - 案場 ID（如有）

4. 寫入資料庫
   - 檔案：`daily_report_server/data/case_names_final.json`
   - 格式：JSON
   - 包含：標準名稱、別名、使用次數、最後更新

5. 生成報告：
   - 總案場數
   - 名稱變體統計
   - 修正對照表
   - 輸出：`case_name_finalization_report.md`

6. 後續處理：
   - 完成後建議停用 `case_name_finalization.py` 排程
   - 此為一次性任務

7. 回報方式：
   - 完成後透過 Telegram 發送摘要報告
   - 包含案場數量、修正數量

請開始執行！
''',
            'label': '案場名稱定稿_Scribe',
            'runtime': 'subagent',
            'agentId': 'scribe',
            'mode': 'run',
            'timeout': 1800  # 30 分鐘
        }
        
        return task_config
    
    def spawn_context_monitor(self):
        """Spawn Chronos 執行上下文監控"""
        task_config = {
            'task': '''
【任務：上下文長度監控與 Session 管理】

請執行以下步驟：
1. 檢查當前 Session 的上下文長度
   - 估算 token 數量
   - 檢查是否超過閾值（100,000 tokens）

2. 如果超過閾值：
   A. 保存當前 Session 記憶
      - 提取重要決策
      - 記錄相關檔案路徑
      - 生成摘要
   
   B. 建議新開 Session
      - 提供新 Session 的啟動指令
      - 包含記憶載入機制
   
   C. 建立記憶延續機制
      - 保存點：`session_memory/`
      - 格式：JSON
      - 包含：摘要、決策、檔案

3. 監控規則：
   - 每 30 分鐘檢查一次
   - 超過 80% 閾值時預警
   - 超過 100% 時建議新開 Session

4. 回報方式：
   - 常規：僅記錄（不發送 Telegram）
   - 預警：Telegram 摘要報告
   - 緊急：Telegram 詳細報告 + 建議行動

請開始執行！
''',
            'label': '上下文監控_Chronos',
            'runtime': 'subagent',
            'agentId': 'chronos',
            'mode': 'session',  # 持續監控
            'timeout': 3600  # 60 分鐘
        }
        
        return task_config
    
    def format_telegram_report(self, task_name, agent, status, details):
        """格式化 Telegram 報告"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if status == 'completed':
            emoji = '✅'
            status_text = '完成'
        elif status == 'failed':
            emoji = '❌'
            status_text = '失敗'
        elif status == 'running':
            emoji = '🔄'
            status_text = '執行中'
        else:
            emoji = '⏳'
            status_text = '待處理'
        
        report = f"""
{emoji} **{task_name}**

**執行 Agent**: {agent}
**狀態**: {status_text}
**時間**: {timestamp}

**詳細資訊**:
{details}
"""
        return report
    
    def save_task_result(self, task_name, agent, status, details):
        """保存任務結果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = TASK_REPORT_DIR / f"{task_name}_{timestamp}.json"
        
        result = {
            'task_name': task_name,
            'agent': agent,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 已保存任務結果：{result_file}")
        return result_file

def main():
    """主函數"""
    logger.info("=" * 70)
    logger.info("🚀 昱金生能源 - 子代理任務執行器")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    executor = SubAgentExecutor()
    
    # 任務 A: 開啟視覺化看板
    logger.info("\n📊 任務 A: 視覺化任務看板")
    logger.info(f"✅ 看板已建立：{WORKSPACE_DIR}/task-board-dashboard-v2.html")
    logger.info("📋 請在瀏覽器中開啟此檔案查看")
    logger.info("💡 提示：可使用 `openclaw browser` 或手動開啟")
    
    # 任務 B: Spawn 子代理執行任務
    logger.info("\n🚀 任務 B: Spawn 子代理")
    
    # B1: AUO 完整掃描
    logger.info("\n🏭 子代理 1: AUO 完整掃描 (Argus)")
    auo_config = executor.spawn_auo_scanner()
    logger.info(f"  任務：{auo_config['label']}")
    logger.info(f"  Agent: {auo_config['agentId']}")
    logger.info(f"  模式：{auo_config['mode']}")
    logger.info(f"  超時：{auo_config['timeout']}秒")
    logger.info("  ✅ 配置已準備完成")
    
    # B2: 案場名稱定稿
    logger.info("\n📧 子代理 2: 案場名稱定稿 (Scribe)")
    case_config = executor.spawn_case_finalization()
    logger.info(f"  任務：{case_config['label']}")
    logger.info(f"  Agent: {case_config['agentId']}")
    logger.info(f"  模式：{case_config['mode']}")
    logger.info(f"  超時：{case_config['timeout']}秒")
    logger.info("  ✅ 配置已準備完成")
    
    # B3: 上下文監控
    logger.info("\n🔄 子代理 3: 上下文監控 (Chronos)")
    ctx_config = executor.spawn_context_monitor()
    logger.info(f"  任務：{ctx_config['label']}")
    logger.info(f"  Agent: {ctx_config['agentId']}")
    logger.info(f"  模式：{ctx_config['mode']}")
    logger.info(f"  超時：{ctx_config['timeout']}秒")
    logger.info("  ✅ 配置已準備完成")
    
    # 任務 C: 完成 AUO 掃描
    logger.info("\n🏭 任務 C: AUO 掃描執行")
    logger.info("⏳ 等待 Argus 子代理執行...")
    
    # 保存任務配置
    logger.info("\n📋 保存任務配置")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    config_file = TASK_REPORT_DIR / f"subagent_configs_{timestamp}.json"
    
    configs = {
        'auo_scanner': auo_config,
        'case_finalization': case_config,
        'context_monitor': ctx_config
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(configs, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ 已保存配置：{config_file}")
    
    # 生成 Telegram 報告預覽
    logger.info("\n📱 Telegram 報告預覽")
    
    report_a = executor.format_telegram_report(
        '視覺化任務看板',
        'Jenny',
        'completed',
        f'看板已建立：task-board-dashboard-v2.html\n包含 18 項任務、6 人 Agent 團隊、完整排程表'
    )
    logger.info(report_a)
    
    report_b = executor.format_telegram_report(
        'AUO 完整掃描',
        'Argus',
        'running',
        '已 spawn 子代理，預計 30 分鐘內完成\n將掃描 9 頁案場，生成深度分析報告'
    )
    logger.info(report_b)
    
    report_c = executor.format_telegram_report(
        '案場名稱定稿',
        'Scribe',
        'running',
        '已 spawn 子代理，預計 30 分鐘內完成\n將掃描 365 天郵件，一次性定稿'
    )
    logger.info(report_c)
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ 子代理任務執行器完成！")
    logger.info("=" * 70)
    logger.info("\n📋 下一步:")
    logger.info("1. 在瀏覽器中開啟看板：task-board-dashboard-v2.html")
    logger.info("2. 等待子代理完成任務")
    logger.info("3. 檢視 Telegram 報告")
    logger.info("4. 檢查生成的報告檔案")
    
    # 返回 spawn 配置（供 main agent 使用）
    return {
        'auo_scanner': auo_config,
        'case_finalization': case_config,
        'context_monitor': ctx_config
    }

if __name__ == '__main__':
    result = main()
    # 如果是直接執行，輸出 JSON 配置
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
