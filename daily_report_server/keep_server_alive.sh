#!/bin/bash
# keep_server_alive.sh
# 確保日報服務常駐，若掛掉就自動重啟
# 每 5 分鐘由 crontab 呼叫

LOG=/tmp/keep_server_alive.log
APP_DIR=/home/yjsclaw/.openclaw/workspace/daily_report_server
PORT=5000

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 檢查服務狀態..." >> $LOG

# 檢查 port 是否有在 listen
if ! ss -tlnp | grep -q ":$PORT "; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  服務未運行，正在重啟..." >> $LOG
    
    # 先確保沒有殭屍進程
    pkill -9 -f "python3 app.py" 2>/dev/null
    sleep 2
    
    # 重啟服務
    cd $APP_DIR
    nohup python3 app.py >> /tmp/server.log 2>&1 &
    
    sleep 5
    
    # 確認重啟成功
    if ss -tlnp | grep -q ":$PORT "; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 服務重啟成功" >> $LOG
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 服務重啟失敗！請手動檢查" >> $LOG
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 服務運行正常 (port $PORT)" >> $LOG
fi
