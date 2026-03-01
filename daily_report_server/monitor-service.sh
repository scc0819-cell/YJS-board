#!/bin/bash
# 昱金生能源日報系統 - 服務監控腳本
# 功能：檢測服務是否運行，異常時自動重啟

SERVICE_NAME="python3 app.py"
WORK_DIR="/home/yjsclaw/.openclaw/workspace/daily_report_server"
LOG_FILE="/tmp/server_monitor.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始監控日報系統服務..." >> $LOG_FILE

# 檢查服務是否運行
if ! pgrep -f "$SERVICE_NAME" > /dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  服務未運行，正在重啟..." >> $LOG_FILE
    
    # 啟動服務
    cd $WORK_DIR
    nohup python3 app.py > /tmp/server.log 2>&1 &
    
    sleep 5
    
    # 驗證服務是否啟動成功
    if pgrep -f "$SERVICE_NAME" > /dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 服務已成功重啟 (PID: $(pgrep -f "$SERVICE_NAME"))" >> $LOG_FILE
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 服務重啟失敗，請檢查日誌" >> $LOG_FILE
    fi
else
    PID=$(pgrep -f "$SERVICE_NAME")
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 服務運行正常 (PID: $PID)" >> $LOG_FILE
fi

# 檢查網頁是否可訪問
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null)
if [ "$HTTP_STATUS" = "302" ] || [ "$HTTP_STATUS" = "200" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 網頁訪問正常 (HTTP $HTTP_STATUS)" >> $LOG_FILE
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  網頁訪問異常 (HTTP $HTTP_STATUS)" >> $LOG_FILE
fi
