#!/bin/bash
#
# 昱金生能源 - 異地備份腳本
# 用途：備份到 NAS + 雲端（Google Drive/OneDrive）
# 使用方式：./backup_offsite.sh
#

set -e

BACKUP_DIR="/mnt/c/Users/YJSClaw/Documents/Openclaw/offsite_backup"
NAS_MOUNT="/mnt/y"  # 彰化辦公室 NAS
CLOUD_BACKUP_DIR="/mnt/c/Users/YJSClaw/Documents/Openclaw/cloud_backup"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db"
ATTACHMENTS_DIR="/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments"

echo "🌍 昱金生能源 - 異地備份腳本"
echo "=================================="
echo ""

# 1. 建立備份目錄
mkdir -p "$BACKUP_DIR"
mkdir -p "$CLOUD_BACKUP_DIR"
echo "✅ 備份目錄已建立"
echo ""

# 2. 資料庫備份
echo "🗄️  備份資料庫..."
DB_BACKUP="$BACKUP_DIR/app_$DATE.db"
cp "$DB_PATH" "$DB_BACKUP"

# 壓縮資料庫
gzip -f "$DB_BACKUP"
DB_BACKUP_COMPRESSED="${DB_BACKUP}.gz"

echo "  ✅ 資料庫備份完成：$DB_BACKUP_COMPRESSED"
echo "     大小：$(du -h "$DB_BACKUP_COMPRESSED" | cut -f1)"
echo ""

# 3. 附件備份（最近 30 天）
echo "📦 備份附件（最近 30 天）..."
ATTACHMENTS_BACKUP="$BACKUP_DIR/attachments_recent_$DATE.zip"

# 找出最近 30 天的檔案
find "$ATTACHMENTS_DIR" -type f -mtime -30 > /tmp/recent_files.txt
FILE_COUNT=$(wc -l < /tmp/recent_files.txt)

if [ "$FILE_COUNT" -gt 0 ]; then
    zip -j "$ATTACHMENTS_BACKUP" -@ < /tmp/recent_files.txt
    echo "  ✅ 附件備份完成：$ATTACHMENTS_BACKUP"
    echo "     檔案數量：$FILE_COUNT"
    echo "     大小：$(du -h "$ATTACHMENTS_BACKUP" | cut -f1)"
else
    echo "  ℹ️  最近 30 天無新附件"
fi
rm -f /tmp/recent_files.txt
echo ""

# 4. NAS 備份（彰化辦公室）
echo "📁 NAS 備份（彰化辦公室）..."
if [ -d "$NAS_MOUNT" ]; then
    NAS_BACKUP_DIR="$NAS_MOUNT/yjs_backup/daily_report"
    mkdir -p "$NAS_BACKUP_DIR"
    
    # 複製資料庫備份
    cp "$DB_BACKUP_COMPRESSED" "$NAS_BACKUP_DIR/"
    
    # 複製附件備份
    if [ -f "$ATTACHMENTS_BACKUP" ]; then
        cp "$ATTACHMENTS_BACKUP" "$NAS_BACKUP_DIR/"
    fi
    
    echo "  ✅ NAS 備份完成：$NAS_BACKUP_DIR"
else
    echo "  ⚠️  NAS 未掛載，跳過 NAS 備份"
    echo "     請確認 //yjs/yjs fs 已掛載到 $NAS_MOUNT"
fi
echo ""

# 5. 雲端備份準備
echo "☁️  雲端備份準備..."
CLOUD_DB="$CLOUD_BACKUP_DIR/app_$DATE.db.gz"
CLOUD_ATTACHMENTS="$CLOUD_BACKUP_DIR/attachments_recent_$DATE.zip"

cp "$DB_BACKUP_COMPRESSED" "$CLOUD_DB"

if [ -f "$ATTACHMENTS_BACKUP" ]; then
    cp "$ATTACHMENTS_BACKUP" "$CLOUD_ATTACHMENTS"
fi

echo "  ✅ 雲端備份檔案已準備：$CLOUD_BACKUP_DIR"
echo ""
echo "  💡 雲端同步指令（需手動執行或設定自動同步）："
echo "     # Google Drive (使用 rclone)"
echo "     rclone copy $CLOUD_BACKUP_DIR gdrive:daily_report_backup/"
echo ""
echo "     # OneDrive (使用 rclone)"
echo "     rclone copy $CLOUD_BACKUP_DIR onedrive:daily_report_backup/"
echo ""

# 6. 清理舊備份（保留 90 天）
echo "🧹 清理舊備份（保留 90 天）..."
find "$BACKUP_DIR" -type f -mtime +90 -delete
find "$CLOUD_BACKUP_DIR" -type f -mtime +90 -delete
echo "  ✅ 清理完成"
echo ""

# 7. 產生備份報告
echo "📊 產生備份報告..."
REPORT_FILE="$BACKUP_DIR/backup_report_$DATE.txt"

cat > "$REPORT_FILE" << EOF
昱金生能源 - 異地備份報告
==========================
備份日期：$(date '+%Y-%m-%d %H:%M:%S')

備份檔案清單：
$(ls -lh "$BACKUP_DIR"/*.$DATE*)

NAS 備份位置：$NAS_MOUNT/yjs_backup/daily_report
雲端備份位置：$CLOUD_BACKUP_DIR

備份統計：
- 資料庫大小：$(du -h "$DB_BACKUP_COMPRESSED" | cut -f1)
- 附件備份大小：$([ -f "$ATTACHMENTS_BACKUP" ] && du -h "$ATTACHMENTS_BACKUP" | cut -f1 || echo "N/A")
- 總備份大小：$(du -sh "$BACKUP_DIR" | cut -f1)

保留政策：90 天
下次備份：建議每日執行
EOF

echo "  ✅ 備份報告：$REPORT_FILE"
echo ""

# 8. 顯示摘要
echo "=================================="
echo "✅ 異地備份完成！"
echo ""
echo "📊 備份摘要："
echo "  本地備份：$BACKUP_DIR"
echo "  NAS 備份：$NAS_MOUNT/yjs_backup/daily_report"
echo "  雲端準備：$CLOUD_BACKUP_DIR"
echo ""
echo "📋 備份檔案："
ls -lh "$BACKUP_DIR"/*.$DATE* 2>/dev/null || true
echo ""
echo "💡 後續步驟："
echo "  1. 設定 rclone 同步到 Google Drive/OneDrive"
echo "  2. 設定 cron 每日自動執行"
echo "  3. 定期驗證備份可還原"
echo ""
