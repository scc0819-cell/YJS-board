#!/bin/bash

# OpenClaw Dashboard 啟動腳本

echo "🦞 啟動 OpenClaw 任務看板系統..."
echo

# 啟動 Task API
echo "📡 啟動 Task API..."
pkill -f task-api.py 2>/dev/null
nohup python3 ~/.openclaw/workspace/scripts/task-api.py 8080 > /tmp/task-api.log 2>&1 &
sleep 2

# 啟動 Task Chain Handler
echo "🔗 啟動 Task Chain Handler..."
pkill -f task-chain-handler.py 2>/dev/null
nohup python3 ~/.openclaw/workspace/scripts/task-chain-handler.py > /tmp/task-chain.log 2>&1 &
sleep 2

# 檢查服務狀態
echo
echo "=== 服務狀態 ==="
if curl -s http://localhost:8080/api/tasks > /dev/null 2>&1; then
    echo "✅ Task API: 運行中 (port 8080)"
else
    echo "❌ Task API: 啟動失敗"
fi

if pgrep -f task-chain-handler.py > /dev/null 2>&1; then
    echo "✅ Task Chain Handler: 運行中"
else
    echo "❌ Task Chain Handler: 啟動失敗"
fi

echo
echo "🌐 看板網址：http://localhost:8080"
echo
echo "💡 提示：在瀏覽器開啟上述網址即可查看任務看板"
echo

# 嘗試自動開啟瀏覽器
if command -v xdg-open &> /dev/null; then
    echo "🚀 正在開啟瀏覽器..."
    xdg-open http://localhost:8080 2>/dev/null &
elif command -v open &> /dev/null; then
    echo "🚀 正在開啟瀏覽器..."
    open http://localhost:8080 2>/dev/null &
else
    echo "📱 請手動在瀏覽器開啟：http://localhost:8080"
fi
