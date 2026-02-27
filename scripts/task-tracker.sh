#!/bin/bash

# OpenClaw Task Tracker
# 任務追蹤與看板生成工具

WORKSPACE="$HOME/.openclaw/workspace"
TASK_FILE="$WORKSPACE/memory/task-board.json"
MEMORY_DIR="$WORKSPACE/memory"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_help() {
    echo "OpenClaw 任務追蹤器"
    echo ""
    echo "用法：$0 <命令>"
    echo ""
    echo "命令:"
    echo "  list          列出所有任務"
    echo "  add <name>    新增任務"
    echo "  complete <id> 標記任務完成"
    echo "  fail <id>     標記任務失敗"
    echo "  stats         顯示統計資訊"
    echo "  cron          顯示排程任務"
    echo "  dashboard     開啟看板（需要瀏覽器）"
    echo ""
}

list_tasks() {
    echo -e "${BLUE}=== 任務列表 ===${NC}"
    if [ -f "$TASK_FILE" ]; then
        python3 << EOF
import json
with open('$TASK_FILE') as f:
    data = json.load(f)
    
tasks = data.get('tasks', [])
if not tasks:
    print("目前沒有任務")
else:
    for i, task in enumerate(tasks, 1):
        status = task.get('status', 'pending')
        status_icon = {'pending': '⏳', 'running': '🔄', 'completed': '✅', 'failed': '❌'}.get(status, '❓')
        print(f"{i}. {status_icon} {task.get('name', 'Unnamed')}")
        print(f"   描述：{task.get('description', '')}")
        print(f"   Agent: {task.get('agent', 'main')}")
        print(f"   建立：{task.get('createdAt', 'N/A')}")
        if task.get('completedAt'):
            print(f"   完成：{task.get('completedAt')}")
        print()
EOF
    else
        echo "任務文件不存在"
    fi
}

add_task() {
    local name="$1"
    local desc="${2:-手動新增的任務}"
    local agent="${3:-main}"
    
    if [ -z "$name" ]; then
        echo -e "${RED}錯誤：請提供任務名稱${NC}"
        exit 1
    fi
    
    python3 << EOF
import json
from datetime import datetime

with open('$TASK_FILE') as f:
    data = json.load(f)

new_task = {
    "id": "$(uuidgen 2>/dev/null || echo $(date +%s))",
    "name": "$name",
    "description": "$desc",
    "agent": "$agent",
    "status": "pending",
    "createdAt": datetime.now().isoformat(),
    "updatedAt": datetime.now().isoformat()
}

data['tasks'].append(new_task)
data['stats']['totalCreated'] = data['stats'].get('totalCreated', 0) + 1

with open('$TASK_FILE', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ 任務已新增：$name")
EOF
}

show_stats() {
    echo -e "${BLUE}=== 任務統計 ===${NC}"
    if [ -f "$TASK_FILE" ]; then
        python3 << EOF
import json
with open('$TASK_FILE') as f:
    data = json.load(f)

stats = data.get('stats', {})
tasks = data.get('tasks', [])

status_count = {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}
for task in tasks:
    status = task.get('status', 'pending')
    if status in status_count:
        status_count[status] += 1

print(f"總建立：{stats.get('totalCreated', 0)}")
print(f"總完成：{stats.get('totalCompleted', 0)}")
print(f"總失敗：{stats.get('totalFailed', 0)}")
print()
print(f"目前狀態:")
print(f"  {status_count['pending']} 待處理")
print(f"  {status_count['running']} 執行中")
print(f"  {status_count['completed']} 已完成")
print(f"  {status_count['failed']} 失敗")
EOF
    fi
}

show_cron() {
    echo -e "${BLUE}=== 排程任務 ===${NC}"
    openclaw cron list 2>/dev/null || echo "無法獲取排程任務"
}

open_dashboard() {
    echo -e "${GREEN}開啟任務看板...${NC}"
    echo "看板位置：$WORKSPACE/../dashboard/index.html"
    # 嘗試用瀏覽器開啟
    if command -v xdg-open &> /dev/null; then
        xdg-open "$WORKSPACE/../dashboard/index.html" 2>/dev/null || echo "請手動開啟檔案：$WORKSPACE/../dashboard/index.html"
    elif command -v open &> /dev/null; then
        open "$WORKSPACE/../dashboard/index.html" 2>/dev/null || echo "請手動開啟檔案：$WORKSPACE/../dashboard/index.html"
    else
        echo "請在瀏覽器開啟：file://$WORKSPACE/../dashboard/index.html"
    fi
}

# 主程式
case "${1:-help}" in
    list)
        list_tasks
        ;;
    add)
        add_task "$2" "$3" "$4"
        ;;
    complete)
        echo "功能開發中..."
        ;;
    fail)
        echo "功能開發中..."
        ;;
    stats)
        show_stats
        ;;
    cron)
        show_cron
        ;;
    dashboard)
        open_dashboard
        ;;
    *)
        show_help
        ;;
esac
