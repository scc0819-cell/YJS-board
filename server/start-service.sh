#!/bin/bash
# 昱金生能源集團 - 員工日報系統 啟動腳本

cd /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server

# 檢查是否已在運行
if pgrep -f "python3 app.py" > /dev/null; then
    echo "服務已在運行中"
    exit 0
fi

# 啟動服務
nohup python3 app.py > /tmp/daily_report.log 2>&1 &
echo "服務已啟動 (PID: $!)"
