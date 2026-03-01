# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## 🖥️ 昱金生能源 - 基礎設施

### NAS 網路共享（10 個掛載點）

| 掛載點 | 來源 | 用途 | 容量 | 已用 |
|--------|------|------|------|------|
| `/mnt/y` | `\\yjs\彰化辦公室 fs` | 彰化辦公室 | 13T | 4.2T (35%) |
| `/mnt/z` | `\\yjs\yjs fs` | 主檔案 | 13T | 4.2T (35%) |
| `/mnt/k` | `\\YJS\Accounting` | 會計 | 13T | 4.2T (35%) |
| `/mnt/w` | `\\YJS\homes` | 員工家目錄 | 13T | 4.2T (35%) |
| `/mnt/q` | `\\YJS\採購` | 採購 | 13T | 4.2T (35%) |
| `/mnt/r` | `\\YJS\專案管理` | 專案管理 | 13T | 4.2T (35%) |
| `/mnt/s` | `\\YJS\售電` | 售電 | 13T | 4.2T (35%) |
| `/mnt/t` | `\\YJS\未分類` | **（需確認用途）** | 13T | 4.2T (35%) |
| `/mnt/u` | `\\YJS\未分類` | **（需確認用途）** | 13T | 4.2T (35%) |
| `/mnt/v` | `\\YJS\未分類` | **（需確認用途）** | 13T | 4.2T (35%) |

### Windows C 槽
| 掛載點 | 容量 | 已用 |
|--------|------|------|
| `/mnt/c` | 952G | 167G (18%) |

### 系統掛載點（非業務用）
- `/mnt/wsl` - WSL 系統
- `/mnt/wslg` - WSL GUI

### 總計
- **業務用 NAS**: 10 個掛載點（130TB）
- **Windows C 槽**: 952G
- **實際可用**: 約 91TB（已用 35%）

---

## 📧 郵件伺服器設定

```
IMAP 伺服器：mail.yjsenergy.com:143
帳號：johnnys
密碼：Yjs0929176533cdef
郵箱：johnnys@yjsenergy.com
```

---

## 🤖 Agent 團隊

| 代號 | 名字 | 角色 | 專長 |
|------|------|------|------|
| main | Jenny | 主助理 | 綜合任務、決策協調 |

---

## 📁 核心系統路徑

```
/home/yjsclaw/.openclaw/workspace/
├── daily_report_server/          # 日報管理系統
│   ├── app.py                    # Flask 主服務
│   ├── data/users.json           # 15 位用戶資料
│   ├── data/app.db               # SQLite 資料庫
│   ├── email_analyzer_scheduler.py
│   ├── system_health_checker.py
│   └── templates/
├── server/                       # 郵件解析系統
│   ├── read_outlook_emails.py    # IMAP 提取
│   └── data/
└── memory/                       # 記憶系統
    ├── MEMORY.md                 # L1 策略層
    └── YYYY-MM-DD.md             # L2 每日層
```

### 輸出路徑（Windows 可存取）
```
/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/
├── email_analysis/               # 郵件解析結果
├── daily_report_attachments/     # 員工上傳附件
└── chairman_reports/             # 董事長專屬報告
```

---

## 👥 完整員工名單（15 位）

### 管理部（5 人）
- 20101 宋啓綸（admin）
- 20102 游若誼（manager）
- 22104 洪淑嫆（employee）
- 24106 楊傑麟（employee）
- 24108 褚佩瑜（employee）

### 工程部（5 人）
- 23102 楊宗衛（employee）
- 24302 張億峖（manager）
- 25105 陳明德（employee）
- 25305 李雅婷（employee）
- 25308 陳谷濱（manager）

### 維運部（1 人）
- 25108 陳靜儒（employee）

### 行政部（2 人）
- 25106 林天睛（employee）
- 25311 呂宜芹（employee）

### 設計部（2 人）
- 25107 顏呈晞（employee）
- 25110 高竹妤（employee）

---

## 🔑 重要決策記錄

- [2026-03-01] IMAP 設定確認：mail.yjsenergy.com:143, johnnys/Yjs0929176533cdef
- [2026-03-01] 建立 7 項 crontab 排程（服務/郵件/健檢/備份）
- [2026-03-01] 建立 Watchdog 機制（每 5 分鐘監控）
- [2026-03-01] 員工資料修正為 15 位（含員工代碼、部門）
- [2026-03-01] 決定不移入沙盒（需存取 NAS）
- [2026-03-01] 建立上下文監控機制（每 2 小時檢查，超過 8 小時建議重啟）
- [2026-03-01] 確認 NAS 掛載點為 10 個（y,z,k,w,q,r,s,t,u,v）

---
