#!/usr/bin/env python3
"""
昱金生能源 - 子代理任務管理器
動態分派任務給子代理，實現自我演化
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
TASK_BOARD_FILE = WORKSPACE_DIR / 'task-board.json'
AGENT_CONFIG_FILE = WORKSPACE_DIR / 'agent-team.json'

# Agent 團隊配置
AGENT_TEAM = {
    'jenny': {
        'name': 'Jenny',
        'role': '主助理',
        'specialties': ['綜合任務', '決策協調', '任務分派'],
        'status': 'active',
        'tasks_assigned': 8,
        'emoji': '🎯'
    },
    'argus': {
        'name': 'Argus',
        'role': '監控專家',
        'specialties': ['系統監控', '異常偵測', '告警通知'],
        'status': 'active',
        'tasks_assigned': 4,
        'emoji': '👁️'
    },
    'scribe': {
        'name': 'Scribe',
        'role': '報告專家',
        'specialties': ['報表生成', '文件整理', '數據匯出'],
        'status': 'active',
        'tasks_assigned': 6,
        'emoji': '📝'
    },
    'chronos': {
        'name': 'Chronos',
        'role': '排程專家',
        'specialties': ['排程管理', '任務分配', '時間優化'],
        'status': 'active',
        'tasks_assigned': 3,
        'emoji': '⏰'
    },
    'athena': {
        'name': 'Athena',
        'role': '分析專家',
        'specialties': ['數據分析', '決策支援', '趨勢預測'],
        'status': 'active',
        'tasks_assigned': 3,
        'emoji': '🧠'
    },
    'hermes': {
        'name': 'Hermes',
        'role': '通訊專家',
        'specialties': ['郵件處理', '訊息通知', '對外通訊'],
        'status': 'active',
        'tasks_assigned': 2,
        'emoji': '📧'
    }
}

# 任務模板
TASK_TEMPLATES = {
    'monitoring': {
        'type': 'monitoring',
        'priority': 'high',
        'auto_retry': True,
        'timeout_minutes': 30
    },
    'analysis': {
        'type': 'analysis',
        'priority': 'medium',
        'auto_retry': True,
        'timeout_minutes': 60
    },
    'report': {
        'type': 'report',
        'priority': 'medium',
        'auto_retry': False,
        'timeout_minutes': 45
    },
    'optimization': {
        'type': 'optimization',
        'priority': 'low',
        'auto_retry': True,
        'timeout_minutes': 90
    }
}

def load_task_board():
    """載入任務看板"""
    if TASK_BOARD_FILE.exists():
        with open(TASK_BOARD_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 確保 tasks 鍵存在
            if 'tasks' not in data:
                data['tasks'] = []
            return data
    return {'tasks': [], 'agents': AGENT_TEAM}

def save_task_board(data):
    """儲存任務看板"""
    with open(TASK_BOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ 已儲存任務看板：{TASK_BOARD_FILE}")

def create_task(name, description, agent_id, task_type='general', priority='medium'):
    """建立新任務"""
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    task = {
        'id': task_id,
        'name': name,
        'description': description,
        'agent_id': agent_id,
        'type': task_type,
        'priority': priority,
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'started_at': None,
        'completed_at': None,
        'result': None,
        'retry_count': 0
    }
    
    # 套用模板
    if task_type in TASK_TEMPLATES:
        task.update(TASK_TEMPLATES[task_type])
    
    return task

def assign_task(task, agent_id):
    """分派任務給 Agent"""
    if agent_id not in AGENT_TEAM:
        logger.error(f"❌ Agent {agent_id} 不存在")
        return False
    
    task['agent_id'] = agent_id
    task['status'] = 'assigned'
    task['assigned_at'] = datetime.now().isoformat()
    
    # 更新 Agent 任務計數
    AGENT_TEAM[agent_id]['tasks_assigned'] += 1
    
    logger.info(f"✅ 任務 {task['name']} 已分派給 {AGENT_TEAM[agent_id]['name']}")
    return True

def spawn_subagent(task, mode='run'):
    """Spawn 子代理執行任務"""
    logger.info(f"🚀 準備 spawn 子代理執行任務：{task['name']}")
    
    # 這裡會調用 sessions_spawn 工具
    # 由於這是參考腳本，實際執行需要在 main agent 中進行
    
    spawn_config = {
        'task': task['description'],
        'label': f"{task['name']}_{task['agent_id']}",
        'runtime': 'subagent',
        'agentId': task['agent_id'],
        'mode': mode,
        'timeout': task.get('timeout_minutes', 30) * 60
    }
    
    logger.info(f"📋 Spawn 配置：{json.dumps(spawn_config, indent=2)}")
    return spawn_config

def complete_task(task_id, result):
    """完成任務"""
    task_board = load_task_board()
    
    for task in task_board['tasks']:
        if task['id'] == task_id:
            task['status'] = 'completed'
            task['completed_at'] = datetime.now().isoformat()
            task['result'] = result
            logger.info(f"✅ 任務 {task['name']} 已完成")
            break
    
    save_task_board(task_board)

def get_agent_workload():
    """取得 Agent 工作負載"""
    workload = {}
    for agent_id, agent in AGENT_TEAM.items():
        workload[agent_id] = {
            'name': agent['name'],
            'tasks': agent['tasks_assigned'],
            'status': agent['status'],
            'capacity': 'high' if agent['tasks_assigned'] < 3 else 'medium' if agent['tasks_assigned'] < 6 else 'low'
        }
    return workload

def auto_assign_task(task_name, description, task_type='general'):
    """自動分派任務（根據工作負載）"""
    workload = get_agent_workload()
    
    # 根據任務類型選擇合適的 Agent
    agent_mapping = {
        'monitoring': 'argus',
        'analysis': 'athena',
        'report': 'scribe',
        'optimization': 'chronos',
        'communication': 'hermes',
        'general': 'jenny'
    }
    
    preferred_agent = agent_mapping.get(task_type, 'jenny')
    
    # 檢查首選 Agent 的工作負載
    if workload[preferred_agent]['capacity'] != 'low':
        agent_id = preferred_agent
    else:
        # 選擇工作負載最低的 Agent
        agent_id = min(workload.keys(), key=lambda x: workload[x]['tasks'])
    
    # 建立任務
    task = create_task(task_name, description, agent_id, task_type)
    
    # 分派任務
    assign_task(task, agent_id)
    
    # 加入任務看板
    task_board = load_task_board()
    task_board['tasks'].append(task)
    save_task_board(task_board)
    
    # Spawn 子代理
    spawn_config = spawn_subagent(task)
    
    return {
        'task': task,
        'agent_id': agent_id,
        'spawn_config': spawn_config
    }

def generate_status_report():
    """生成狀態報告"""
    task_board = load_task_board()
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tasks': len(task_board['tasks']),
        'by_status': {},
        'agents': AGENT_TEAM
    }
    
    # 統計各狀態任務數
    for task in task_board['tasks']:
        status = task['status']
        report['by_status'][status] = report['by_status'].get(status, 0) + 1
    
    return report

def main():
    """主函數 - 示範用法"""
    logger.info("=" * 70)
    logger.info("🤖 昱金生能源 - 子代理任務管理器")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 初始化任務看板
    task_board = load_task_board()
    task_board['agents'] = AGENT_TEAM
    save_task_board(task_board)
    logger.info("✅ 任務看板已初始化")
    
    # 示範：自動分派任務
    logger.info("\n📋 示範：自動分派任務")
    
    # 任務 1: AUO 完整掃描
    result = auto_assign_task(
        task_name='🏭 AUO 完整案場掃描',
        description='完成剩餘 7 頁案場數據提取，生成深度分析報告',
        task_type='monitoring'
    )
    logger.info(f"✅ 任務已分派給 {AGENT_TEAM[result['agent_id']]['name']}")
    
    # 任務 2: 案場名稱定稿
    result = auto_assign_task(
        task_name='📧 案場名稱定稿',
        description='掃描 365 天郵件，一次性提取並定稿案場名稱',
        task_type='report'
    )
    logger.info(f"✅ 任務已分派給 {AGENT_TEAM[result['agent_id']]['name']}")
    
    # 生成狀態報告
    report = generate_status_report()
    logger.info("\n📊 狀態報告:")
    logger.info(f"  總任務數：{report['total_tasks']}")
    logger.info(f"  各狀態：{report['by_status']}")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ 子代理任務管理完成！")
    logger.info("=" * 70)

if __name__ == '__main__':
    main()
