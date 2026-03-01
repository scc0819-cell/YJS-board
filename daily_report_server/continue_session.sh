#!/bin/bash
# continue_session.sh
# 新 Session 開始時執行這個腳本，快速接續進度

echo "============================================================"
echo "🚀 昱金生能源 - 新 Session 接續檢查"
echo "============================================================"
echo ""

# 1. 讀取接續摘要
echo "📋 讀取進度摘要..."
if [ -f "/home/yjsclaw/.openclaw/workspace/daily_report_server/SESSION_HANDOVER.md" ]; then
    echo "✅ 已找到 SESSION_HANDOVER.md"
    echo "   最後更新：$(stat -c %y /home/yjsclaw/.openclaw/workspace/daily_report_server/SESSION_HANDOVER.md | cut -d' ' -f1)"
else
    echo "❌ 找不到 SESSION_HANDOVER.md"
fi
echo ""

# 2. 檢查服務狀態
echo "🔍 檢查服務狀態..."
if ss -tlnp | grep -q ":5000 "; then
    echo "✅ 日報服務運行中 (port 5000)"
    curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" http://localhost:5000/login
else
    echo "❌ 服務未運行，正在重啟..."
    cd /home/yjsclaw/.openclaw/workspace/daily_report_server
    nohup python3 app.py >> /tmp/server.log 2>&1 &
    sleep 5
    if ss -tlnp | grep -q ":5000 "; then
        echo "✅ 服務重啟成功"
    else
        echo "❌ 服務重啟失敗，請手動檢查"
    fi
fi
echo ""

# 3. 檢查 crontab
echo "📅 檢查 crontab 排程..."
CRON_COUNT=$(crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' | wc -l)
if [ "$CRON_COUNT" -ge 7 ]; then
    echo "✅ crontab 正常 ($CRON_COUNT 項排程)"
    crontab -l | grep -E "^@|^[0-9*]" | head -3 | sed 's/^/   /'
    echo "   ... (共 $CRON_COUNT 項)"
else
    echo "⚠️  crontab 可能不完整 (目前 $CRON_COUNT 項，應為 7 項)"
fi
echo ""

# 4. 執行健康檢查
echo "🏥 執行系統健康檢查..."
python3 /home/yjsclaw/.openclaw/workspace/daily_report_server/system_health_checker.py 2>&1 | tail -8
echo ""

# 5. 檢查郵件排程
echo "📧 檢查郵件解析狀態..."
if [ -f "/tmp/email_analyzer_cron.log" ]; then
    echo "✅ 郵件解析日誌存在"
    tail -3 /tmp/email_analyzer_cron.log | sed 's/^/   /'
else
    echo "ℹ️  尚未執行郵件解析（等待排程觸發）"
fi
echo ""

echo "============================================================"
echo "✅ Session 接續完成！"
echo "============================================================"
echo ""
echo "💡 下一步建議："
echo "   • 查看完整進度：cat SESSION_HANDOVER.md"
echo "   • 查看記憶：cat ../MEMORY.md"
echo "   • 查看今日記憶：cat ../memory/$(date +%Y-%m-%d).md"
echo "   • 檢查服務日誌：tail -50 /tmp/server.log"
echo ""
