#!/bin/bash
# backup_attachments.sh
# 每日凌晨 3 點備份附件到 NAS
# 備份策略：
# - 當年資料：每日增量備份
# - 去年資料：每週完整備份

LOG=/tmp/backup_attachments.log
SRC_DIR="/home/yjsclaw/.openclaw/workspace/daily_report_attachments"
DST_DIR="/mnt/z/backup/daily_report_attachments"
YEAR=$(date +%Y)
WEEK=$(date +%V)

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始備份附件..." >> $LOG

# 建立目標目錄
mkdir -p "$DST_DIR"

# 檢查來源目錄
if [ ! -d "$SRC_DIR" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  來源目錄不存在：$SRC_DIR" >> $LOG
    exit 0
fi

# 計算檔案數量
FILE_COUNT=$(find "$SRC_DIR" -type f | wc -l)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 來源目錄檔案數：$FILE_COUNT" >> $LOG

if [ $FILE_COUNT -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️  沒有附件需要備份" >> $LOG
    exit 0
fi

# 執行備份（rsync 增量備份）
rsync -av --delete \
    "$SRC_DIR/" \
    "$DST_DIR/" \
    >> $LOG 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 備份成功" >> $LOG
    
    # 計算備份大小
    BACKUP_SIZE=$(du -sh "$DST_DIR" | cut -f1)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 備份大小：$BACKUP_SIZE" >> $LOG
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 備份失敗！請手動檢查" >> $LOG
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 備份完成" >> $LOG
echo "" >> $LOG
