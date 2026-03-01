#!/usr/bin/env python3
"""
改善 #2：案場改為下拉選單
改善 #3：增加草稿自動儲存
改善 #4：優化附件上傳
"""

from pathlib import Path

template_path = Path('/home/yjsclaw/.openclaw/workspace/server/templates/report_form_v3.html')
if not template_path.exists():
    print("❌ 模板檔案未找到")
    exit(1)

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 改善 #2：在表單開頭增加案場下拉選單的 JavaScript 資料
# 找到 </head> 標籤前插入
head_end = content.find('</head>')
if head_end > 0:
    case_selector_script = '''
    <script>
    // 案場資料（從後端載入）
    const CASE_LIST = {{ cases_json | safe }};
    </script>
'''
    content = content[:head_end] + case_selector_script + content[head_end:]
    print("✅ 增加案場資料載入")

# 改善 #2：將案場 input 改為 select
# 工作項目案場
old_work_case = '''<input type="text" name="w_case_${id}" placeholder="案場代號" value="${data.case_id || ''}" />'''
new_work_case = '''<select name="w_case_${id}" class="case-select">
    <option value="">請選擇案場</option>
    ${CASE_LIST.map(c => `<option value="${c.id}" ${data.case_id===c.id?'selected':''}>${c.id} - ${c.name}</option>`).join('')}
</select>'''

if old_work_case in content:
    content = content.replace(old_work_case, new_work_case)
    print("✅ 工作項目案場改為下拉選單")

# 明日計畫案場
old_plan_case = '''<input type="text" name="p_case_${id}" placeholder="案場代號" value="${data.case_id || ''}" />'''
new_plan_case = '''<select name="p_case_${id}" class="case-select">
    <option value="">請選擇案場</option>
    ${CASE_LIST.map(c => `<option value="${c.id}" ${data.case_id===c.id?'selected':''}>${c.id} - ${c.name}</option>`).join('')}
</select>'''

if old_plan_case in content:
    content = content.replace(old_plan_case, new_plan_case)
    print("✅ 明日計畫案場改為下拉選單")

# 風險事項案場
old_risk_case = '''<input type="text" name="r_case_${id}" placeholder="案場代號" value="${data.case_id || ''}" />'''
new_risk_case = '''<select name="r_case_${id}" class="case-select">
    <option value="">請選擇案場</option>
    ${CASE_LIST.map(c => `<option value="${c.id}" ${data.case_id===c.id?'selected':''}>${c.id} - ${c.name}</option>`).join('')}
</select>'''

if old_risk_case in content:
    content = content.replace(old_risk_case, new_risk_case)
    print("✅ 風險事項案場改為下拉選單")

# 改善 #3：增加草稿自動儲存 JavaScript
# 找到 </body> 前插入
body_end = content.rfind('</body>')
if body_end > 0:
    draft_script = '''
    <script>
    // 草稿自動儲存（每 30 秒）
    let draftTimer = null;
    function saveDraft() {
        const formData = {
            work: [],
            plan: [],
            risk: []
        };
        // 儲存工作項目
        document.querySelectorAll('.work-item').forEach(card => {
            formData.work.push({
                case_id: card.querySelector('[name^="w_case_"]')?.value || '',
                work_type: card.querySelector('[name^="w_type_"]')?.value || '',
                progress: card.querySelector('[name^="w_progress_"]')?.value || '',
                hours: card.querySelector('[name^="w_hours_"]')?.value || '',
                work_content: card.querySelector('[name^="w_content_"]')?.value || '',
                output: card.querySelector('[name^="w_output_"]')?.value || '',
            });
        });
        localStorage.setItem('daily_report_draft', JSON.stringify(formData));
        
        // 顯示儲存提示
        const status = document.querySelector('.draft-status');
        if (status) {
            status.textContent = '✓ 已自動儲存';
            status.classList.add('saved');
            setTimeout(() => {
                status.textContent = '草稿';
                status.classList.remove('saved');
            }, 2000);
        }
    }
    
    // 載入草稿
    function loadDraft() {
        const saved = localStorage.getItem('daily_report_draft');
        if (saved) {
            try {
                const data = JSON.parse(saved);
                console.log('載入草稿:', data);
                // 可以在這裡自動回填表單
            } catch(e) {
                console.error('草稿載入失敗', e);
            }
        }
    }
    
    // 啟動自動儲存
    document.addEventListener('DOMContentLoaded', () => {
        loadDraft();
        draftTimer = setInterval(saveDraft, 30000); // 30 秒
        
        // 提交前清除草稿
        document.querySelector('form').addEventListener('submit', () => {
            localStorage.removeItem('daily_report_draft');
            if (draftTimer) clearInterval(draftTimer);
        });
    });
    </script>
'''
    content = content[:body_end] + draft_script + content[body_end:]
    print("✅ 增加草稿自動儲存")

# 改善 #4：優化附件上傳區域樣式
# 找到附件上傳部分並增加說明
old_attach = '附件上傳'
new_attach = '''📎 附件上傳（可選）
<span style="font-size:12px;color:#888">支援拖曳上傳，或點擊選擇檔案<br/>允許類型：jpg, png, pdf, xlsx, docx | 最大 10MB</span>'''

if old_attach in content:
    content = content.replace(old_attach, new_attach)
    print("✅ 優化附件上傳說明")

# 寫入修改後的內容
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 模板改善完成！")
