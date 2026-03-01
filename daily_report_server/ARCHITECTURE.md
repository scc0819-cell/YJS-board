# 昱金生能源 - 員工日報管理系統架構文件

> 最後更新：2026-03-01 15:26  
> 版本：v2.0

---

## 📁 系統目錄結構

```
/home/yjsclaw/.openclaw/workspace/
├── daily_report_server/              # 主系統目錄
│   ├── app.py                        # Flask 主服務（Port 5000）
│   ├── data/
│   │   ├── users.json                # 15 位用戶資料
│   │   ├── app.db                    # SQLite 資料庫
│   │   └── audit.jsonl               # 稽核日誌
│   ├── templates/                    # HTML 模板
│   │   ├── login.html
│   │   ├── index_v3.html             # 管理員儀表板
│   │   ├── cases.html                # 案場總覽
│   │   ├── history.html              # 歷史記錄
│   │   └── ...
│   │
│   ├── 郵件解析系統
│   │   ├── email_analyzer_scheduler.py    # 排程器（每 30 分鐘）
│   │   └── learn_cases_from_emails.py     # 案場學習（每 30 分鐘）
│   │
│   ├── 系統監控
│   │   ├── system_health_checker.py       # 健康檢查（每 30 分鐘）
│   │   ├── keep_server_alive.sh           # Watchdog（每 5 分鐘）
│   │   ├── check_context_length.sh        # 上下文監控（每 2 小時）
│   │   └── generate_health_report.py      # 健康報告（每日 05:00）
│   │
│   ├── 案場管理
│   │   ├── optimize_case_names.py         # 案場名稱優化（每日 04:00）
│   │   └── import_cases_to_db.py          # 案場資料匯入
│   │
│   ├── 備份系統
│   │   └── backup_attachments.sh          # 附件備份（每日 03:00）
│   │
│   └── 文件與腳本
│       ├── SESSION_HANDOVER.md            # Session 接續摘要
│       ├── continue_session.sh            # 一鍵接續腳本
│       └── ARCHITECTURE.md                # 本文件
│
├── server/                           # 郵件解析系統（舊版）
│   ├── read_outlook_emails.py        # IMAP 郵件提取
│   └── data/
│
└── memory/                           # 記憶系統
    ├── MEMORY.md                     # L1 策略層
    ├── 2026-03-01.md                 # L2 每日層
    └── knowledge_z_drive.md          # 知識掃描結果
```

### 輸出路徑（Windows 可存取）

```
/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/
├── email_analysis/                   # 郵件解析結果
│   └── emails_YYYYMMDD_HHMMSS.json
├── full_email_analysis/              # 完整分析結果
│   ├── case_database_from_emails.json
│   ├── case_database_optimized.json
│   ├── case_analysis_report.txt
│   └── case_name_optimization_report.txt
├── daily_report_attachments/         # 員工上傳附件
└── chairman_reports/                 # 董事長專屬報告
```

---

## 🔄 完整排程（15 項）v3.0 優化版

| # | 排程 | 頻率 | 功能 | 日誌 |
|---|------|------|------|------|
| 1 | `@reboot` | 啟動時 | 自動啟動 Flask 服務 | `/tmp/server.log` |
| 2 | Watchdog | 每 5 分鐘 | 服務監控與自動重啟 | `/tmp/keep_server_alive.log` |
| 3 | 郵件解析 | 每 30 分鐘 (0,30) | IMAP 郵件提取 | `/tmp/email_analyzer_cron.log` |
| 4 | 案場學習 | 每 30 分鐘 (5,35) | 從郵件學習案場 | `/tmp/case_learning.log` |
| 5 | 完整分析 | 每日 02:00 | 深度郵件分析 | `/tmp/full_analysis.log` |
| 6 | 附件備份 | 每日 03:00 | 備份到 NAS | `/tmp/backup_cron.log` |
| 7 | 案場優化 | 每日 04:00 | 優化案場名稱 | `/tmp/case_optimization.log` |
| 8 | 健康檢查 | 每 30 分鐘 (15,45) | 系統健檢 | `/tmp/health_check.log` |
| 9 | 健康報告 | 每日 05:00 | 彙整健康報告 | `/tmp/weekly_health.log` |
| 10 | 上下文監控 | 每 2 小時 | 檢查 Session 長度 | `/tmp/context_monitor.log` |
| 11 | **知識掃描** | **每日 06:00** | **掃描 Z 槽知識庫** | `/tmp/knowledge_scan.log` |
| 12 | **記憶索引** | **每日 07:00** | **建立記憶檢索索引** | `/tmp/memory_index.log` |
| 13 | **每週回顧** | **每週一 09:00** | **彙整記憶到 MEMORY.md** | `/tmp/weekly_review.log` |
| 14 | **自我優化** | **每週日 23:00** | **系統自動檢測優化** | `/tmp/self_optimization.log` |

---

## 👥 用戶架構（15 位）

### 管理層（2 位）
- 20101 宋啓綸（admin）- 董事長
- 20102 游若誼（manager）- 管理部經理

### 管理部（4 位）
- 22104 洪淑嫆、24106 楊傑麟、24108 褚佩瑜

### 工程部（5 位）
- 23102 楊宗衛、24302 張億峖（manager）、25105 陳明德、25305 李雅婷、25308 陳谷濱（manager）

### 維運部（1 位）
- 25108 陳靜儒

### 行政部（2 位）
- 25106 林天睛、25311 呂宜芹

### 設計部（2 位）
- 25107 顏呈晞、25110 高竹妤

---

## 📊 資料庫結構

### cases 表
```sql
CREATE TABLE cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT UNIQUE NOT NULL,
    name TEXT,                    -- 案場名稱
    type TEXT,                    -- 案場類型（屋頂型/地面型/PPA 等）
    enabled INTEGER DEFAULT 1,
    created_at TEXT,
    updated_at TEXT
);
```

### case_status 表
```sql
CREATE TABLE case_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL,
    report_count INTEGER DEFAULT 0,
    email_count INTEGER DEFAULT 0,
    first_report DATE,
    last_report DATE,
    has_attachments INTEGER DEFAULT 0,
    employees TEXT,               -- 負責員工（逗號分隔）
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);
```

### employees 表
```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    department TEXT,
    role TEXT DEFAULT 'employee',
    enabled INTEGER DEFAULT 1,
    created_at TEXT,
    updated_at TEXT
);
```

### reports 表
```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT,
    case_id TEXT,
    report_date DATE,
    work_content TEXT,
    progress REAL,
    hours_worked REAL,
    has_attachment INTEGER DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_code),
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);
```

---

## 🔧 核心功能

### 1. 員工日報提交
- 員工登入系統提交日報
- 可上傳多個附件（圖片/Excel/Word/PDF）
- 自動關聯案場（下拉選單）
- 自動 AI 分析與建議

### 2. 郵件自動解析
- 每 30 分鐘掃描董事長郵箱
- 提取員工日報郵件
- 解析附件並儲存
- 建立案場知識庫

### 3. 案場學習系統
- 從郵件主旨/內文提取案場代碼
- 建立案場資料庫
- 每日凌晨優化案場名稱
- 匯入 SQLite 資料庫

### 4. 系統監控
- Watchdog 每 5 分鐘監控服務
- 健康檢查每 30 分鐘
- 上下文長度監控每 2 小時
- 自動修復常見問題

### 5. 備份系統
- 每日凌晨備份附件到 NAS
- 增量備份當年資料
- 完整備份去年資料

---

## 📈 系統狀態（2026-03-01 15:26）

| 指標 | 數值 | 狀態 |
|------|------|------|
| 用戶數 | 15 位 | ✅ 正常 |
| 案場數 | 24 個 | ✅ 正常 |
| 日報數 | 2 筆 | ⚠️ 待員工開始使用 |
| 郵件解析 | 315 封 | ✅ 正常 |
| 案場學習 | 11 個 | ✅ 正常 |
| 排程任務 | 11 項 | ✅ 正常 |

---

## 🎯 下一步優化計畫

### 短期（本週）
- [ ] 優化案場名稱提取演算法
- [ ] 測試完整郵件掃描（90 天）
- [ ] 建立案場名稱對照表

### 中期（下個月）
- [ ] 統一腳本路徑（全部移到 daily_report_server/）
- [ ] 清理舊版模板（index_v2.html 等）
- [ ] 建立 API 文件

### 長期（下季度）
- [ ] 導入 Grafana 監控儀表板
- [ ] 建立員工績效分析模型
- [ ] 整合電廠監控系統

---

## 🔑 重要決策記錄

- [2026-03-01] 停用 SEED_USERS，改用 users.json
- [2026-03-01] 確認 NAS 掛載點為 10 個（y,z,k,w,q,r,s,t,u,v）
- [2026-03-01] 建立案場學習自動排程
- [2026-03-01] 建立案場名稱優化排程（每日 04:00）

---

## 📞 維護聯絡

- 系統管理員：宋啓綸（admin）
- 技術支援：OpenClaw 文件（https://docs.openclaw.ai）
- 社區支援：Discord（https://discord.com/invite/clawd）
