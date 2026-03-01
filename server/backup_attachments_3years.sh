#!/bin/bash
#
# 昱金生能源 - 附件三年備份腳本
# 用途：每三年備份一次附件目錄
# 備份結構：年份壓縮檔
#

ATTACHMENTS_DIR="/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments"
BACKUP_DIR="/mnt/c/Users/YJSClaw/Documents/Openclaw/attachments_backup"
DATE=$(date +%Y%m%d_%H%M%S)

echo "📦 昱金生能源 - 附件三年備份腳本"
echo "=================================="
echo ""

# 1. 建立備份目錄
mkdir -p "$BACKUP_DIR"
echo "✅ 備份目錄：$BACKUP_DIR"

# 2. 進入附件目錄
cd "$ATTACHMENTS_DIR" || exit 1

# 3. 備份每個年份
for year_dir in */; do
    year=${year_dir%/}
    
    # 檢查是否為數字年份
    if [[ $year =~ ^[0-9]{4}$ ]]; then
        echo ""
        echo "📁 備份年份：$year"
        
        # 計算年份內的文件數
        file_count=$(find "$year" -type f | wc -l)
        echo "   檔案數量：$file_count"
        
        # 計算年份目錄大小
        dir_size=$(du -sh "$year" | cut -f1)
        echo "   目錄大小：$dir_size"
        
        # 壓縮年份目錄
        backup_file="$BACKUP_DIR/${year}_backup_${DATE}.zip"
        echo "   壓縮中：$backup_file"
        
        zip -r "$backup_file" "$year" -x "*.zip"
        
        if [ $? -eq 0 ]; then
            echo "   ✅ 備份完成：$backup_file"
            
            # 顯示壓縮檔大小
            backup_size=$(du -sh "$backup_file" | cut -f1)
            echo "   壓縮檔大小：$backup_size"
        else
            echo "   ❌ 備份失敗：$year"
        fi
    fi
done

# 4. 產生備份清單
echo ""
echo "📋 產生備份清單..."
backup_list="$BACKUP_DIR/backup_list_${DATE}.txt"

cat > "$backup_list" << EOF
昱金生能源 - 附件備份清單
==========================
備份日期：$(date '+%Y-%m-%d %H:%M:%S')
備份目錄：$ATTACHMENTS_DIR

備份檔案清單：
EOF

ls -lh "$BACKUP_DIR"/*.zip >> "$backup_list" 2>/dev/null

echo ""
echo "📊 備份統計："
echo "   備份檔案數：$(ls "$BACKUP_DIR"/*.zip 2>/dev/null | wc -l)"
echo "   總備份大小：$(du -sh "$BACKUP_DIR" | cut -f1)"
echo "   備份清單：$backup_list"

# 5. 驗證備份
echo ""
echo "🔍 驗證備份..."
for zip_file in "$BACKUP_DIR"/*.zip; do
    if [ -f "$zip_file" ]; then
        echo -n "   驗證：$(basename $zip_file) ... "
        if unzip -t "$zip_file" > /dev/null 2>&1; then
            echo "✅ OK"
        else
            echo "❌ 損毀"
        fi
    fi
done

echo ""
echo "✅ 三年備份作業完成！"
echo ""
echo "💡 後續步驟："
echo "  1. 將備份檔複製到 NAS 或外部儲存"
echo "  2. 驗證備份檔可正常解壓縮"
echo "  3. 記錄備份位置到備份日誌"
echo ""
echo "📦 備份位置：$BACKUP_DIR"
