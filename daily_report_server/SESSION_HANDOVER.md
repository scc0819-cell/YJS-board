# 📋 日報管理系統 - 完整進度摘要

> 最後更新：2026-03-01 15:26  
> 版本：v2.0  
> 這是給新 Session 的 AI 接續用的快速摘要

---

## 🎯 系統定位

昱金生能源集團的**員工日報管理系統**，包含：
- 員工每日提交工作日報（可上傳附件）
- 管理員即時查看提交狀況、高風險案場、逾期任務
- 自動從董事長郵箱提取員工日報郵件，建立案場知識庫
- 每 30 分鐘自動健康檢查，確保系統穩定

---

## 🏢 集團資訊

- **董事長**：宋啓綸（johnnys@yjsenergy.com）
- **總人數**：15 位（1 admin + 1 manager + 13 employees）
- **主攻業務**：公標案太陽光電（屋頂、停車場、風雨球場）
- **NAS 路徑**：/mnt/y,z,k,w,q,r,s（91TB 共享）

---

## 📧 郵件系統設定（重要！）

```
IMAP 伺服器：mail.yjsenergy.com:143
帳號：johnnys
密碼：Yjs0929176533cdef
郵箱：johnnys@yjsenergy.com
```

**已提取成果**：
- 過去 30 天：200 封郵件
- 日報郵件：60 封
- 案場資料庫：401 個案場
- 員工資料庫：15 位

---

## ⏰ 完整排程（11 項 crontab）

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

---

## 📁 核心檔案位置

```
/home/yjsclaw/.openclaw/workspace/daily_report_server/
├── app.py                          # 主服務（Flask）
├── data/users.json                 # 15 位用戶資料
├── data/app.db                     # SQLite 資料庫
├── email_analyzer_scheduler.py     # 郵件解析排程
├── system_health_checker.py        # 健康檢查系統
├── keep_server_alive.sh            # Watchdog 腳本
├── backup_attachments.sh           # 附件備份腳本
└── templates/
    ├── index_v3.html               # 首頁（含員工代碼/部門）
    ├── cases.html                  # 案場總覽
    ├── history.html                # 歷史記錄
    └── login.html                  # 登入頁

/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/
├── email_analysis/                 # 郵件分析結果
│   ├── emails_*.json               # 提取的郵件
│   ├── case_database.json          # 401 個案場
│   └── employee_database.json      # 15 位員工
└── daily_report_attachments/       # 員工上傳附件
```

---

## ✅ 已完成功能

1. **員工日報系統**
   - 員工登入提交日報（可上傳多個附件）
   - 管理員即時查看提交狀況
   - 首頁顯示：高風險 Top 5、逾期任務 Top 5
   - 員工名單：已提交/待提交（含員編、部門）

2. **郵件自動學習**
   - IMAP 連接董事長郵箱
   - 自動提取員工日報郵件
   - 分析郵件內容與附件
   - 建立案場知識庫（401 個案場）
   - 更新記憶系統

3. **系統監控**
   - 每 5 分鐘 Watchdog 監控服務
   - 每 30 分鐘健康檢查（6 大項目）
   - 自動修復常見問題
   - 嚴重問題上報機制

4. **資安強化**
   - 密碼雜湊（Werkzeug + salt）
   - 登入失敗鎖定
   - 稽核日誌記錄
   - 修改密碼功能

---

## 🚨 已知問題 / 待改善

1. **服務常駐** — 已用 crontab @reboot + Watchdog 解決
2. **附件中文檔名** — 需確認 UTF-8 編碼處理
3. **IMAP SSL** — 目前用 port 143（未加密），可考慮升級 993
4. **健康檢查優化** — 已驗證的項目要記錄，避免重複檢查

---

## 🎯 下一步待辦

- [ ] 執行第一次深度郵件分析（60 封日報完整學習）
- [ ] 建立 Grafana 監控儀表板（可選）
- [ ] 測試附件完整提取（Excel/Word/圖片）
- [ ] 優化案場經驗提取演算法

---

## 💬 與董事長的互動偏好

- 重視**視覺化**和**一目瞭然**的資訊
- 不喜歡重複確認，要**簡潔直接**
- 重視**記憶連續性**，不能斷裂
- 希望 AI 是「生活中的自動化好夥伴」

---

## 🔑 重要決策記錄

- [2026-03-01] IMAP 設定確認：mail.yjsenergy.com:143, johnnys/Yjs0929176533cdef
- [2026-03-01] 建立 7 項 crontab 排程（服務/郵件/健檢/備份）
- [2026-03-01] 建立 Watchdog 機制（每 5 分鐘監控）
- [2026-03-01] 員工資料修正為 15 位（含員工代碼、部門）
- [2026-03-01] 決定不移入沙盒（需存取 NAS）
- [2026-03-01] 建立上下文監控機制（每 2 小時檢查，超過 8 小時建議重啟）

---

> **給新 Session 的 AI**：
> 讀完這個摘要後，你可以：
> 1. 檢查服務狀態：`ps aux | grep app.py`
> 2. 檢查排程：`crontab -l`
> 3. 檢查健康：`python3 system_health_checker.py`
> 4. 繼續優化系統功能
> 
> 有不確定的事，請先查閱 `MEMORY.md` 和 `memory/2026-03-01.md`
