#!/usr/bin/env python3
"""
改善 C（完成）：在案件明細頁增加風險/任務歷史記錄顯示
"""

from pathlib import Path

app_path = Path('/home/yjsclaw/.openclaw/workspace/server/app.py')

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 在 case_detail 函數中，找到 risks 查詢後，增加 risk_history 查詢
# 找到 risks 查詢的結束位置
risks_end = content.find("        # 明日計畫（最近 60 筆）")
if risks_end > 0:
    # 在 risks 查詢後增加 risk_history 查詢
    insert_pos = risks_end
    
    history_code = '''
        # ✅ 改善 C：風險歷史記錄（最近 50 筆）
        risk_history = db.execute(
            """
            SELECT h.*, r.risk_desc, r.case_id
            FROM risk_history h
            JOIN risk_items r ON h.risk_id = r.id
            WHERE r.case_id = ?
            ORDER BY h.changed_at DESC
            LIMIT 50
            """,
            (case_id,)
        ).fetchall()
        
        # ✅ 改善 C：任務歷史記錄（最近 50 筆）
        task_history = db.execute(
            """
            SELECT h.*, t.title, t.case_id
            FROM task_history h
            JOIN tasks t ON h.task_id = t.id
            WHERE t.case_id = ?
            ORDER BY h.changed_at DESC
            LIMIT 50
            """,
            (case_id,)
        ).fetchall()

'''
    
    content = content[:insert_pos] + history_code + content[insert_pos:]
    print("✅ 增加風險/任務歷史記錄查詢")

# 在 render_template 中增加 risk_history 和 task_history 參數
# 找到 case_detail 的 render_template 呼叫
template_call = content.find("return render_template('case_detail.html'")
if template_call > 0:
    # 找到這行的結尾
    line_end = content.find(")", template_call)
    if line_end > 0:
        # 在 ) 前增加參數
        old_text = content[template_call:line_end]
        new_text = old_text.rstrip()[:-1] + ",\n        risk_history=risk_history,\n        task_history=task_history\n    )"
        content = content[:template_call] + new_text + content[line_end:]
        print("✅ 更新 render_template 參數")

# 寫入修改後的內容
with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 案件明細頁歷史記錄功能完成！")
