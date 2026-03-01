#!/usr/bin/env python3
"""
改善 A（完成）：更新日報表單模板，案場改為下拉選單
"""

from pathlib import Path
import re

template_path = Path('/home/yjsclaw/.openclaw/workspace/server/templates/report_form_v3.html')

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在 <head> 區域增加案場資料載入
head_end = content.find('</head>')
if head_end > 0:
    # 檢查是否已有 CASE_LIST
    if 'CASE_LIST' not in content:
        script = '''
    <script>
    // 案場字典（從後端載入）
    const CASE_LIST = {{ cases_json | safe }};
    </script>
'''
        content = content[:head_end] + script + content[head_end:]
        print("✅ 增加 CASE_LIST 載入")

# 2. 將工作項目的案場 input 改為 select
# 找到工作項目的模板部分
work_case_pattern = r'<input type="text" name="w_case_\$\{id\}" placeholder="案場代號" value="\$\{data\.case_id \|\| \'\'\}" />'
work_case_replacement = '''<select name="w_case_${id}" class="case-select" style="width:100%;padding:10px 12px;border:2px solid #e9ecef;border-radius:8px;font-size:14px;">
    <option value="">請選擇案場</option>
    ${CASE_LIST.map(c => `<option value="${c.case_id}" ${data.case_id===c.case_id?'selected':''}>${c.case_code || c.case_id} - ${c.name}</option>`).join('')}
</select>'''

if re.search(work_case_pattern, content):
    content = re.sub(work_case_pattern, work_case_replacement, content)
    print("✅ 工作項目案場改為下拉選單")

# 3. 將明日計畫的案場 input 改為 select
plan_case_pattern = r'<input type="text" name="p_case_\$\{id\}" placeholder="案場代號" value="\$\{data\.case_id \|\| \'\'\}" />'
plan_case_replacement = '''<select name="p_case_${id}" class="case-select" style="width:100%;padding:10px 12px;border:2px solid #e9ecef;border-radius:8px;font-size:14px;">
    <option value="">請選擇案場</option>
    ${CASE_LIST.map(c => `<option value="${c.case_id}" ${data.case_id===c.case_id?'selected':''}>${c.case_code || c.case_id} - ${c.name}</option>`).join('')}
</select>'''

if re.search(plan_case_pattern, content):
    content = re.sub(plan_case_pattern, plan_case_replacement, content)
    print("✅ 明日計畫案場改為下拉選單")

# 4. 將風險事項的案場 input 改為 select
risk_case_pattern = r'<input type="text" name="r_case_\$\{id\}" placeholder="案場代號" value="\$\{data\.case_id \|\| \'\'\}" />'
risk_case_replacement = '''<select name="r_case_${id}" class="case-select" style="width:100%;padding:10px 12px;border:2px solid #e9ecef;border-radius:8px;font-size:14px;">
    <option value="">請選擇案場</option>
    ${CASE_LIST.map(c => `<option value="${c.case_id}" ${data.case_id===c.case_id?'selected':''}>${c.case_code || c.case_id} - ${c.name}</option>`).join('')}
</select>'''

if re.search(risk_case_pattern, content):
    content = re.sub(risk_case_pattern, risk_case_replacement, content)
    print("✅ 風險事項案場改為下拉選單")

# 5. 增加 JavaScript 函數，動態生成下拉選單選項
# 在 </body> 前增加
body_end = content.rfind('</body>')
if body_end > 0:
    # 檢查是否已有 updateCaseSelects
    if 'updateCaseSelects' not in content:
        script = '''
    <script>
    // 動態更新所有案場下拉選單
    function updateCaseSelects() {
        document.querySelectorAll('.case-select').forEach(select => {
            const currentValue = select.value;
            select.innerHTML = '<option value="">請選擇案場</option>' + 
                CASE_LIST.map(c => 
                    `<option value="${c.case_id}" ${currentValue===c.case_id?'selected':''}>${c.case_code || c.case_id} - ${c.name}</option>`
                ).join('');
        });
    }
    
    // 頁面載入時更新
    document.addEventListener('DOMContentLoaded', () => {
        updateCaseSelects();
    });
    </script>
'''
        content = content[:body_end] + script + content[body_end:]
        print("✅ 增加動態更新函數")

# 寫入修改後的內容
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 日報表單模板更新完成！")
print("📋 現在案場改為下拉選單，禁止自由輸入")
