#!/bin/bash
# ============================================================
# 昱金生能源集團 - 員工日報附件備份腳本
# ============================================================
# 用途：將附件從 WSL 備份到 NAS
# 排程：每日 02:00 執行
# 設定：crontab -e
#       0 2 * * * /mnt/c/Users/YJSClaw/Documents/Openclaw/backup_attachments.sh
# ============================================================

set -e  # 遇到錯誤立即停止

# ===================== 設定 =====================
SOURCE_DIR="/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments"
NAS_MOUNT="/mnt/y/backups/daily_report_attachments"  # NAS 掛載點
LOG_FILE="/tmp/backup_attachments_$(date +%Y%m%d_%H%M%S).log"
EMAIL="admin@yjsenergy.com"  # 告警 Email（可選）

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ===================== 函數 =====================
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_space() {
    local path=$1
    local available=$(df -P "$path" | tail -1 | awk '{print $4}')
    local available_gb=$((available * 1024 / 1024))
    
    if [ $available_gb -lt 50 ]; then
        log "${RED}⚠️  警告：剩餘空間不足 50GB (剩餘: ${available_gb}GB)${NC}"
        return 1
    fi
    log "${GREEN}✓ 可用空間：${available_gb}GB${NC}"
    return 0
}

backup_year() {
    local year=$1
    local target=$2
    
    log "📦 備份 $year 年度資料..."
    
    if [ -d "$SOURCE_DIR/$year" ]; then
        rsync -av --delete \
            --stats \
            "$SOURCE_DIR/$year/" \
            "$target/$year/" >> "$LOG_FILE" 2>&1
        
        log "${GREEN}✓ $year 年度備份完成${NC}"
    else
        log "${YELLOW}⚠️  $year 年度資料夾不存在，跳過${NC}"
    fi
}

cleanup_old_backups() {
    log "🧹 清理超過 30 天的日誌檔..."
    find /tmp -name "backup_attachments_*.log" -mtime +30 -delete
}

send_notification() {
    local status=$1
    local message=$2
    
    # Email 通知（需安裝 mailutils）
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "[日報附件備份] $status" "$EMAIL"
    fi
    
    # 或 Telegram 通知（可選）
    # curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
    #     -d chat_id="<CHAT_ID>" \
    #     -d text="$status%0A$message"
}

# ===================== 主程式 =====================
log "============================================================"
log "🚀 開始備份員工日報附件"
log "============================================================"
log "來源：$SOURCE_DIR"
log "目標：$NAS_MOUNT"

# 檢查來源目錄
if [ ! -d "$SOURCE_DIR" ]; then
    log "${RED}❌ 錯誤：來源目錄不存在${NC}"
    exit 1
fi

# 檢查目標目錄
if [ ! -d "$NAS_MOUNT" ]; then
    log "${YELLOW}⚠️  目標目錄不存在，建立中...${NC}"
    mkdir -p "$NAS_MOUNT"
fi

# 檢查空間
log "\n📊 檢查磁碟空間..."
check_space "$SOURCE_DIR" || true
check_space "$NAS_MOUNT" || true

# 備份當年資料（增量）
CURRENT_YEAR=$(date +%Y)
log "\n📋 備份當年資料 ($CURRENT_YEAR)..."
backup_year "$CURRENT_YEAR" "$NAS_MOUNT"

# 備份去年資料（完整，每週執行一次）
if [ "$(date +%u)" -eq 7 ]; then  # 每週日
    LAST_YEAR=$((CURRENT_YEAR - 1))
    log "\n📋 備份去年資料 ($LAST_YEAR)..."
    backup_year "$LAST_YEAR" "$NAS_MOUNT/archive"
fi

# 統計備份結果
log "\n📊 備份統計："
if [ -d "$NAS_MOUNT/$CURRENT_YEAR" ]; then
    TOTAL_SIZE=$(du -sh "$NAS_MOUNT/$CURRENT_YEAR" | cut -f1)
    FILE_COUNT=$(find "$NAS_MOUNT/$CURRENT_YEAR" -type f | wc -l)
    log "  當年資料：$TOTAL_SIZE ($FILE_COUNT 個檔案)"
fi

# 清理舊日誌
cleanup_old_backups

# 完成通知
log "\n${GREEN}✅ 備份完成！${NC}"
send_notification "✅ 成功" "備份完成，詳細資訊請查看：$LOG_FILE"

exit 0
