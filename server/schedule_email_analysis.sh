#!/bin/bash
# 昱金生能源 - 郵件分析排程腳本
# 功能：等待 3 小時後執行郵件分析

echo "⏰ 設定 3 小時後執行郵件分析..."
echo "   開始時間：$(date)"

# 計算 3 小時後的時間
DELAY_SECONDS=$((3 * 60 * 60))

echo "   執行時間：$(date -d "+$DELAY_SECONDS seconds" 2>/dev/null || date -v+3H)"

# 等待 3 小時
sleep $DELAY_SECONDS

echo ""
echo "🚀 開始執行郵件分析..."
echo "   執行時間：$(date)"

cd /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server

# 執行郵件分析（預設 365 天）
python3 scripts/email_analyzer.py 365

# 執行結果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 郵件分析完成！"
    echo ""
    echo "📊 檢視結果："
    echo "   cat email_analysis/analysis_summary.md"
    echo "   cat email_analysis/ai_memory_injection.md"
    echo "   cat email_analysis/employee_requests.md"
    echo ""
    echo "📬 董事長副本通知："
    echo "   cat email_analysis/chairman_copy.md"
else
    echo ""
    echo "❌ 郵件分析失敗，請檢查日誌"
    echo "   tail /tmp/email_analysis.log"
fi
