#!/usr/bin/env python3
"""
改善：在首頁和管理頁面增加部門顯示
"""

from pathlib import Path

# 1. 更新首頁模板，增加部門顯示
index_template = Path('/home/yjsclaw/.openclaw/workspace/server/templates/index_v3.html')

if index_template.exists():
    with open(index_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在員工名單中增加部門顯示
    old_emp_dept = '{{ emp.name }}'
    new_emp_dept = '{{ emp.name }}<br/><span style="font-size:11px;color:#888">{{ emp.department or "未分類" }}</span>'
    
    if old_emp_dept in content and '已提交' in content:
        content = content.replace(old_emp_dept, new_emp_dept, content.count('已提交'))
        print("✅ 首頁員工名單已增加部門顯示")
    
    with open(index_template, 'w', encoding='utf-8') as f:
        f.write(content)

# 2. 更新帳號管理頁面，增加部門欄位
admin_users_template = Path('/home/yjsclaw/.openclaw/workspace/server/templates/admin_users.html')

if admin_users_template.exists():
    with open(admin_users_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在表格中增加部門欄位
    if '<th>ID</th>' in content and '<th>姓名</th>' in content:
        # 在 ID 後增加部門
        content = content.replace('<th>ID</th>', '<th>ID</th>\n            <th>部門</th>')
        print("✅ 帳號管理頁面已增加部門欄位（表頭）")
    
    # 在新增表單中增加部門輸入
    if '<div class="muted">部門</div>' not in content:
        # 在角色前增加部門輸入
        insert_pos = content.find('<div>\n          <div class="muted">角色</div>')
        if insert_pos > 0:
            dept_input = '''<div>
          <div class="muted">部門</div>
          <input name="department" placeholder="例如：工程部" style="width:160px" list="dept-list" />
          <datalist id="dept-list">
            <option value="管理部">
            <option value="工程部">
            <option value="財務部">
            <option value="維運部">
          </datalist>
        </div>
        '''
            content = content[:insert_pos] + dept_input + content[insert_pos:]
            print("✅ 帳號管理頁面已增加部門輸入（含下拉建議）")
    
    with open(admin_users_template, 'w', encoding='utf-8') as f:
        f.write(content)

print("\n✅ 模板更新完成！")
