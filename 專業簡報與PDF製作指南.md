# 🎨 OpenClaw 專業簡報與 PDF 製作指南

> 讓你的報告像專業設計師做的一樣精美！

---

## 📋 已安裝工具

### ✅ 簡報工具
1. **Marp** - Markdown 轉專業簡報
2. **python-pptx** - Python 生成 PowerPoint
3. **Reveal.js** (透過 Pandoc) - HTML5 簡報

### ✅ PDF 工具
1. **WeasyPrint** - HTML+CSS 轉精美 PDF ⭐ 最推薦
2. **ReportLab** - Python 程式化 PDF
3. **Pandoc + LaTeX** - 學術級 PDF

---

## 🚀 快速開始

### 方法 1：一鍵生成（最簡單）⭐推薦

執行自動生成腳本：

```bash
~/.openclaw/workspace/scripts/create-beautiful-report.sh
```

**會自動生成：**
- `簡報.pdf` - Marp 製作的專業簡報
- `簡報.pptx` - PowerPoint 格式
- `報告.pdf` - WeasyPrint 製作的精美 PDF

**檔案位置：**
```
C:\Users\YJSClaw\Documents\Openclaw\2026-02-28\
```

---

### 方法 2：自訂 Marp 簡報

#### 步驟 1：建立 Markdown 檔案

```markdown
---
marp: true
theme: gaia  # 可選：gaia, default, uncover
class: lead
paginate: true
---

# 簡報標題

## 副標題

---

# 第一頁內容

- 重點 1
- 重點 2
- 重點 3

---

# 表格範例

| 項目 | 數值 |
|------|------|
| 任務 | 12 |
| 完成 | 10 |
```

#### 步驟 2：轉換為簡報

```bash
# 生成 PDF
marp report.md --output report.pdf --theme gaia

# 生成 PowerPoint
marp report.md --output report.pptx --theme gaia

# 生成 HTML
marp report.md --output report.html --theme gaia
```

---

### 方法 3：自訂 WeasyPrint PDF

#### 步驟 1：建立 HTML 檔案

```html
<!DOCTYPE html>
<html>
<head>
<style>
@page { size: A4; margin: 2.5cm; }
body { font-family: 'Microsoft YaHei', sans-serif; }
h1 { 
  color: #2563eb; 
  border-bottom: 4px solid #2563eb;
}
.card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 10px;
  margin: 20px 0;
}
</style>
</head>
<body>
<h1>任務報告</h1>

<div class="card">
  <h2>今日總結</h2>
  <p>完成 12 項任務</p>
</div>

<table>
  <tr><th>任務</th><th>狀態</th></tr>
  <tr><td>任務 1</td><td>✅ 已完成</td></tr>
</table>
</body>
</html>
```

#### 步驟 2：轉換為 PDF

```bash
weasyprint report.html report.pdf
```

---

## 🎨 主題模板

### Marp 內建主題

| 主題 | 風格 | 適用場合 |
|------|------|---------|
| `gaia` | 現代漸層 | 商業簡報 ⭐ |
| `default` | 簡潔 | 一般報告 |
| `uncover` | 全屏圖片 | 產品發表 |
| `beige` | 溫暖 | 教育訓練 |

### 自訂主題範例

```markdown
---
marp: true
theme: custom
style: |
  section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-family: 'Microsoft YaHei';
  }
  h1 {
    color: #ffd700;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
  }
---

# 金色文字配漸層背景
```

---

## 📊 實用範例

### 範例 1：任務統計報告

```markdown
---
marp: true
theme: gaia
paginate: true
---

# 📊 任務統計報告

## 2026 年 2 月 28 日

---

# 今日概況

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">

<div style="background: #22c55e; color: white; padding: 20px; border-radius: 10px;">

## ✅ 已完成

### 12 項

</div>

<div style="background: #3b82f6; color: white; padding: 20px; border-radius: 10px;">

## 🔄 執行中

### 3 項

</div>

</div>

---

# 任務明細

| 任務 | 狀態 | 時間 |
|------|------|------|
| 早晨檢查 | ✅ | 08:05 |
| 專案監控 | ✅ | 10:30 |
| 郵件處理 | 🔄 | - |
```

### 範例 2：專案進度報告

```html
<!DOCTYPE html>
<html>
<head>
<style>
@page { size: A4; margin: 2cm; }
body { font-family: sans-serif; }
h1 { color: #2563eb; }
.progress-bar {
  background: #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  margin: 10px 0;
}
.progress-fill {
  background: linear-gradient(90deg, #667eea, #764ba2);
  padding: 10px;
  color: white;
  text-align: right;
}
</style>
</head>
<body>
<h1>專案進度報告</h1>

<h2>整體進度</h2>
<div class="progress-bar">
  <div class="progress-fill" style="width: 75%;">75%</div>
</div>

<h2>各階段進度</h2>
<table>
  <tr><th>階段</th><th>進度</th></tr>
  <tr><td>需求分析</td><td>✅ 100%</td></tr>
  <tr><td>設計</td><td>✅ 100%</td></tr>
  <tr><td>開發</td><td>🔄 75%</td></tr>
  <tr><td>測試</td><td>⏳ 30%</td></tr>
</table>
</body>
</html>
```

---

## 🎯 進階技巧

### 1. 加入公司 Logo

**Marp:**
```markdown
---
marp: true
header: '![bg right:50% height:100px](logo.png)'
---
```

**WeasyPrint:**
```html
<div style="position: absolute; top: 2cm; right: 2cm;">
  <img src="logo.png" style="height: 50px;">
</div>
```

### 2. 加入 QR Code

```markdown
---
marp: true
footer: '![bg right:100px height:100px](qrcode.png)'
---
```

### 3. 程式碼高亮

````markdown
```python
# Python 程式碼範例
def hello():
    print("Hello, OpenClaw!")
```
````

### 4. 數學公式

```markdown
$$
E = mc^2
$$
```

---

## 📁 範例檔案位置

| 檔案 | 位置 |
|------|------|
| 範例 Markdown | `C:\Users\YJSClaw\Documents\Openclaw\2026-02-28\demo-report.md` |
| 範例 HTML | `C:\Users\YJSClaw\Documents\Openclaw\2026-02-28\demo-report.html` |
| 精美 PDF | `C:\Users\YJSClaw\Documents\Openclaw\2026-02-28\demo-report-beautiful.pdf` |
| 測試 PDF | `C:\Users\YJSClaw\Documents\Openclaw\2026-02-28\test-report.pdf` |
| 測試 PPTX | `C:\Users\YJSClaw\Documents\Openclaw\2026-02-28\test-report.pptx` |

---

## 🔧 常用命令

```bash
# Marp 轉換
marp input.md --output output.pdf
marp input.md --output output.pptx
marp input.md --output output.html

# WeasyPrint 轉換
weasyprint input.html output.pdf

# Pandoc 轉換
pandoc input.md -o output.pdf --pdf-engine=xelatex
pandoc input.md -t revealjs -o output.html
```

---

## 💡 最佳實踐

### 簡報設計原則

1. **一頁一重點** - 不要塞太多內容
2. **使用圖片** - 一图勝千言
3. **一致風格** - 保持顏色、字體統一
4. **留白** - 不要填滿整個頁面
5. **對比** - 確保文字清晰可讀

### PDF 設計原則

1. **專業字體** - 使用 Microsoft YaHei、Arial
2. **適當邊距** - 至少 2.5cm
3. **頁眉頁腳** - 加入頁碼、日期
4. **目錄** - 長文件加入目錄
5. **超連結** - 加入可點擊連結

---

## 🎨 配色建議

### 商業風格
```
主色：#2563eb (藍色)
輔色：#1e40af (深藍)
強調：#f59e0b (琥珀)
背景：#f9fafb (淺灰)
```

### 現代風格
```
漸層：#667eea → #764ba2 (紫藍)
文字：#1f2937 (深灰)
背景：#ffffff (純白)
```

### 活潑風格
```
主色：#ec4899 (粉紅)
輔色：#8b5cf6 (紫色)
強調：#10b981 (綠色)
```

---

## 📚 更多資源

- **Marp 文件**: https://marp.app/
- **WeasyPrint 文件**: https://weasyprint.org/
- **SlidesCarnival**: https://www.slidescarnival.com/ (免費模板)
- **Canva**: https://www.canva.com/ (線上設計)

---

## 🚀 下一步

1. **修改範例** - 打開 `demo-report.md` 修改內容
2. **執行腳本** - 執行 `create-beautiful-report.sh`
3. **查看結果** - 在 Windows 文件夾查看生成的檔案
4. **自訂風格** - 修改 CSS 創造自己的風格

---

**讓你的報告更專業、更有說服力！** 🦞✨
