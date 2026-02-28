#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任務看板動態更新腳本
功能：從 task-board.json 讀取數據，更新 HTML 看板
"""

import json
from pathlib import Path
from datetime import datetime

def load_task_board():
    """載入任務看板數據"""
    board_path = Path.home() / '.openclaw' / 'workspace' / 'task-board.json'
    if board_path.exists():
        with open(board_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_memory():
    """載入記憶數據"""
    memory_dir = Path.home() / '.openclaw' / 'workspace' / 'memory'
    today = datetime.now().strftime('%Y-%m-%d')
    memory_path = memory_dir / f'{today}.md'
    
    if memory_path.exists():
        with open(memory_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取記憶條目
            memories = []
            for line in content.split('\n'):
                if line.startswith('### mem-'):
                    memories.append(line)
            return memories[:10]  # 最近 10 條
    return []

def generate_dashboard_html(data):
    """生成動態 HTML 看板"""
    
    tasks = data.get('tasks', [])
    agents = data.get('agents', {})
    
    # 分類任務
    pending = [t for t in tasks if t.get('status') == 'pending']
    running = [t for t in tasks if t.get('status') == 'running']
    completed = [t for t in tasks if t.get('status') == 'completed']
    
    # 統計
    stats = {
        'total': len(tasks),
        'pending': len(pending),
        'running': len(running),
        'completed': len(completed),
        'agents': len(agents)
    }
    
    # 生成任務卡片 HTML
    def task_card(task):
        agent_info = agents.get(task.get('agent'), {})
        agent_name = agent_info.get('name', task.get('agent', 'Unknown'))
        agent_emoji = agent_info.get('emoji', '🤖')
        time = task.get('createdAt', '')[:16].replace('T', ' ')
        priority = task.get('priority', 'medium')
        
        return f'''
        <div class="task-card" onclick="showTaskDetails('{task.get('id', '')}')">
            <div class="task-header">
                <div class="task-title">{task.get('name', 'Unnamed Task')}</div>
            </div>
            <span class="task-agent agent-{task.get('agent', 'unknown')}">{agent_emoji} {agent_name}</span>
            <div class="task-description">{task.get('description', '')}</div>
            <div class="task-meta">
                <div class="task-time">⏰ {time}</div>
                <span class="task-priority priority-{priority}">{priority}</span>
            </div>
        </div>
        '''
    
    # 生成 Agent 卡片 HTML
    def agent_card(agent_id, agent):
        status_class = 'active' if agent.get('status') == 'active' else 'standby'
        status_text = '運作中' if agent.get('status') == 'active' else '待命中'
        status_badge = 'status-active' if agent.get('status') == 'active' else 'status-standby'
        
        return f'''
        <div class="agent-card {status_class}" onclick="spawnAgent('{agent_id}')">
            <div class="agent-avatar">{agent.get('emoji', '🤖')}</div>
            <div class="agent-name">{agent.get('name', agent_id)}</div>
            <div class="agent-role">{agent.get('role', '')}</div>
            <div class="agent-stats">專長：{agent.get('specialty', '')}</div>
            <div class="agent-stats">完成任務：{agent.get('tasksCompleted', 0)}</div>
            <span class="agent-status {status_badge}">{status_text}</span>
        </div>
        '''
    
    # 生成改善項目 HTML
    improvements = load_memory()
    improvement_html = ''
    if improvements:
        for mem in improvements[:5]:
            improvement_html += f'''
            <div class="improvement-item">
                <div class="improvement-title">{mem}</div>
            </div>
            '''
    else:
        improvement_html = '''
        <div class="improvement-item">
            <div class="improvement-title">系統剛建立，等待改善記錄...</div>
            <div class="improvement-metric">開始追蹤後，這裡會顯示任務效率提升、準確率改善等數據</div>
        </div>
        '''
    
    # 組合完整 HTML（簡化版，實際應該讀取完整模板）
    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦞 OpenClaw 任務管理看板</title>
    <style>
        /* 這裡插入完整的 CSS，為節省空間省略 */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        header {{ background: white; padding: 20px 30px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .stats-bar {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .stat-item {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 20px; border-radius: 8px; min-width: 150px; text-align: center; }}
        .stat-number {{ font-size: 32px; font-weight: bold; }}
        .board {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .column {{ background: #f1f5f9; border-radius: 12px; padding: 15px; min-height: 500px; }}
        .task-card {{ background: white; border-radius: 8px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); cursor: pointer; }}
        /* ... 完整 CSS 應該從原始模板複製 ... */
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🦞 OpenClaw 任務管理看板</h1>
            <div class="stats-bar">
                <div class="stat-item"><div class="stat-number">{stats['total']}</div><div class="stat-label">總任務數</div></div>
                <div class="stat-item" style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);"><div class="stat-number">{stats['completed']}</div><div class="stat-label">已完成</div></div>
                <div class="stat-item" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);"><div class="stat-number">{stats['running']}</div><div class="stat-label">執行中</div></div>
                <div class="stat-item" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);"><div class="stat-number">{stats['pending']}</div><div class="stat-label">待處理</div></div>
                <div class="stat-item" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);"><div class="stat-number">{stats['agents']}</div><div class="stat-label">Agent 團隊</div></div>
            </div>
        </header>

        <div class="board">
            <div class="column column-pending">
                <div class="column-header"><span>⏳ 待處理</span><span class="column-count">{stats['pending']}</span></div>
                <div id="pending-tasks">
                    {''.join([task_card(t) for t in pending])}
                </div>
            </div>
            <div class="column column-running">
                <div class="column-header"><span>🔄 執行中</span><span class="column-count">{stats['running']}</span></div>
                <div id="running-tasks">
                    {''.join([task_card(t) for t in running])}
                </div>
            </div>
            <div class="column column-completed">
                <div class="column-header"><span>✅ 已完成</span><span class="column-count">{stats['completed']}</span></div>
                <div id="completed-tasks">
                    {''.join([task_card(t) for t in completed])}
                </div>
            </div>
        </div>

        <div class="agents-section">
            <h2>🤖 Agent 團隊</h2>
            <div class="agents-grid">
                {''.join([agent_card(aid, a) for aid, a in agents.items()])}
            </div>
        </div>

        <div class="improvements-section">
            <h2>📈 持續改善追蹤</h2>
            <div class="improvement-timeline">
                {improvement_html}
            </div>
        </div>

        <footer>
            <p>🦞 OpenClaw 任務管理系統 v2.0 | 最後更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>模型：GPT-5.3-Codex | 記憶系統：已啟用</p>
        </footer>
    </div>
</body>
</html>'''
    
    return html

def main():
    """主函數"""
    print("🔄 更新任務看板...")
    
    # 載入數據
    data = load_task_board()
    if not data:
        print("❌ 找不到 task-board.json")
        return
    
    # 生成 HTML
    html = generate_dashboard_html(data)
    
    # 儲存到兩個位置
    workspace = Path.home() / '.openclaw' / 'workspace'
    
    # 1. 工作區
    output_path = workspace / 'task-board-dashboard.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 已更新：{output_path}")
    
    # 2. Windows 資料夾
    windows_path = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw') / datetime.now().strftime('%Y-%m-%d') / 'task-board-dashboard.html'
    windows_path.parent.mkdir(exist_ok=True)
    with open(windows_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 已複製：{windows_path}")
    
    print("\n📊 統計:")
    print(f"  總任務：{data.get('stats', {}).get('totalCreated', len(data.get('tasks', [])))}")
    print(f"  已完成：{data.get('stats', {}).get('totalCompleted', 0)}")
    print(f"  Agent: {len(data.get('agents', {}))}")

if __name__ == '__main__':
    main()
