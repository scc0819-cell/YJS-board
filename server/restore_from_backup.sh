#!/bin/bash
#
# 昱金生能源 - 系統還原腳本
# 用途：從備份快速還原系統
# 使用方式：./restore_from_backup.sh <備份檔路徑>
#

set -e

BACKUP_FILE="$1"
RESTORE_DIR="/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server"
DB_RESTORE_PATH="$RESTORE_DIR/data/app.db"
ATTACHMENTS_RESTORE_DIR="/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments"

echo "🔄 昱金生能源 - 系統還原腳本"
echo "=================================="
echo ""

# 1. 檢查參數
if [ -z "$BACKUP_FILE" ]; then
    echo "❌ 錯誤：請指定備份檔路徑"
    echo "用法：$0 <備份檔路徑>"
    echo ""
    echo "範例："
    echo "  $0 /mnt/c/Users/YJSClaw/Documents/Openclaw/attachments_backup/2026_backup_20260301_120000.zip"
    echo "  $0 /mnt/c/Users/YJSClaw/Documents/Openclaw/db_backup/app_20260301_120000.db"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 錯誤：找不到備份檔 $BACKUP_FILE"
    exit 1
fi

echo "✅ 備份檔：$BACKUP_FILE"
echo ""

# 2. 停止服務
echo "🛑 停止服務..."
pkill -f "python3 app.py" 2>/dev/null || true
sleep 2
echo "  ✅ 服務已停止"
echo ""

# 3. 判斷備份類型並還原
if [[ "$BACKUP_FILE" == *.db ]]; then
    # 資料庫備份
    echo "🗄️  還原資料庫..."
    mkdir -p "$(dirname $DB_RESTORE_PATH)"
    cp "$BACKUP_FILE" "$DB_RESTORE_PATH"
    echo "  ✅ 資料庫已還原：$DB_RESTORE_PATH"
    
elif [[ "$BACKUP_FILE" == *.zip ]]; then
    # 附件備份
    echo "📦 還原附件..."
    
    # 建立臨時目錄
    TEMP_DIR=$(mktemp -d)
    echo "  臨時目錄：$TEMP_DIR"
    
    # 解壓縮
    echo "  解壓縮中..."
    unzip -q "$BACKUP_FILE" -d "$TEMP_DIR"
    
    # 找到年份目錄
    YEAR_DIR=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "20*" | head -1)
    
    if [ -z "$YEAR_DIR" ]; then
        echo "❌ 錯誤：找不到年份目錄"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    YEAR_NAME=$(basename "$YEAR_DIR")
    echo "  年份：$YEAR_NAME"
    
    # 建立目標目錄
    TARGET_DIR="$ATTACHMENTS_RESTORE_DIR/$YEAR_NAME"
    mkdir -p "$TARGET_DIR"
    
    # 複製檔案
    echo "  複製檔案中..."
    cp -r "$YEAR_DIR/"* "$TARGET_DIR/"
    
    # 清理臨時目錄
    rm -rf "$TEMP_DIR"
    
    echo "  ✅ 附件已還原：$TARGET_DIR"
    
else
    echo "❌ 錯誤：不支持的備份檔格式"
    echo "  支持的格式：.db (資料庫) 或 .zip (附件)"
    exit 1
fi

echo ""

# 4. 驗證還原
echo "🔍 驗證還原..."

if [[ "$BACKUP_FILE" == *.db ]]; then
    # 驗證資料庫
    if sqlite3 "$DB_RESTORE_PATH" "SELECT COUNT(*) FROM users;" > /dev/null 2>&1; then
        USER_COUNT=$(sqlite3 "$DB_RESTORE_PATH" "SELECT COUNT(*) FROM users;")
        echo "  ✅ 資料庫驗證通過"
        echo "     用戶數量：$USER_COUNT"
    else
        echo "  ❌ 資料庫驗證失敗"
        exit 1
    fi
    
elif [[ "$BACKUP_FILE" == *.zip ]]; then
    # 驗證附件
    FILE_COUNT=$(find "$TARGET_DIR" -type f | wc -l)
    echo "  ✅ 附件驗證通過"
    echo "     檔案數量：$FILE_COUNT"
fi

echo ""

# 5. 重啟服務
echo "🚀 重啟服務..."
cd "$RESTORE_DIR"
nohup python3 app.py > /tmp/daily_report.log 2>&1 &
sleep 8

# 檢查服務狀態
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "302\|200"; then
    echo "  ✅ 服務已重啟"
else
    echo "  ⚠️  服務啟動中，請稍後檢查"
fi

echo ""
echo "✅ 系統還原完成！"
echo ""
echo "📊 還原摘要："
echo "  備份檔：$BACKUP_FILE"
echo "  還原時間：$(date '+%Y-%m-%d %H:%M:%S')"
echo "  還原類型：$([ "$BACKUP_FILE" == *.db ] && echo '資料庫' || echo '附件')"
echo ""
echo "💡 後續步驟："
echo "  1. 測試登入功能"
echo "  2. 驗證資料完整性"
echo "  3. 檢查附件可訪問性"
echo ""
