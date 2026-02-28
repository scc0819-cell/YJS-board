#!/bin/bash

# OpenClaw 專業簡報與 PDF 生成腳本

set -e

REPORT_NAME="${1:-任務報告}"
DATE=$(date +%Y-%m-%d)
WORKSPACE="$HOME/.openclaw/workspace"
OUTPUT_DIR="/mnt/c/Users/YJSClaw/Documents/Openclaw/$DATE"

echo "🦞 OpenClaw 專業簡報與 PDF 生成器"
echo "=================================="
echo
echo "報告名稱：$REPORT_NAME"
echo "輸出目錄：$OUTPUT_DIR"
echo

# 建立輸出目錄
mkdir -p "$OUTPUT_DIR"

# 1. 生成 Marp 簡報
echo "📽️  生成 Marp 簡報..."
cat > "$WORKSPACE/temp-report.md" << 'MARP_EOF'
---
marp: true
theme: gaia
class: lead
paginate: true
backgroundColor: #fff
style: |
  section {
    font-family: 'Microsoft YaHei', sans-serif;
  }
  h1 {
    color: #2563eb;
  }
  .highlight {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
  }
---

# 🦞 OpenClaw 任務報告

## REPORT_DATE

自動化任務管理系統

---

# 📊 今日統計

<div class="highlight">

## 任務完成概況

- ✅ **已完成**: 12 項
- 🔄 **執行中**: 3 項  
- ⏳ **待處理**: 5 項
- ❌ **失敗**: 0 項

</div>

---

# 📋 任務明細

| 任務名稱 | 狀態 | Agent | 完成時間 |
|----------|------|-------|----------|
| 早晨檢查 | ✅ | main | 08:05 |
| 專案監控 | ✅ | main | 10:30 |
| 郵件處理 | 🔄 | main | - |
| 客戶回覆 | ⏳ | main | - |

---

# 🚀 系統功能

## 完整自動化工具

✅ PDF 生成 (ReportLab, WeasyPrint)
✅ Excel 報表 (OpenPyXL)
✅ PowerPoint 簡報 (python-pptx, Marp)
✅ 郵件處理 (imap-tools)
✅ 日曆整合 (Google API)
✅ 網頁自動化 (Playwright)
✅ OCR 識別 (Tesseract)
✅ 語音功能 (pyttsx3)

---

# 📈 系統狀態

```
OpenClaw 版本：2026.2.27
模型：Qwen 3.5 397B Cloud
排程任務：4 個
任務鏈規則：已啟用
看板狀態：運行中
```

---

# 💡 下一步計劃

1. 整合 Gmail 自動檢查
2. 設定 Google 日曆同步
3. 建立更多任務鏈規則
4. 優化看板 UI

---

# 🎉 感謝

## 讓 OpenClaw 成為你的自動化好夥伴！

🦞✨
MARP_EOF

# 替換日期
sed -i "s/REPORT_DATE/$DATE/" "$WORKSPACE/temp-report.md"

# 使用 Marp 生成 PDF 和 PPTX
marp "$WORKSPACE/temp-report.md" --output "$OUTPUT_DIR/簡報.pdf" --pdf --theme gaia
marp "$WORKSPACE/temp-report.md" --output "$OUTPUT_DIR/簡報.pptx" --theme gaia

echo "✅ Marp 簡報已生成"

# 2. 生成 WeasyPrint PDF
echo "📄 生成 WeasyPrint 精美 PDF..."
cat > "$WORKSPACE/temp-report.html" << 'HTML_EOF'
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>OpenClaw 任務報告</title>
    <style>
        @page { size: A4; margin: 2.5cm; }
        body { font-family: 'Microsoft YaHei', sans-serif; line-height: 1.8; color: #333; }
        h1 { color: #2563eb; font-size: 32px; border-bottom: 4px solid #2563eb; padding-bottom: 15px; }
        h2 { color: #1e40af; font-size: 24px; margin-top: 35px; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 40px; border-radius: 15px; margin-bottom: 30px; text-align: center;
        }
        .header h1 { color: white; border: none; }
        .stats-grid {
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px; border-radius: 12px; text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-number { font-size: 48px; font-weight: bold; color: #2563eb; }
        .stat-label { font-size: 16px; color: #666; margin-top: 10px; }
        table { width: 100%; border-collapse: collapse; margin: 25px 0; }
        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 15px; text-align: left;
        }
        td { padding: 12px 15px; border-bottom: 1px solid #e5e7eb; }
        tr:nth-child(even) { background: #f9fafb; }
        .footer {
            margin-top: 50px; padding-top: 20px; border-top: 2px solid #e5e7eb;
            text-align: center; color: #6b7280; font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦞 OpenClaw 任務報告</h1>
        <p style="font-size: 18px; margin-top: 10px;">REPORT_DATE · 自動化任務管理系統</p>
    </div>

    <h2>📊 今日統計</h2>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number" style="color: #22c55e;">12</div>
            <div class="stat-label">✅ 已完成</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" style="color: #3b82f6;">3</div>
            <div class="stat-label">🔄 執行中</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" style="color: #f59e0b;">5</div>
            <div class="stat-label">⏳ 待處理</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" style="color: #ef4444;">0</div>
            <div class="stat-label">❌ 失敗</div>
        </div>
    </div>

    <h2>📋 任務明細</h2>
    <table>
        <thead>
            <tr>
                <th>任務名稱</th>
                <th>狀態</th>
                <th>Agent</th>
                <th>完成時間</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>早晨檢查</td><td>✅ 已完成</td><td>main</td><td>08:05</td></tr>
            <tr><td>專案監控</td><td>✅ 已完成</td><td>main</td><td>10:30</td></tr>
            <tr><td>郵件處理</td><td>🔄 執行中</td><td>main</td><td>-</td></tr>
            <tr><td>客戶回覆</td><td>⏳ 待處理</td><td>main</td><td>-</td></tr>
        </tbody>
    </table>

    <h2>🚀 系統功能</h2>
    <ul>
        <li>✅ PDF 生成 (ReportLab, WeasyPrint)</li>
        <li>✅ Excel 報表 (OpenPyXL)</li>
        <li>✅ PowerPoint 簡報 (python-pptx, Marp)</li>
        <li>✅ 郵件處理 (imap-tools)</li>
        <li>✅ 日曆整合 (Google API)</li>
        <li>✅ 網頁自動化 (Playwright)</li>
        <li>✅ OCR 識別 (Tesseract)</li>
        <li>✅ 語音功能 (pyttsx3)</li>
    </ul>

    <div class="footer">
        <p>🦞 讓 OpenClaw 成為你的自動化好夥伴！</p>
        <p>文件：https://docs.openclaw.ai</p>
    </div>
</body>
</html>
HTML_EOF

# 替換日期
sed -i "s/REPORT_DATE/$DATE/" "$WORKSPACE/temp-report.html"

# 使用 WeasyPrint 生成 PDF
weasyprint "$WORKSPACE/temp-report.html" "$OUTPUT_DIR/報告.pdf"

echo "✅ WeasyPrint PDF 已生成"

# 清理臨時檔案
rm -f "$WORKSPACE/temp-report.md" "$WORKSPACE/temp-report.html"

echo
echo "=================================="
echo "✅ 生成完成！"
echo "=================================="
echo
echo "檔案位置："
ls -lh "$OUTPUT_DIR" | grep -E "簡報 | 報告"
echo
echo "🎉 完成！"
