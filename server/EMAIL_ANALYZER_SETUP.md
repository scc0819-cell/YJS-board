# 📧 郵件分析系統設定指南

## 🎯 目的

讓 AI 透過分析歷史郵件，快速建立案場脈絡，與團隊記憶同步。

---

## 📋 系統功能

### 1. 郵件掃描

- ✅ 掃描在職員工發送的郵件
- ✅ 掃描已離職員工（江勇毅）的歷史郵件
- ✅ 僅分析 [收件夾] 中的郵件
- ✅ 可設定時間範圍（預設 365 天）

### 2. 智能分析

- ✅ 識別寄件員工
- ✅ 識別案場名稱
- ✅ 提取關鍵事件（進度、問題、里程碑、財務、風險）
- ✅ 建立時間軸
- ✅ 識別待解決問題

### 3. 記憶注入

- ✅ 生成案場完整脈絡
- ✅ 建立 AI 記憶文件
- ✅ 寫入資料庫（email_analysis 表）
- ✅ 生成摘要報告

### 4. 主動提問

- ✅ 識別需要補充的資訊
- ✅ 生成員工補充請求清單
- ✅ 可自動發送 Email 要求補充

---

## 🔧 設定步驟

### 步驟 1：設定郵箱帳號密碼

**方式 A：環境變數（推薦）**

編輯 `~/.bashrc` 或 `~/.profile`：

```bash
export YJS_EMAIL_USER="your_email@yjsenergy.com"
export YJS_EMAIL_PASS="your_app_password"
```

然後執行：
```bash
source ~/.bashrc
```

**方式 B：直接修改腳本**

編輯 `email_analyzer.py`，找到：

```python
EMAIL_ACCOUNTS = {
    'outlook': {
        'server': 'outlook.office365.com',
        'port': 993,
        'username': 'your_email@yjsenergy.com',  # 修改這裡
        'password': 'your_app_password',  # 修改這裡
    }
}
```

---

### 步驟 2：取得 Outlook 應用程式密碼

**重要**：Outlook 需要使用「應用程式密碼」，而非登入密碼。

1. 登入 Microsoft 帳戶：https://account.microsoft.com/security
2. 進入「進階安全性選項」
3. 找到「應用程式密碼」
4. 點擊「建立新的應用程式密碼」
5. 複製產生的密碼（格式：`xxxx xxxx xxxx xxxx`）
6. 將密碼設定到環境變數

---

### 步驟 3：測試連接

```bash
cd /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server
python3 scripts/email_analyzer.py 30  # 測試最近 30 天
```

**預期輸出**：
```
============================================================
📧 昱金生能源 - 郵件分析系統
============================================================
✅ 已連接 Outlook 郵箱：your_email@yjsenergy.com
📬 找到 XXX 封郵件

📊 開始分析 XXX 封郵件...

  ✅ 已寫入 XX 筆事件至資料庫
  ✅ 已生成分析結果
  ✅ 已生成 AI 記憶注入
  ✅ 已生成員工補充請求

============================================================
✅ 郵件分析完成！
============================================================

📊 分析摘要:
  總郵件數：XXX
  員工人數：10
  案場數量：XX
  關鍵事件：XXX
  待補充問題：XX
```

---

## 📊 輸出檔案

分析完成後，會在以下位置生成檔案：

### 1. 分析結果

**位置**：`/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/email_analysis/`

| 檔案 | 用途 |
|------|------|
| `email_analysis.json` | 完整分析結果（JSON 格式） |
| `analysis_summary.md` | 人類可讀的摘要報告 |
| `ai_memory_injection.md` | AI 記憶注入文件 |
| `employee_requests.md` | 員工補充請求清單 |

### 2. 資料庫表

**表名**：`email_analysis`

| 欄位 | 說明 |
|------|------|
| `id` | 主鍵 |
| `email_date` | 郵件日期 |
| `sender` | 寄件者 |
| `subject` | 郵件主旨 |
| `employee_id` | 員工 ID |
| `case_id` | 案場 ID |
| `event_type` | 事件類型（progress/issue/milestone/finance/risk） |
| `summary` | 事件摘要 |
| `created_at` | 建立時間 |

---

## 🤖 AI 記憶同步流程

### 流程圖

```
歷史郵件
    ↓
掃描 + 分析
    ↓
提取關鍵事件
    ↓
建立案場脈絡
    ↓
AI 記憶注入
    ↓
主動提問補充
    ↓
完整知識庫
```

### 實際應用

#### 情境 1：新日報提交

**員工**：楊宗衛提交仁豐國小日報

**AI 反應**：
```
📧 已讀取歷史郵件：
  - 2026-02-15：仁豐國小光電板安裝 80%
  - 2026-02-20：併聯申請已送件
  - 2026-02-25：現場施工空間不足

🧠 AI 理解：
  目前進度應為 90%+，併聯申請可能仍在審查中

💡 AI 建議：
  - 詢問併聯申請審查進度
  - 確認施工空間問題是否解決
  - 提醒注意天氣預報
```

#### 情境 2：風險項目新增

**員工**：新增「馬偕護專 - 廠商延遲」風險

**AI 反應**：
```
📧 已讀取歷史郵件：
  - 2025-12-10：馬偕護專第一期請款完成
  - 2026-01-05：第二期請款單據整理中
  - 2026-01-20：廠商發票有誤退回

🧠 AI 理解：
  該案場有廠商配合度問題的前科

💡 AI 建議：
  - 建議指派專人追蹤廠商進度
  - 提前準備替代廠商名單
  - 通知財務單位注意請款時程
```

---

## 📬 員工補充請求

### 自動生成範例

系統會自動識別需要補充的資訊：

```markdown
# 📬 員工資訊補充請求

## 👤 楊宗衛

- [ ] 「仁豐國小案場進度回報 - 2026/02」中提到的「現場施工空間不足」問題是否已解決？
- [ ] 「仁豐國小案場進度回報 - 2026/02」中提到的「進度落後 3 天」目前是否已追平？

## 👤 陳谷濱

- [ ] 「馬偕護專案 - 財務請款進度」中提到的「廠商發票有誤」是否已重新開立？
```

### 發送方式

**方式 A：手動發送**

1. 打開 `employee_requests.md`
2. 複製對應員工的問題
3. 透過 Email 或通訊軟體發送

**方式 B：自動發送（需設定）**

修改腳本，加入自動發送功能：

```python
def send_request_emails(self, requests):
    """自動發送補充請求 Email"""
    for emp_id, questions in requests.items():
        # 發送 Email
        send_email(
            to=f"{emp_id}@yjsenergy.com",
            subject="【請補充】案場資訊補充請求",
            body=generate_email_body(questions)
        )
```

---

## 🔄 定期執行

### 建議頻率

- **首次執行**：分析過去 365 天
- **後續執行**：每週分析過去 7 天
- **每日增量**：可設定每日分析前一天

### Crontab 設定

```bash
# 每週一 02:00 執行郵件分析
0 2 * * 1 cd /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server && \
    python3 scripts/email_analyzer.py 7 >> /tmp/email_analysis.log 2>&1
```

---

## 🔒 安全注意事項

### 1. 應用程式密碼

- ✅ 使用應用程式密碼，而非登入密碼
- ✅ 定期更換密碼
- ✅ 不要將密碼提交到 Git

### 2. 資料存取

- ✅ 僅分析收件夾
- ✅ 不刪除或修改郵件
- ✅ 僅存取在職員工 + 指定離職員工的郵件

### 3. 隱私保護

- ✅ 分析結果僅內部使用
- ✅ 不對外公開郵件內容
- ✅ 定期清理舊的分析檔案

---

## 📊 監控與維護

### 檢查分析狀態

```bash
# 查看最新分析結果
cat /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/email_analysis/analysis_summary.md

# 查看資料庫事件數量
sqlite3 /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db \
  "SELECT COUNT(*) FROM email_analysis;"

# 查看最近分析日誌
tail -50 /tmp/email_analysis.log
```

### 常見問題

**Q1: 連接郵箱失敗**

```
❌ 連接郵箱失敗：LOGIN failed
```

**解決**：
- 確認帳號密碼正確
- 確認使用應用程式密碼
- 檢查網路連線

**Q2: 找不到員工郵件**

```
📬 找到 0 封郵件
```

**解決**：
- 確認員工 Email 地址正確
- 檢查郵件時間範圍
- 確認郵箱資料夾名稱

**Q3: 案場識別不準確**

```
案場數量：0
```

**解決**：
- 確認 `cases` 表中有案場資料
- 檢查案場名稱是否匹配
- 加入更多案場關鍵字

---

## 🎯 最佳實踐

### 1. 首次執行

```bash
# 分析過去一年
python3 scripts/email_analyzer.py 365
```

### 2. 檢視結果

```bash
# 查看摘要
cat email_analysis/analysis_summary.md

# 查看 AI 記憶
cat email_analysis/ai_memory_injection.md

# 查看需要補充的問題
cat email_analysis/employee_requests.md
```

### 3. 發送補充請求

```bash
# 手動發送 Email 給相關員工
# 或使用通訊軟體通知
```

### 4. 定期執行

```bash
# 每週執行一次
python3 scripts/email_analyzer.py 7
```

---

## ✅ 驗收清單

- [ ] 設定 Outlook 應用程式密碼
- [ ] 設定環境變數
- [ ] 測試連接郵箱
- [ ] 執行首次分析（365 天）
- [ ] 檢視分析結果
- [ ] 發送員工補充請求
- [ ] 設定定期執行（crontab）
- [ ] 建立監控機制

---

**文件維護**：
- 最後更新：2026-03-01
- 負責人：Jenny
- 下次檢視：2026-03-08
