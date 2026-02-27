#!/usr/bin/env python3
"""
OpenClaw Task Board API
提供任務看板的後端 API
"""

import json
import os
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import subprocess
import threading

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
TASK_FILE = os.path.join(WORKSPACE, "memory", "task-board.json")

class TaskAPIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/tasks":
            self.send_json(get_tasks())
        elif self.path == "/api/cron":
            self.send_json(get_cron_jobs())
        elif self.path == "/api/stats":
            self.send_json(get_stats())
        elif self.path.startswith("/dashboard") or self.path == "/":
            self.serve_dashboard()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == "/api/tasks":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            result = create_task(data)
            self.send_json(result)
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def serve_dashboard(self):
        dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_error(404, "Dashboard not found")

def get_tasks():
    if not os.path.exists(TASK_FILE):
        return []
    with open(TASK_FILE) as f:
        data = json.load(f)
    return data.get('tasks', [])

def get_cron_jobs():
    try:
        result = subprocess.run(['openclaw', 'cron', 'list'], 
                              capture_output=True, text=True, timeout=10)
        # 解析 JSON 輸出
        if result.stdout.strip().startswith('{'):
            return json.loads(result.stdout)
        return []
    except:
        return []

def get_stats():
    if not os.path.exists(TASK_FILE):
        return {}
    with open(TASK_FILE) as f:
        data = json.load(f)
    return data.get('stats', {})

def create_task(task_data):
    if not os.path.exists(TASK_FILE):
        # 初始化文件
        init_data = {
            "tasks": [],
            "cronJobs": [],
            "agents": {"main": {"name": "Jenny", "model": "ollama/qwen3.5:397b-cloud"}},
            "stats": {"totalCreated": 0, "totalCompleted": 0, "totalFailed": 0}
        }
        with open(TASK_FILE, 'w') as f:
            json.dump(init_data, f, indent=2)
    
    with open(TASK_FILE) as f:
        data = json.load(f)
    
    new_task = {
        "id": f"task-{datetime.now().timestamp()}",
        "name": task_data.get('name', 'Unnamed'),
        "description": task_data.get('description', ''),
        "agent": task_data.get('agent', 'main'),
        "status": task_data.get('status', 'pending'),
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    
    data['tasks'].append(new_task)
    data['stats']['totalCreated'] = data['stats'].get('totalCreated', 0) + 1
    
    with open(TASK_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return new_task

def run_server(port=8080):
    server = HTTPServer(('localhost', port), TaskAPIHandler)
    print(f"🦞 Task Board API running at http://localhost:{port}")
    print(f"Dashboard: http://localhost:{port}/dashboard")
    server.serve_forever()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
