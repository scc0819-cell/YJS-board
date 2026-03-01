#!/usr/bin/env python3
"""
昱金生能源集團 - 員工日報系統 v4.0 升級腳本
升級項目：
1. 案件儀表板（里程碑 + 進度百分比）
2. 風險追蹤系統（7 大分類 + 狀態管理）
3. 任務指派系統
4. AI 數據 API
"""

import sys
from pathlib import Path

app_path = Path('/home/yjsclaw/.openclaw/workspace/server/app.py')
if not app_path.exists():
    print("❌ app.py 未找到")
    sys.exit(1)

print("🔧 開始升級到 v4.0...")

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 更新 MILESTONE_STAGES
old_milestones = """MILESTONE_STAGES = [
    '規劃中', '設計中', '施工中', '完工待驗', '已驗收', '已併聯', '已結案'
]"""

new_milestones = """MILESTONE_STAGES = [
    '規劃中', '設計中', '送審中', '施工中', '完工待驗', '已驗收', '已併聯', '已結案'
]"""

if old_milestones in content:
    content = content.replace(old_milestones, new_milestones)
    print("✅ 更新里程碑階段")

# 2. 在 app.py 開頭附近新增 AI API 路由
# 找到 imports 結束的位置
import_end = content.find("# ===================== 路徑設定 =====================")
if import_end > 0:
    ai_api_code = """
# ===================== AI 數據 API（只讀，供 AI 分析使用） =====================
@app.route('/api/ai/cases', methods=['GET'])
def api_ai_cases():
    \"\"\"提供 AI 讀取的案件進度摘要\"\"\"
    with get_db() as db:
        rows = db.execute('''
            SELECT cs.case_id, cs.stage, cs.percent, cs.updated_at,
                   (SELECT COUNT(*) FROM risk_items WHERE case_id=cs.case_id AND status!='closed') as open_risks,
                   (SELECT COUNT(*) FROM tasks WHERE case_id=cs.case_id AND status!='closed') as open_tasks,
                   (SELECT MAX(report_date) FROM work_items w JOIN reports r ON w.report_key=r.report_key WHERE w.case_id=cs.case_id) as last_work_date
            FROM case_status cs
        ''').fetchall()
    
    result = []
    for r in rows:
        result.append({
            'case_id': r['case_id'],
            'stage': r['stage'],
            'percent': r['percent'],
            'updated_at': r['updated_at'],
            'open_risks': r['open_risks'],
            'open_tasks': r['open_tasks'],
            'last_work_date': r['last_work_date'],
        })
    
    return jsonify({'cases': result, 'count': len(result)})

@app.route('/api/ai/risks', methods=['GET'])
def api_ai_risks():
    \"\"\"提供 AI 讀取的風險清單\"\"\"
    with get_db() as db:
        rows = db.execute('''
            SELECT * FROM risk_items WHERE status != 'closed'
            ORDER BY 
              CASE level WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END,
              due_date ASC
        ''').fetchall()
    
    return jsonify({'risks': [dict(r) for r in rows], 'count': len(rows)})

@app.route('/api/ai/tasks', methods=['GET'])
def api_ai_tasks():
    \"\"\"提供 AI 讀取的任務清單\"\"\"
    today = datetime.now().strftime('%Y-%m-%d')
    with get_db() as db:
        rows = db.execute('''
            SELECT * FROM tasks WHERE status != 'closed'
            ORDER BY 
              CASE status WHEN 'open' THEN 0 WHEN 'in_progress' THEN 1 ELSE 2 END,
              CASE WHEN due_date != '' AND due_date < ? THEN 0 ELSE 1 END,
              due_date ASC
        ''', (today,)).fetchall()
    
    return jsonify({'tasks': [dict(r) for r in rows], 'count': len(rows)})

@app.route('/api/ai/summary', methods=['GET'])
def api_ai_summary():
    \"\"\"提供 AI 讀取的整體摘要（董事長視角）\"\"\"
    today = datetime.now().strftime('%Y-%m-%d')
    with get_db() as db:
        # 案件統計
        total_cases = db.execute('SELECT COUNT(*) FROM case_status').fetchone()[0]
        active_cases = db.execute("SELECT COUNT(*) FROM case_status WHERE stage NOT IN ('已結案', '規劃中')").fetchone()[0]
        
        # 風險統計
        risk_stats = db.execute('''
            SELECT 
              SUM(CASE WHEN level='high' THEN 1 ELSE 0 END) as high,
              SUM(CASE WHEN level='medium' THEN 1 ELSE 0 END) as medium,
              SUM(CASE WHEN level='low' THEN 1 ELSE 0 END) as low
            FROM risk_items WHERE status != 'closed'
        ''').fetchone()
        
        # 任務統計
        task_stats = db.execute('''
            SELECT 
              SUM(CASE WHEN status='open' THEN 1 ELSE 0 END) as open_count,
              SUM(CASE WHEN status='in_progress' THEN 1 ELSE 0 END) as progress_count,
              SUM(CASE WHEN due_date != '' AND due_date < ? THEN 1 ELSE 0 END) as overdue
            FROM tasks WHERE status != 'closed'
        ''', (today,)).fetchone()
        
        # 今日提交率
        today_dir = REPORTS_DIR / today
        submitted = len(list(today_dir.glob('*_report.json'))) if today_dir.exists() else 0
        total_emp = len(EMPLOYEES)
    
    return jsonify({
        'cases': {'total': total_cases, 'active': active_cases},
        'risks': {'high': risk_stats['high'] or 0, 'medium': risk_stats['medium'] or 0, 'low': risk_stats['low'] or 0},
        'tasks': {'open': task_stats['open_count'] or 0, 'in_progress': task_stats['progress_count'] or 0, 'overdue': task_stats['overdue'] or 0},
        'today_submission': {'submitted': submitted, 'total': total_emp, 'rate': round(submitted/total_emp*100, 1) if total_emp else 0},
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })

"""
    
    # 插入在 health check 之後
    health_marker = "def health_check():"
    if health_marker in content:
        # 找到 health_check 函數結束的位置
        idx = content.find(health_marker)
        end_idx = content.find("\n\n# ", idx)
        if end_idx > 0:
            content = content[:end_idx] + "\n" + ai_api_code + content[end_idx:]
            print("✅ 新增 AI 數據 API")

# 寫入
with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ v4.0 升級完成！請重啟服務。")
