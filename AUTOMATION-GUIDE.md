# 🦞 OpenClaw 自動化任務看板系統

## 🎯 功能特色

### 1. **即時任務看板**
- 📊 一目了然查看所有任務狀態（執行中、待處理、已完成、失敗）
- 🔄 每 10 秒自動更新
- 📱 響應式設計，支援手機/平板/桌面

### 2. **自動化排程**
已設定的排程任務：
- ⏰ **早晨檢查** (每日 08:00) - 檢查郵件、日曆、天氣
- 🔄 **專案監控** (每 30 分鐘) - 監控 git 狀態
- 💓 **心跳檢查** (每小時) - 檢查緊急事項
- 🌙 **晚間總結** (每日 22:00) - 整理當日任務與規劃

### 3. **任務鏈自動化**
任務完成後自動產生後續任務，例如：
```
早晨檢查 → 整理檢查結果 → 產生待辦清單
檢查郵件 → 分類重要郵件 → 產生回覆草稿
Git 監控 → (如有變更) 提交變更報告
```

### 4. **Agent 追蹤**
- 記錄每個任務使用的 Agent
- 支援多 Agent 協作
- 可追蹤任務執行歷史

---

## 🚀 快速開始

### 啟動看板
```bash
# 方法 1: 使用啟動腳本
~/.openclaw/workspace/scripts/start-dashboard.sh

# 方法 2: 手動啟動
python3 ~/.openclaw/workspace/scripts/task-api.py 8080
```

### 開啟看板
在瀏覽器開啟：**http://localhost:8080**

---

## 📋 管理任務

### 使用命令列
```bash
# 列出所有任務
~/.openclaw/workspace/scripts/task-tracker.sh list

# 新增任務
~/.openclaw/workspace/scripts/task-tracker.sh add "任務名稱" "任務描述"

# 查看統計
~/.openclaw/workspace/scripts/task-tracker.sh stats

# 查看排程
~/.openclaw/workspace/scripts/task-tracker.sh cron
```

### 使用 API
```bash
# 獲取所有任務
curl http://localhost:8080/api/tasks

# 建立新任務
curl -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"name":"新任務","description":"描述","agent":"main"}'
```

---

## ⚙️ 自訂任務鏈

編輯任務鏈規則：`~/.openclaw/workspace/task-chain-rules.json`

範例：
```json
{
  "rules": [
    {
      "name": "自訂任務鏈",
      "trigger": "觸發任務名稱",
      "next_tasks": [
        {
          "name": "後續任務 1",
          "description": "描述",
          "delay_minutes": 5
        },
        {
          "name": "後續任務 2",
          "description": "描述",
          "condition": "has_changes"
        }
      ]
    }
  ]
}
```

---

## 📊 查看排程任務

```bash
# 列出所有排程
openclaw cron list

# 停用排程
openclaw cron disable <job-id>

# 啟用排程
openclaw cron enable <job-id>

# 立即執行排程任務（測試用）
openclaw cron run <job-id>
```

---

## 🔧 檔案位置

| 檔案/目錄 | 用途 |
|----------|------|
| `~/openclaw-dashboard/index.html` | 任務看板前端 |
| `~/.openclaw/workspace/scripts/task-api.py` | 看板後端 API |
| `~/.openclaw/workspace/scripts/task-chain-handler.py` | 任務鏈處理器 |
| `~/.openclaw/workspace/memory/task-board.json` | 任務資料庫 |
| `~/.openclaw/workspace/task-chain-rules.json` | 任務鏈規則 |

---

## 💡 使用情境

### 情境 1: 自動化早晨流程
1. 08:00 自動執行「早晨檢查」
2. 自動產生「整理檢查結果」任務
3. 自動產生「今日待辦清單」
4. 在看板上即時看到所有進度

### 情境 2: 專案監控
1. 每 30 分鐘自動檢查 git 狀態
2. 如有未提交變更，自動建立「提交變更」任務
3. 完成後自動建立「更新日誌」任務

### 情境 3: 郵件處理
1. 每小時檢查郵件
2. 發現重要郵件自動建立「回覆郵件」任務
3. 完成後自動建立「追蹤回覆」任務

---

## 🎨 看板預覽

```
┌─────────────────────────────────────────────────────────────┐
│  🦞 OpenClaw 任務看板                         🔄 ➕        │
├─────────────────────────────────────────────────────────────┤
│  🚀 執行中：3  │  📋 待處理：5  │  🎉 已完成：12 │  ⚠️ 失敗：1  │
├─────────────────────────────────────────────────────────────┤
│  📌 進行中任務                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ 🔄 早晨檢查       │  │ ⏳ 整理郵件       │                │
│  │ 描述...          │  │ 描述...          │                │
│  │ 🤖 main          │  │ 🤖 main          │                │
│  └──────────────────┘  └──────────────────┘                │
├─────────────────────────────────────────────────────────────┤
│  ⏰ 自動化排程                                               │
│  早晨檢查     每日 08:00    ✅ 啟用   下次：明天 08:00      │
│  專案監控     每 30 分鐘     ✅ 啟用   下次：10:35          │
│  心跳檢查     每小時       ✅ 啟用   下次：11:00          │
│  晚間總結     每日 22:00    ✅ 啟用   下次：今天 22:00     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 故障排除

### 看板無法開啟
```bash
# 檢查 API 是否運行
ps aux | grep task-api

# 重新啟動
pkill -f task-api.py
python3 ~/.openclaw/workspace/scripts/task-api.py 8080 &
```

### 任務鏈未觸發
```bash
# 檢查處理器是否運行
ps aux | grep task-chain

# 查看日誌
cat /tmp/task-chain.log
```

### 排程未執行
```bash
# 檢查 Gateway 狀態
openclaw status

# 重啟 Gateway
openclaw gateway restart
```

---

## 📞 支援

- 文件：https://docs.openclaw.ai
- 社群：https://discord.gg/clawd
- 技能市場：https://clawhub.com

---

**讓 OpenClaw 成為你的自動化好夥伴！** 🦞✨
