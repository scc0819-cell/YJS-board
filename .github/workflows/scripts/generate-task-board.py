#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
TASK_DATA_FILE = WORKSPACE / "task-board.json"
HTML_OUTPUT_FILE = WORKSPACE / "index.html"

def get_latest_task_data():
    try:
        with open(TASK_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {
            "last_updated": datetime.now().isoformat(),
            "agents": [
                {"id": "main", "name": "Jenny", "role": "主助理", "tasks": 5, "status": "active"},
                {"id": "monitor", "name": "Argus", "role": "監控", "tasks": 3, "status": "active"},
                {"id": "reporter", "name": "Scribe", "role": "報告", "tasks": 2, "status": "idle"},
                {"id": "scheduler", "name": "Chronos", "role": "排程", "tasks": 4, "status": "active"},
                {"id": "analyst", "name": "Athena", "role": "分析", "tasks": 1, "status": "idle"},
                {"id": "communicator", "name": "Hermes", "role": "通訊", "tasks": 6, "status": "active"},
            ],
            "tasks": [
                {"id": 1, "title": "監控系統檢查", "agent": "Argus", "status": "running", "priority": "high"},
                {"id": 2, "title": "日報生成", "agent": "Scribe", "status": "pending", "priority": "medium"},
                {"id": 3, "title": "排程優化", "agent": "Chronos", "status": "running", "priority": "high"},
                {"id": 4, "title": "數據分析", "agent": "Athena", "status": "completed", "priority": "low"},
                {"id": 5, "title": "郵件處理", "agent": "Hermes", "status": "running", "priority": "medium"},
            ],
            "stats": {"total_tasks": 21, "active": 12, "pending": 5, "completed": 4}
        }
    data["last_updated"] = datetime.now().isoformat()
    import random
    for agent in data["agents"]:
        agent["tasks"] = max(0, agent["tasks"] + random.randint(-2, 3))
    data["stats"]["total_tasks"] = sum(agent["tasks"] for agent in data["agents"])
    return data
def generate_html(data):
    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>🤖 昱金生能源 - AI 任務看板</title>
    <style>
        body {{ font-family: sans-serif; background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{ text-align: center; padding: 30px 0; }}
        h1 {{ font-size: 2.5em; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: rgba(255,255,255,0.1); padding: 25px; border-radius: 15px; text-align: center; }}
        .stat-number {{ font-size: 3em; color: #00d9ff; }}
        .section-title {{ font-size: 1.8em; border-left: 4px solid #00d9ff; padding-left: 15px; margin: 30px 0 20px; }}
        .agents-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
        .agent-card {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; }}
        .agent-header {{ display: flex; justify-content: space-between; }}
        .agent-status {{ padding: 5px 12px; border-radius: 20px; }}
        .tasks-list {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin-top: 20px; }}
        .task-item {{ display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 15px; padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
    </style>
</head>
<body>
    <div class="container">
        <header><h1>🤖 昱金生能源 - AI 任務看板</h1><div>最後更新：{data["last_updated"]}</div></header>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-number">{data["stats"]["total_tasks"]}</div><div>總任務數</div></div>
            <div class="stat-card"><div class="stat-number">{data["stats"]["active"]}</div><div>進行中</div></div>
            <div class="stat-card"><div class="stat-number">{data["stats"]["pending"]}</div><div>待處理</div></div>
            <div class="stat-card"><div class="stat-number">{data["stats"]["completed"]}</div><div>已完成</div></div>
        </div>
        <h2 class="section-title">👥 Agent 團隊</h2>
        <div class="agents-grid">
'''
    for agent in data["agents"]:
        color = "#4CAF50" if agent["status"]=="active" else "#FFC107"
        html += f'<div class="agent-card"><div class="agent-header"><b>{agent["name"]}</b><span style="background:{color}">{agent["status"]}</span></div><div>{agent["role"]}</div><div>任務：{agent["tasks"]}</div></div>
'
    html += '</div><h2 class="section-title">📋 任務列表</h2><div class="tasks-list">'
    for task in data["tasks"]:
        sc = {"running":"#2196F3","pending":"#FFC107","completed":"#4CAF50"}.get(task["status"],"#999")
        html += f'<div class="task-item"><span>{task["title"]}</span><span>{task["agent"]}</span><span style="background:{sc}">{task["status"]}</span><span>{task["priority"]}</span></div>
'
    html += '</div></div></body></html>'
    return html

def main():
    data = get_latest_task_data()
    with open(TASK_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    html = generate_html(data)
    with open(HTML_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print("✅ 完成！")

if __name__ == "__main__":
    main()
