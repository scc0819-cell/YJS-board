#!/usr/bin/env python3
"""
生成任務看板數據和 HTML
讀取最新任務數據，更新 task-board.json 和 index.html
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 工作目錄
WORKSPACE = Path(__file__).parent.parent
TASK_DATA_FILE = WORKSPACE / "task-board.json"
HTML_TEMPLATE_FILE = WORKSPACE / "task-board-template.html"
HTML_OUTPUT_FILE = WORKSPACE / "index.html"

def get_latest_task_data():
    """
    從數據源獲取最新任務數據
    目前從 task-board.json 讀取，未來可改為 API/資料庫
    """
    # 讀取現有數據
    try:
        with open(TASK_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        # 如果沒有現有數據，建立預設數據
        data = {
            "version": "2.0",
            "lastUpdated": datetime.now().isoformat(),
            "agents": {
                "jenny": {"name": "Jenny", "role": "主助理", "tasks_assigned": 5, "status": "active", "emoji": "🎯"},
                "argus": {"name": "Argus", "role": "監控專家", "tasks_assigned": 3, "status": "active", "emoji": "👁️"},
                "scribe": {"name": "Scribe", "role": "報告專家", "tasks_assigned": 2, "status": "active", "emoji": "📝"},
                "chronos": {"name": "Chronos", "role": "排程專家", "tasks_assigned": 4, "status": "active", "emoji": "⏰"},
                "athena": {"name": "Athena", "role": "分析專家", "tasks_assigned": 1, "status": "active", "emoji": "🧠"},
                "hermes": {"name": "Hermes", "role": "通訊專家", "tasks_assigned": 6, "status": "active", "emoji": "📧"}
            },
            "improvements": [],
            "taskChains": []
        }
    
    # 更新時間戳
    data["lastUpdated"] = datetime.now().isoformat()
    
    # 計算統計數據
    total_tasks = sum(agent.get("tasks_assigned", 0) for agent in data["agents"].values())
    
    # 添加 stats 供 HTML 使用
    data["stats"] = {
        "total_tasks": total_tasks,
        "active": total_tasks,  # 簡化：假設所有任務都在進行中
        "pending": 0,
        "completed": 0
    }
    
    # 將 agents 物件轉換為陣列供 HTML 模板使用
    data["agents_list"] = [
        {
            "id": key,
            "name": info["name"],
            "role": info["role"],
            "tasks": info.get("tasks_assigned", 0),
            "status": info.get("status", "active"),
            "emoji": info.get("emoji", "")
        }
        for key, info in data["agents"].items()
    ]
    
    return data

def generate_html(data):
    """
    根據數據生成 HTML 看板
    """
    # 讀取模板
    try:
        with open(HTML_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        # 如果沒有模板，使用內建模板
        template = get_default_template()
    
    # 替換數據
    html = template.replace('{{last_updated}}', data["lastUpdated"])
    html = html.replace('{{total_tasks}}', str(data["stats"]["total_tasks"]))
    html = html.replace('{{active_tasks}}', str(data["stats"]["active"]))
    html = html.replace('{{pending_tasks}}', str(data["stats"]["pending"]))
    html = html.replace('{{completed_tasks}}', str(data["stats"]["completed"]))
    
    # 生成 Agent 卡片
    agents_html = ""
    for agent in data.get("agents_list", []):
        status_color = "#4CAF50" if agent["status"] == "active" else "#FFC107"
        agents_html += f'''
        <div class="agent-card">
            <div class="agent-header">
                <span class="agent-name">{agent["name"]}</span>
                <span class="agent-status" style="background:{status_color}">{agent["status"]}</span>
            </div>
            <div class="agent-role">{agent["role"]}</div>
            <div class="agent-tasks">任務數：<strong>{agent["tasks"]}</strong></div>
        </div>
        '''
    
    html = html.replace('{{agents_grid}}', agents_html)
    
    # 任務列表（目前 JSON 中沒有明細，留空）
    tasks_html = "<p style='text-align:center;color:#888;'>任務明細將於後續版本中加入</p>"
    html = html.replace('{{tasks_list}}', tasks_html)
    
    return html

def get_default_template():
    """預設 HTML 模板"""
    return '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 昱金生能源 - AI 任務看板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft JhengHei', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #0f3460;
            margin-bottom: 30px;
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .last-updated { color: #888; font-size: 0.9em; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        .stat-number { font-size: 3em; font-weight: bold; color: #00d9ff; }
        .stat-label { color: #aaa; margin-top: 10px; }
        .section-title { font-size: 1.8em; margin-bottom: 20px; border-left: 4px solid #00d9ff; padding-left: 15px; }
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .agent-card {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .agent-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .agent-name { font-size: 1.3em; font-weight: bold; }
        .agent-status { padding: 5px 12px; border-radius: 20px; font-size: 0.8em; }
        .agent-role { color: #888; margin-bottom: 10px; }
        .agent-tasks { font-size: 1.1em; }
        .tasks-list { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; }
        .task-item {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 15px;
            padding: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            align-items: center;
        }
        .task-item:last-child { border-bottom: none; }
        .task-title { font-weight: bold; }
        .task-agent { color: #00d9ff; }
        .task-status, .task-priority { padding: 5px 12px; border-radius: 20px; font-size: 0.85em; text-align: center; }
        @media (max-width: 768px) {
            .task-item { grid-template-columns: 1fr; gap: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 昱金生能源 - AI 任務看板</h1>
            <div class="last-updated">最後更新：{{last_updated}}</div>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{total_tasks}}</div>
                <div class="stat-label">總任務數</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{active_tasks}}</div>
                <div class="stat-label">進行中</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{pending_tasks}}</div>
                <div class="stat-label">待處理</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{completed_tasks}}</div>
                <div class="stat-label">已完成</div>
            </div>
        </div>
        
        <h2 class="section-title">👥 Agent 團隊狀態</h2>
        <div class="agents-grid">
            {{agents_grid}}
        </div>
        
        <h2 class="section-title">📋 任務列表</h2>
        <div class="tasks-list">
            {{tasks_list}}
        </div>
    </div>
</body>
</html>'''

def main():
    print("🚀 開始生成任務看板...")
    
    # 獲取最新數據
    data = get_latest_task_data()
    
    # 保存 JSON 數據
    with open(TASK_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 數據已保存：{TASK_DATA_FILE}")
    
    # 生成 HTML
    html = generate_html(data)
    with open(HTML_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ HTML 已生成：{HTML_OUTPUT_FILE}")
    
    print("🎉 完成！")

if __name__ == "__main__":
    main()
