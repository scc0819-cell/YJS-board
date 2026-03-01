# 🧠 MEMORY.md — Jenny 的長期記憶

> 最後更新：2026-02-28 08:03
> 這是 Jenny 的策略記憶層。記錄重要決策、人物關係、偏好、教訓。
> 每日記憶在 `memory/YYYY-MM-DD.md`，這裡只留精華。

---

## 👤 關於宋董事長（宋啓綸）

- 昱金生能源集團創辦人兼董事長
- 時區：Asia/Taipei (GMT+8)
- 重視**視覺化**和**一目瞭然**的資訊呈現
- 喜歡參考 YouTube 上的 OpenClaw 教學影片，要求達到同等水準
- 希望 AI 能成為「生活中的自動化好夥伴」，不只是工具
- 非常在意記憶連續性，不能有斷裂或片段化

## 🏢 集團架構

- **昱金生能源** — 電廠投資持有，資本額 2.7 億
- **矅澄科技** — 電廠維運管理
- **緯基能源** — 統包 EPC 工程
- **泰陽電力** — 綠電轉供交易，資本額 3000 萬
- **錡緯投資** — 控股公司（稅務規劃）
- 主攻：公標案屋頂、停車場、風雨球場太陽光電
- 不做：民間案場開發、土地開發

## 🖥️ 基礎設施

- NAS 共享：91TB，7 掛載點（/mnt/y,z,k,w,q,r,s）
- /mnt/y = 彰化辦公室、/mnt/z = 主檔案、/mnt/k = 會計
- /mnt/w = 員工家目錄、/mnt/q = 採購、/mnt/r = 專案管理、/mnt/s = 售電
- 輸出路徑：`/mnt/c/Users/YJSClaw/Documents/Openclaw/`
- 中文 PDF：使用 ReportLab + 微軟正黑體（`/mnt/c/Windows/Fonts/msjh.ttc`）

## 🤖 Agent 團隊（2026-02-28 建立）

| 代號 | 名字 | 角色 | 專長 |
|------|------|------|------|
| main | Jenny | 主助理 | 綜合任務、決策協調 |
| monitor | Argus | 監控 | 系統監控、異常偵測 |
| reporter | Scribe | 報告 | 報表生成、文件整理 |
| scheduler | Chronos | 排程 | 排程管理、任務分配 |
| analyst | Athena | 分析 | 數據分析、決策支援 |
| communicator | Hermes | 通訊 | 郵件處理、訊息通知 |

## 📌 重要決策記錄

- [2026-03-01] 完成 A→B→C 三項關鍵改善（案場字典/附件上傳/歷程追蹤），系統正式上線
- [2026-03-01] 決定附件存放路徑為 `/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments/`（Windows 可存取）
- [2026-03-01] 決定附件備份策略：每日增量備份當年資料，每週完整備份去年資料
- [2026-02-28] 決定採用 OpenClaw 內建記憶系統增強，不引入外部向量資料庫
- [2026-02-28] 決定使用 NAS 網路共享（91TB），不掛載雲端硬碟
- [2026-02-28] 建立 6 人 Agent 團隊架構
- [2026-02-28] 模型切換至 anthropic/claude-opus-4-6（OPUS）
- [2026-02-28] 依董事長指示移除「專案監控」cron job（保留：心跳/早晨檢查/晚間總結）

## 💡 教訓與注意事項

- 中文 PDF 在 Linux 上需嵌入字體，否則亂碼
- WSL2/Windows 存取 localhost 服務：需確保服務常駐（必要時配合 portproxy/網路設定），否則 Windows 端會開不起來
- 用戶不希望看到太多重複的確認訊息，要簡潔直接
- 模型切換用 `session_status` 工具的 `model` 參數
- 要確認模型可用性再回覆，不要亂猜

## 🔗 常用參考

- 員工日報腳本：`scripts/generate-daily-report.py`
- 任務看板數據：`task-board.json`
- 記憶管理：`scripts/memory_manager.py`
- Session 記憶注入器：`scripts/session_injector.py`
- 指揮中心看板（暗色系 dashboard）：`task-board-dashboard.html`


---

## 📧 郵件完整解析（2026-03-01）

**解析成果**:
- 總郵件：2,783 封
- 日報：1,553 封（55.8%）
- 活躍用戶：10 位（從郵件解析）
- ⚠️ ~~401 個案場~~ → **錯誤數字，已廢棄**

**✅ 正確案場數量**：**26 個**（來自 Z 槽知識掃描）

**✅ 正確員工人數**：**15 位**（14 位員工 + 董事長）

**員工績效 TOP 3**:
1. 陳明德（工程部）- 294 封，負責 60 個案場
2. 張億峖（工程部）- 281 封，日報率 99.6%
3. 陳靜儒（維運部）- 249 封，維運報告為主

**前 5 大活躍案場**（郵件提及次數）:
1. 04-720（149 封）- 陳谷濱負責
2. 02-2999（127 封）- 陳靜儒負責
3. 25-1（46 封）
4. 18-1（46 封）
5. 30-1（44 封）

**關鍵洞察**:
- 陳明德：案場冠軍，負責 60 個案場
- 張億峖：日報模範，提交率 99.6%
- 高竹妤：設計支援 43 個案場
- 陳靜儒：維運報告，附件量大

**輸出檔案**:
- `/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/full_email_analysis/`
- ~~case_database.json（401 個，錯誤）~~ → **已廢棄**
- ~~employee_database.json（10 位，不完整）~~ → **已廢棄**
- full_analysis_report.json（完整報告）

**正確數據來源**:
- 案場：Z 槽掃描 `memory/knowledge_z_drive.md`（26 個）
- 員工：日報系統 `daily_report_server/data/app.db`（15 位）

