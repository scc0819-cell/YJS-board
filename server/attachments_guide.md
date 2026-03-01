# 📎 附件檔案管理規範

## 存放路徑總覽

### 主存放目錄
```
/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments/
```

**說明**：
- 位於 Windows 可直接存取的路徑
- 方便你定期備份到 NAS
- 與 SQLite DB 在同一層級，易於管理

---

## 目錄結構（依年份/日期/人員分類）

```
daily_report_attachments/
├── 2026/                    # 年份
│   ├── 2026-03-01/         # 日期
│   │   ├── chen_ming_de/   # 員工 ID
│   │   │   ├── 20260301_143022/  # 提交時間（YYYYMMDD_HHMMSS）
│   │   │   │   ├── photo/        # 照片
│   │   │   │   ├── meeting/      # 會議記錄
│   │   │   │   ├── document/     # 文件資料
│   │   │   │   └── other/        # 其他
│   │   ├── wang_xiao_ming/
│   │   │   └── 20260301_150815/
│   │   │       ├── photo/
│   │   │       └── document/
│   ├── 2026-03-02/
│   │   └── ...
```

### 路徑規則

| 層級 | 命名規則 | 範例 | 說明 |
|------|---------|------|------|
| L1 | 年份 | `2026` | 方便年度歸檔 |
| L2 | 日期 | `2026-03-01` | 方便按日查詢 |
| L3 | 員工 ID | `chen_ming_de` | 方便權限管理 |
| L4 | 提交時間 | `20260301_143022` | 精確到秒，避免覆蓋 |
| L5 | 附件類型 | `photo` / `meeting` / `document` / `other` | 分類管理 |

---

## 檔案命名規則

### 儲存檔名
```
{隨機 token}__{原始檔名}
```

**範例**：
- `a3f8b2c1__仁豐國小現場照片.jpg`
- `9d4e5f6a__2026Q1 進度報告.pdf`

**說明**：
- 隨機 token：8 碼十六進位（`secrets.token_hex(4)`）
- 避免檔名衝突
- 防止路徑猜測攻擊
- 保留原始檔名方便識別

---

## 資料庫記錄

### `attachments` 表結構

```sql
CREATE TABLE attachments (
    id INTEGER PRIMARY KEY,
    report_key TEXT,          -- 日報唯一鍵（日期_員工）
    report_date TEXT,         -- 日報日期
    employee_id TEXT,         -- 員工 ID
    kind TEXT,                -- 類型：photo/meeting/document/other
    original_name TEXT,       -- 原始檔名
    stored_name TEXT,         -- 儲存檔名（含 token）
    rel_path TEXT,            -- 相對路徑
    size_bytes INTEGER,       -- 檔案大小
    uploaded_at TEXT          -- 上傳時間
);
```

### 查詢範例

```sql
-- 查詢某員工某日的所有附件
SELECT * FROM attachments 
WHERE employee_id = 'chen_ming_de' 
  AND report_date = '2026-03-01';

-- 查詢特定案場相關的所有附件
SELECT a.* FROM attachments a
JOIN work_items w ON a.report_key = w.report_key
WHERE w.case_id = '仁豐國小';

-- 查詢超過 10MB 的大檔案
SELECT * FROM attachments 
WHERE size_bytes > 10485760 
ORDER BY uploaded_at DESC;
```

---

## 定期備份策略

### 備份頻率建議

| 資料類型 | 備份頻率 | 保留期限 | 說明 |
|---------|---------|---------|------|
| 當年附件 | 每日增量 | 永久 | 使用中的資料 |
| 1-3 年前附件 | 每週完整 | 3 年 | 較少存取 |
| 3 年以上附件 | 每月完整 | 10 年 | 歸檔儲存 |

### 備份腳本範例

```bash
#!/bin/bash
# backup_attachments.sh
# 備份附件到 NAS

SOURCE="/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments"
NAS_MOUNT="/mnt/y/backups/daily_report_attachments"
DATE=$(date +%Y%m%d)
LOG="/tmp/backup_attachments_$DATE.log"

echo "=== 開始備份附件 ($DATE) ===" >> $LOG

# 備份當年資料（增量）
CURRENT_YEAR=$(date +%Y)
rsync -av --delete \
    "$SOURCE/$CURRENT_YEAR/" \
    "$NAS_MOUNT/$CURRENT_YEAR/" >> $LOG 2>&1

# 備份去年資料（完整）
LAST_YEAR=$((CURRENT_YEAR - 1))
rsync -av \
    "$SOURCE/$LAST_YEAR/" \
    "$NAS_MOUNT/archive/$LAST_YEAR/" >> $LOG 2>&1

echo "=== 備份完成 ===" >> $LOG
```

### 排程設定（Windows 工作排程器）

1. 開啟「工作排程器」
2. 建立基本工作
3. 名稱：`Daily Report Attachments Backup`
4. 觸發：每天 02:00
5. 動作：啟動程式
   - 程式：`C:\Windows\System32\bash.exe`
   - 參數：`-c "/mnt/c/Users/YJSClaw/Documents/Openclaw/backup_attachments.sh"`
6. 完成

---

## 安全機制

### 1. 副檔名白名單

**允許**：
- 圖片：`jpg`, `jpeg`, `png`, `gif`
- 文件：`pdf`, `xlsx`, `xls`, `docx`, `doc`, `pptx`, `ppt`
- 文字：`txt`
- 壓縮：`zip`, `rar`, `7z`

**拒絕**：
- 可執行檔：`exe`, `bat`, `cmd`, `ps1`, `sh`
- 腳本：`js`, `vbs`, `wsf`
- 其他：`msi`, `dll`, `sys`

### 2. 檔案大小限制

| 類型 | 限制 | 說明 |
|------|------|------|
| 單檔上限 | 10MB | 避免過大檔案 |
| 單次提交總量 | 50MB | 避免大量上傳 |

### 3. 病毒掃描（可選）

整合 ClamAV 掃描上傳檔案：

```python
# 若啟用 ClamAV
import clamd
cd = clamd.ClamdUnixSocket()
scan_result = cd.scan_stream(file_content)
if scan_result.get('stream', [])[0] == 'FOUND':
    # 拒絕上傳並記錄
    audit('upload_rejected_virus', ...)
```

---

## 空間管理

### 預估空間需求

假設：
- 員工數：10 人
- 每人每日附件：5MB
- 工作天：250 天/年

```
年空間需求 = 10 人 × 5MB × 250 天 = 12.5 GB/年
3 年空間需求 = 37.5 GB
```

### 清理策略

1. **測試資料**：7 天後自動刪除（標題含「測試」）
2. **重複檔案**：比對 hash 值，刪除重複
3. **離職員工**：保留 1 年後歸檔

---

## 權限控管

### 檔案存取規則

| 角色 | 可檢視範圍 |
|------|----------|
| 員工 | 自己的附件 |
| 主管 | 所屬部門員工的附件 |
| 管理員 | 全部附件 |

### 下載連結

```
GET /attachments/download/<attachment_id>
```

- 需登入驗證
- 檢查權限
- 記錄下載日誌

---

## 監控與告警

### 監控項目

1. **空間使用率**：超過 80% 發出警告
2. **單日成長量**：異常增長（>500MB/天）發出警告
3. **大檔案數量**：超過 100 個 >10MB 檔案發出警告

### 告警方式

- Email 通知管理員
- Telegram 機器人訊息
- 系統首頁顯示警告

---

## 還原流程

### 情境 1：誤刪單一附件

1. 從 NAS 備份找到對應日期/人員資料夾
2. 複製回原路徑
3. 更新 DB 記錄（如有需要）

### 情境 2：整年資料遺失

1. 從 NAS 備份還原整年資料夾
2. 執行 `repair_attachments.py` 腳本重建 DB 索引
3. 驗證檔案完整性

---

## 審計日誌

所有附件操作都會記錄：

```python
# 上傳成功
audit('upload_success', actor_id=employee_id, detail={
    'filename': '照片.jpg',
    'kind': 'photo',
    'size': 1024000
})

# 上傳失敗（副檔名不符）
audit('upload_rejected_extension', actor_id=employee_id, detail={
    'filename': 'virus.exe',
    'kind': 'other'
})

# 下載
audit('attachment_download', actor_id=user_id, detail={
    'attachment_id': 123,
    'filename': '報告.pdf'
})
```

---

## 快速查詢指令

```bash
# 查看某員工今日上傳的附件
ls /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments/2026/2026-03-01/chen_ming_de/

# 查看今日所有附件總大小
du -sh /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments/2026/2026-03-01/

# 找出最大的 10 個檔案
find /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments -type f -exec ls -lh {} \; | sort -k5 -h -r | head -10

# 統計每年空間使用
du -sh /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments/*/
```

---

*文件版本：1.0*
*最後更新：2026-03-01*
