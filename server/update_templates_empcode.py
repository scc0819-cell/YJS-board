#!/usr/bin/env python3
"""
改善：在模板中顯示工號
"""

from pathlib import Path
import re

templates_dir = Path('/home/yjsclaw/.openclaw/workspace/server/templates')

# 1. 更新首頁模板，增加工號顯示
index_template = templates_dir / 'index_v3.html'

if index_template.exists():
    with open(index_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在員工名單中增加工號顯示
    # 舊：{{ emp.name }}<br/><span style="font-size:11px;color:#888">{{ emp.department or "未分類" }}</span>
    # 新：EMP-XXX | 姓名<br/><span style="font-size:11px;color:#888">{{ emp.department or "未分類" }}</span>
    
    old_text = '{{ emp.name }}<br/><span style="font-size:11px;color:#888">{{ emp.department or "未分類" }}</span>'
    new_text = '{{ (emp.employee_code or "N/A") }} | {{ emp.name }}<br/><span style="font-size:11px;color:#888">{{ emp.department or "未分類" }}</span>'
    
    if old_text in content:
        content = content.replace(old_text, new_text)
        print("✅ 首頁員工名單已增加工號顯示")
    else:
        print("ℹ️  首頁模板格式不同，跳過工號顯示更新")
    
    with open(index_template, 'w', encoding='utf-8') as f:
        f.write(content)

# 2. 更新帳號管理頁面，增加工號欄位
admin_users_template = templates_dir / 'admin_users.html'

if admin_users_template.exists():
    with open(admin_users_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在表格中增加工號欄位
    if '<th>ID</th>' in content and '<th>姓名</th>' in content:
        # 在 ID 後增加工號
        content = content.replace('<th>ID</th>', '<th>ID</th>\n            <th>工號</th>')
        print("✅ 帳號管理頁面已增加工號欄位（表頭）")
    
    # 在新增表單中增加工號輸入
    if '<div class="muted">工號</div>' not in content:
        # 在部門前增加工號輸入
        insert_pos = content.find('<div class="muted">部門</div>')
        if insert_pos > 0:
            emp_code_input = '''<div>
          <div class="muted">工號</div>
          <input name="employee_code" placeholder="例如：EMP-003" style="width:160px" pattern="EMP-[0-9]{3}" title="格式：EMP-XXX" />
          <div class="muted" style="font-size:11px;margin-top:4px">格式：EMP-XXX</div>
        </div>
        '''
            content = content[:insert_pos] + emp_code_input + content[insert_pos:]
            print("✅ 帳號管理頁面已增加工號輸入")
    
    with open(admin_users_template, 'w', encoding='utf-8') as f:
        f.write(content)

# 3. 更新日報表單，顯示員工工號
report_form_template = templates_dir / 'report_form_v3.html'

if report_form_template.exists():
    with open(report_form_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在表單頂部顯示員工資訊
    if '<div class="top">' in content and '員工日報</div>' in content:
        old_top = '<div class="top">\n    <div style="font-weight:900">📝 員工日報</div>'
        new_top = '''<div class="top">
    <div>
      <div style="font-weight:900">📝 員工日報</div>
      <div style="font-size:12px;color:#c7d2fe;margin-top:4px">
        {{ current_user.employee_code or 'N/A' }} | {{ current_user.name }} ({{ current_user.department or '未分類' }})
      </div>
    </div>'''
        
        if old_top in content:
            content = content.replace(old_top, new_top)
            print("✅ 日報表單已增加員工資訊顯示（工號 + 姓名 + 部門）")
    
    with open(report_form_template, 'w', encoding='utf-8') as f:
        f.write(content)

print("\n✅ 模板更新完成！")
