# 📧 郵件解析系統設定指南

## 目前狀態

**❌ 尚未執行郵件解析**

原因：需要設定 Outlook 郵箱帳號密碼

---

## 📋 需要您提供的資訊

### 1️⃣ Outlook 郵箱帳號

請提供以下資訊：

**郵箱帳號（YJS_EMAIL_USER）**:
```
例如：yjsenergy@outlook.com
或：admin@yjsenergy.com
```

**郵箱密碼（YJS_EMAIL_PASS）**:
```
您的 Outlook 密碼
```

**注意**: 
- 密碼會以**環境變數**方式儲存，不會寫入檔案
- 僅用於郵件讀取，不會儲存或記錄
- 建議使用**應用程式密碼**而非主密碼（如果 Outlook 支援）

---

## 🔐 設定方式

### 方法 1：臨時設定（僅當前 session）

```bash
export YJS_EMAIL_USER="your_email@outlook.com"
export YJS_EMAIL_PASS="your_password"
```

### 方法 2：永久設定（寫入 ~/.bashrc）

```bash
echo 'export YJS_EMAIL_USER="your_email@outlook.com"' >> ~/.bashrc
echo 'export YJS_EMAIL_PASS="your_password"' >> ~/.bashrc
source ~/.bashrc
```

### 方法 3：寫入環境變數檔案（推薦）

建立 `/home/yjsclaw/.openclaw/workspace/server/.env` 檔案：

```bash
YJS_EMAIL_USER=your_email@outlook.com
YJS_EMAIL_PASS=your_password
```

---

## 📊 郵件解析功能

### ✅ 已實現功能

1. **掃描 Outlook 郵箱**
   - 在職員工發送的日報郵件
   - 江勇毅（前員工）的歷史郵件
   - 包含案場資訊的所有郵件

2. **解析郵件內容**
   - 提取案場名稱（仁豐國小、馬偕護專、大城國小等）
   - 解析工作內容、進度、問題
   - 識別發送人、日期、主旨

3. **解析附件**
   - 📷 **圖片檔**（JPG, PNG, GIF）
     - 使用 OCR 識別圖片中的文字
     - 分析圖片內容（施工照片、圖表等）
   - 📊 **Excel 檔**（XLS, XLSX）
     - 讀取表格數據
     - 提取進度、工時、物料等資訊
   - 📄 **Word 檔**（DOC, DOCX）
     - 讀取文件內容
     - 提取報告、會議記錄等

4. **建立 AI 記憶**
   - 案場脈絡資料庫
   - 員工工作歷史
   - 常見問題與解決方案
   - 物料供應商資訊

5. **主動要求補充**
   - 檢測不完整的日報
   - 自動發送郵件要求員工補充資訊

---

## 🎯 解析流程

```
1. 連接 Outlook 郵箱
   ↓
2. 掃描收件匣（過去 30 天）
   ↓
3. 過濾員工發送的日報郵件
   ↓
4. 解析郵件內容
   ├── 提取案場名稱
   ├── 解析工作內容
   ├── 識別進度、工時
   └── 提取問題與協助請求
   ↓
5. 解析附件
   ├── 圖片 → OCR 文字識別 + 內容分析
   ├── Excel → 表格數據提取
   └── Word → 文件內容解析
   ↓
6. 儲存到資料庫
   ├── 案場脈絡
   ├── 員工工作歷史
   ├── 附件內容摘要
   └── AI 記憶標籤
   ↓
7. 生成分析報告
   └── 發送給董事長
```

---

## 📁 輸出內容

解析後會產生以下檔案：

```
/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/email_analysis/

├── parsed_emails.json      # 解析後的郵件內容
├── attachments/            # 附件儲存目錄
│   ├── images/            # 圖片檔
│   ├── excel/             # Excel 檔
│   └── word/              # Word 檔
├── ocr_results/           # OCR 識別結果
│   └── images/            # 圖片文字識別
├── case_context.json      # 案場脈絡資料庫
├── employee_history.json  # 員工工作歷史
└── ai_memory.json         # AI 記憶摘要
```

---

## 🔍 解析範例

### 郵件範例

**寄件者**: 楊宗衛 <yang_zong_wei@yjsenergy.com>
**主旨**: 【日報】2026-02-28 仁豐國小光電案場
**日期**: 2026-02-28 17:30
**附件**: 
- 施工照片_01.jpg
- 進度表_20260228.xlsx

**內容**:
```
宋董好，

今日工作項目：
1. 光電板安裝（第 55-60 片）
2. 直流接線作業
3. 逆變器測試

進度：95%
工時：8 小時

問題：水塔遮陰影響發電效率

請見附件照片和進度表。

楊宗衛
```

### 解析結果

```json
{
  "email_id": "abc123",
  "from": "yang_zong_wei",
  "date": "2026-02-28",
  "case_id": "ren_feng_elementary",
  "case_name": "仁豐國小",
  "work_items": [
    {
      "type": "施工",
      "content": "光電板安裝（第 55-60 片）",
      "progress": 95,
      "hours": 8
    },
    {
      "type": "測試",
      "content": "逆變器測試"
    }
  ],
  "issues": [
    {
      "desc": "水塔遮陰影響發電效率",
      "severity": "medium"
    }
  ],
  "attachments": [
    {
      "filename": "施工照片_01.jpg",
      "type": "image",
      "ocr_text": "仁豐國小光電案場 2026-02-28...",
      "analysis": "顯示光電板安裝情況，部分區域有水塔遮陰"
    },
    {
      "filename": "進度表_20260228.xlsx",
      "type": "excel",
      "data": {
        "total_panels": 60,
        "installed": 57,
        "progress": "95%"
      }
    }
  ]
}
```

---

## 🚀 立即執行

請提供郵箱帳號密碼後，執行以下命令：

```bash
# 1. 設定環境變數
export YJS_EMAIL_USER="your_email@outlook.com"
export YJS_EMAIL_PASS="your_password"

# 2. 執行郵件解析
cd /home/yjsclaw/.openclaw/workspace/server
python3 email_analyzer.py --scan --days 30

# 3. 查看解析結果
ls -lh /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/email_analysis/
cat /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/email_analysis/parsed_emails.json | head -100
```

---

## 📊 預期效益

### 解析過去 30 天郵件

**假設情境**:
- 郵件總數：500 封
- 員工日報：150 封
- 案場相關：300 封
- 附件總數：200 個（圖片 150 + Excel 30 + Word 20）

**解析結果**:
- ✅ 建立 150 筆員工工作記錄
- ✅ 提取 20 個案場脈絡資訊
- ✅ 分析 200 個附件內容
- ✅ 生成 50 頁 AI 記憶摘要
- ✅ 識別 30 個常見問題與解決方案

### AI 學習效益

**系統會記住**:
- 每個員工的專長和工作模式
- 每個案場的歷史進度和問題
- 物料供應商的交貨狀況
- 常見施工問題的解決方案
- 天氣對施工的影響模式

**董事長受益**:
- 掌握案場完整脈絡
- 了解員工工作實績
- 提前預警潛在問題
- 數據驅動決策

---

## ⚠️ 注意事項

1. **隱私保護**
   - 僅解析員工發送的日報郵件
   - 不解析私人郵件
   - 解析結果僅限內部使用

2. **附件儲存**
   - 附件會複製到本地儲存
   - 原始郵件保持不變
   - 定期清理舊附件（保留 90 天）

3. **執行時間**
   - 首次解析（30 天）：約 30-60 分鐘
   - 每日增量解析：約 5-10 分鐘
   - 建議在離峰時段執行

4. **網路依賴**
   - 需要網路連接 Outlook
   - OCR 服務可能需要網路
   - 建議使用有線網路

---

## 📞 下一步

**請提供**:
1. Outlook 郵箱帳號
2. Outlook 密碼

**我會立即**:
1. 設定環境變數
2. 執行郵件解析（過去 30 天）
3. 生成分析報告
4. 向您匯報解析結果

---

**聯絡方式**: 請直接回覆郵箱帳號密碼，或告訴我您偏好的設定方式。
