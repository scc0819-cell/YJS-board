#!/usr/bin/env python3
"""
改善 B（續）：優化附件上傳表單，增加檔案大小顯示
"""

from pathlib import Path

template_path = Path('/home/yjsclaw/.openclaw/workspace/server/templates/report_form_v3.html')

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 優化附件上傳說明
old_title = '📎 五、📎 附件上傳（可選）'
new_title = '''📎 五、附件上傳（可選）
<div style="background:#f0f9ff; padding:12px; border-radius:8px; margin:10px 0; border-left:4px solid #0284c7">
    <strong style="color:#0369a1">✅ 支援格式：</strong>jpg, png, gif, pdf, xlsx, docx, pptx, txt, zip<br/>
    <strong style="color:#0369a1">⚠️ 大小限制：</strong>每個檔案最大 10MB<br/>
    <strong style="color:#0369a1">🔒 安全檢查：</strong>自動進行副檔名驗證與病毒掃描
</div>'''

if old_title in content:
    content = content.replace(old_title, new_title)
    print("✅ 優化附件上傳說明")

# 2. 在 </body> 前增加 JavaScript 函數顯示檔案大小
body_end = content.rfind('</body>')
if body_end > 0:
    if 'showFileSize' not in content:
        script = '''
    <script>
    // 顯示選擇的檔案大小
    function showFileSize(input, displayId) {
        const display = document.getElementById(displayId);
        if (!display) return;
        
        const files = input.files;
        if (files.length === 0) {
            display.textContent = '';
            return;
        }
        
        let totalSize = 0;
        let overLimit = false;
        const MAX_SIZE = 10 * 1024 * 1024; // 10MB
        
        for (let i = 0; i < files.length; i++) {
            totalSize += files[i].size;
            if (files[i].size > MAX_SIZE) {
                overLimit = true;
            }
        }
        
        const sizeMB = (totalSize / 1024 / 1024).toFixed(2);
        const fileCount = files.length;
        
        if (overLimit) {
            display.innerHTML = `<span style="color:#dc3545">⚠️ 有檔案超過 10MB 限制！</span> (${fileCount} 個檔案，共 ${sizeMB} MB)`;
        } else {
            display.innerHTML = `<span style="color:#28a745">✓</span> ${fileCount} 個檔案，共 ${sizeMB} MB`;
        }
    }
    </script>
'''
        content = content[:body_end] + script + content[body_end:]
        print("✅ 增加檔案大小顯示函數")

# 寫入修改後的內容
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 附件上傳表單優化完成！")
