# 🧠 永久記憶系統 - 設計文件

> **版本：** 1.0
> **建立日期：** 2026 年 2 月 28 日
> **狀態：** 規劃中

---

## 📋 系統目標

1. **記憶連續性** - 跨 Session 保持脈絡不中斷
2. **智能檢索** - 隨時調用相關歷史討論
3. **自動關聯** - 相關話題自動連結
4. **無縫注入** - 新 Session 自動載入相關記憶

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                    記憶管理系統                              │
├─────────────────────────────────────────────────────────────┤
│  採集層  │  儲存層  │  索引層  │  檢索層  │  應用層        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 檔案結構

```
~/.openclaw/workspace/
├── MEMORY.md                      # 核心長期記憶
├── memory-system.md               # 本設計文件
├── memory/
│   ├── 2026-02-28.md              # 每日記憶（原始記錄）
│   ├── 2026-03-01.md
│   └── ...
├── memory-index/
│   ├── topics.json                # 主題索引
│   ├── entities.json              # 實體索引（人、事、物）
│   ├── sessions.json              # Session 索引
│   └── vectors/                   # 向量嵌入（未來）
├── memory-auto/
│   ├── capture.py                 # 自動採集腳本
│   ├── index.py                   # 索引建立腳本
│   └── retrieve.py                # 檢索腳本
└── sessions/
    └── *.jsonl                    # Session 完整記錄
```

---

## 🔄 記憶生命周期

```
對話發生
    │
    ▼
┌─────────────┐
│ 自動採集    │ ← 每次對話自動執行
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 結構化儲存  │ ← 分類：決策/事實/偏好/任務
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 建立索引    │ ← 關鍵字 + 主題 + 實體
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 建立關聯    │ ← 連結相關記憶
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 定期摘要    │ ← 每週/每月壓縮摘要
└─────────────┘
```

---

## 📊 記憶分類

### 1. 事實型記憶（Facts）
- 用戶基本資訊（姓名、公司、職位）
- 集團架構與公司資訊
- 專案細節與進度
- 技術規格與參數

### 2. 決策型記憶（Decisions）
- 重要決策與原因
- 選擇的方案與放棄的選項
- 決策時間與參與者

### 3. 偏好型記憶（Preferences）
- 用戶偏好（格式、風格、工具）
- 溝通習慣
- 工作流程偏好

### 4. 任務型記憶（Tasks）
- 已完成的任務
- 進行中的任務
- 任務鏈與依賴關係

### 5. 關係型記憶（Relationships）
- 人際關係（員工、合作夥伴、客戶）
- 組織關係
- 系統關聯

---

## 🔍 檢索機制

### 檢索層級

| 層級 | 說明 | 使用情境 |
|------|------|----------|
| **L1: 關鍵字** | 全文搜尋 | 快速定位 |
| **L2: 主題** | 主題分類檢索 | 探索相關話題 |
| **L3: 語意** | 向量相似度 | 找到語意相關內容 |
| **L4: 時間** | 時間範圍檢索 | 特定時期的討論 |
| **L5: 關聯** | 記憶圖譜導航 | 探索關聯網絡 |

---

## 📝 記憶格式標準

### 單條記憶格式
```json
{
  "id": "mem-20260228-001",
  "type": "decision",
  "timestamp": "2026-02-28T06:20:00+08:00",
  "session": "agent:main:main",
  "topic": ["自動化系統", "任務管理"],
  "entities": ["昱金生能源", "Jenny", "OpenClaw"],
  "content": "決定建立 6 人 Agent 團隊，包含 Jenny(主助理)、Argus(監控)、Scribe(報告)、Chronos(排程)、Athena(分析)、Hermes(通訊)",
  "importance": 8,
  "related": ["mem-20260228-002", "mem-20260228-003"],
  "tags": ["#agent", "#團隊", "#自動化"]
}
```

### 每日記憶格式
```markdown
# 2026-02-28 記憶記錄

## 📋 今日重點
- 建立任務管理看板系統
- 定義 6 人 Agent 團隊

## 🤝 決策記錄
- 決定採用 OpenClaw 內建記憶系統
- 決定使用網路共享儲存（91TB）

## 📊 事實記錄
- 集團有 5 家公司
- 網路共享共 7 個掛載點

## 💡 洞察與學習
- 用戶重視記憶連續性
- 需要視覺化任務看板

## 🔗 相關 Sessions
- session:agent:main:main (05:10-07:38)
```

---

## 🚀 實作步驟

### 階段 1：基礎建設（第 1 週）
- [ ] 建立記憶索引結構
- [ ] 實作自動採集腳本
- [ ] 建立記憶格式標準
- [ ] 設定 Session 自動儲存

### 階段 2：檢索系統（第 2 週）
- [ ] 實作關鍵字搜尋
- [ ] 實作主題檢索
- [ ] 建立記憶關聯機制
- [ ] 實作自動注入功能

### 階段 3：智能增強（第 3-4 週）
- [ ] 整合向量資料庫（可選）
- [ ] 實作語意搜尋
- [ ] 建立記憶圖譜
- [ ] 實作自動摘要

---

## 💻 核心程式碼範例

### 自動採集腳本
```python
#!/usr/bin/env python3
# memory-auto/capture.py

import json
from datetime import datetime
from pathlib import Path

class MemoryCapture:
    def __init__(self):
        self.workspace = Path.home() / '.openclaw' / 'workspace'
        self.memory_dir = self.workspace / 'memory'
        self.index_dir = self.workspace / 'memory-index'
        
    def capture_session(self, session_data):
        """捕獲 Session 對話"""
        # 提取重要內容
        memories = self.extract_memories(session_data)
        
        # 儲存到每日記憶
        self.save_daily_memories(memories)
        
        # 更新索引
        self.update_index(memories)
        
        # 建立關聯
        self.link_related_memories(memories)
        
    def extract_memories(self, session_data):
        """從對話中提取記憶"""
        memories = []
        # AI 提取邏輯
        return memories
```

### 自動注入腳本
```python
#!/usr/bin/env python3
# memory-auto/inject.py

class MemoryInjector:
    def __init__(self):
        self.workspace = Path.home() / '.openclaw' / 'workspace'
        
    def inject_context(self, session_start_data):
        """在新 Session 開始時注入相關記憶"""
        # 分析新 Session 的主題
        topics = self.analyze_topics(session_start_data)
        
        # 檢索相關記憶
        related_memories = self.search_related(topics)
        
        # 注入到上下文
        context = self.build_context(related_memories)
        
        return context
```

---

## 🎯 使用情境

### 情境 1：新 Session 自動載入脈絡
```
用戶：「繼續討論昨天的自動化系統」

系統自動：
1. 檢索「自動化系統」相關記憶
2. 載入昨天討論的 6 人 Agent 團隊
3. 載入任務看板架構
4. 注入到當前上下文
```

### 情境 2：跨主題關聯
```
用戶：「我們之前討論過採購相關的自動化嗎？」

系統自動：
1. 搜尋「採購」關鍵字
2. 找到 /mnt/q/採購 共享資料夾討論
3. 找到採購自動化任務鏈
4. 呈現完整脈絡
```

### 情境 3：決策追蹤
```
用戶：「為什麼我們決定用 6 個 Agent？」

系統自動：
1. 搜尋決策型記憶
2. 找到 2026-02-28 的決策記錄
3. 呈現決策原因與討論過程
```

---

## 📈 記憶品質指標

| 指標 | 目標值 | 衡量方式 |
|------|--------|----------|
| 記憶完整性 | > 95% | 對話儲存比例 |
| 檢索準確率 | > 90% | 相關記憶比例 |
| 注入及時性 | < 1 秒 | 載入時間 |
| 關聯正確率 | > 85% | 關聯品質評分 |
| 用戶滿意度 | > 4.5/5 | 定期問卷 |

---

## ⚠️ 注意事項

### 隱私與安全
- 敏感資訊加密儲存
- 權限控管（哪些記憶可被哪些 Agent 存取）
- 定期備份

### 記憶管理
- 避免記憶膨脹（定期摘要壓縮）
- 記憶過期機制（舊記憶歸檔）
- 記憶衝突解決（更新 vs 保留）

### 效能考量
- 索引大小控制
- 檢索速度優化
- 儲存空間管理

---

## 🔮 未來擴展

1. **向量搜尋** - 整合 ChromaDB/Pinecone
2. **記憶圖譜** - 視覺化記憶關聯網絡
3. **自動摘要** - AI 自動產生週/月摘要
4. **記憶分享** - 跨用戶記憶共享（需授權）
5. **記憶 API** - 提供外部系統存取

---

**文件版本：** 1.0
**最後更新：** 2026-02-28
**負責人：** Jenny (主助理)
