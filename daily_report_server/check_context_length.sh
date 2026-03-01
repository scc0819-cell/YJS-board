#!/bin/bash
# check_context_length.sh
# 檢查當前 session 的上下文長度，超過閾值時發出警告

LOG_FILE="/home/yjsclaw/.openclaw/workspace/daily_report_server/context_monitor.log"
THRESHOLD_TOKENS=80000  # 80K tokens 警告閾值
THRESHOLD_MESSAGES=200   # 200 則訊息警告閾值

echo "============================================================"
echo "📊 上下文長度檢查"
echo "============================================================"
echo "檢查時間：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 檢查當前 session 的訊息數量（估算）
# 由於無法直接取得 session 長度，我們用間接方式判斷

# 方法 1: 檢查今日記憶檔案大小
MEMORY_FILE="/home/yjsclaw/.openclaw/workspace/memory/$(date +%Y-%m-%d).md"
if [ -f "$MEMORY_FILE" ]; then
    MEMORY_SIZE=$(wc -c < "$MEMORY_FILE")
    MEMORY_LINES=$(wc -l < "$MEMORY_FILE")
    echo "📝 今日記憶檔案："
    echo "   路徑：$MEMORY_FILE"
    echo "   大小：$MEMORY_SIZE bytes"
    echo "   行數：$MEMORY_LINES"
    
    if [ "$MEMORY_SIZE" -gt 50000 ]; then
        echo "   ⚠️  記憶檔案過大，建議摘要整理"
    fi
fi
echo ""

# 方法 2: 檢查 server.log 大小（推斷 session 長度）
SERVER_LOG="/tmp/server.log"
if [ -f "$SERVER_LOG" ]; then
    LOG_SIZE=$(wc -c < "$SERVER_LOG")
    echo "📋 服務日誌："
    echo "   大小：$LOG_SIZE bytes"
    
    if [ "$LOG_SIZE" -gt 10000000 ]; then
        echo "   ⚠️  日誌過大，建議輪替"
    fi
fi
echo ""

# 方法 3: 檢查健康檢查次數（推斷運行時間）
HEALTH_LOG="/tmp/health_check.log"
if [ -f "$HEALTH_LOG" ]; then
    CHECK_COUNT=$(wc -l < "$HEALTH_LOG")
    echo "🏥 健康檢查次數：$CHECK_COUNT"
    
    # 每 30 分鐘檢查一次，推算運行時間
    if [ "$CHECK_COUNT" -gt 0 ]; then
        HOURS=$((CHECK_COUNT / 2))
        echo "   推估運行時間：約 $HOURS 小時"
        
        if [ "$HOURS" -gt 8 ]; then
            echo "   ⚠️  運行超過 8 小時，建議重啟 session"
        fi
    fi
fi
echo ""

# 方法 4: 檢查 crontab 執行次數
CRON_LOG="/tmp/email_analyzer_cron.log"
if [ -f "$CRON_LOG" ]; then
    EMAIL_COUNT=$(wc -l < "$CRON_LOG")
    echo "📧 郵件解析次數：$EMAIL_COUNT"
fi
echo ""

# 判斷是否需要警告
NEED_WARNING=false
WARNING_REASON=""

if [ "$MEMORY_SIZE" -gt 50000 ]; then
    NEED_WARNING=true
    WARNING_REASON="記憶檔案過大"
fi

if [ "$CHECK_COUNT" -gt 48 ]; then  # 8 小時 * 2 次/小時 = 16 次，設定寬鬆一點 48 次（24 小時）
    NEED_WARNING=true
    WARNING_REASON="運行時間過長"
fi

echo "============================================================"
echo "📊 檢查結果"
echo "============================================================"

if [ "$NEED_WARNING" = true ]; then
    echo "⚠️  建議重啟 Session"
    echo "   原因：$WARNING_REASON"
    echo ""
    echo "📋 重啟步驟："
    echo "   1. 複製以下指令到新 Session："
    echo "      bash /home/yjsclaw/.openclaw/workspace/daily_report_server/continue_session.sh"
    echo ""
    echo "   2. 或告訴我：「請接續日報管理系統進度」"
    echo ""
    
    # 記錄警告
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  WARNING: $WARNING_REASON" >> "$LOG_FILE"
else
    echo "✅ 上下文長度正常"
    echo "   可以继续正常使用"
fi

echo "============================================================"
echo ""

# 如果有警告，輸出醒目提示
if [ "$NEED_WARNING" = true ]; then
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  🚨 建議立即行動：開啟新 Session 並執行 continue_session.sh  ║"
    echo "╚══════════════════════════════════════════════════════════╝"
fi
