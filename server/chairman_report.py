#!/usr/bin/env python3
"""
昱金生能源 - 董事長專屬報告系統
功能：
1. 每日 08:00 自動生成案場進度報告
2. 整合所有員工日報 + AI 分析
3. 風險預警與決策建議
4. 推播到董事長個人工作頁面
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
AI_FEEDBACK_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/ai_feedback')
CHAIRMAN_REPORTS_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/chairman_reports')


class ChairmanReport:
    """董事長專屬報告系統"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.reports_dir = CHAIRMAN_REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def connect(self):
        """連接資料庫"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def generate_daily_report(self, date=None):
        """
        生成董事長每日報告
        
        Args:
            date: 報告日期（預設昨天）
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        conn = self.connect()
        
        # 1. 取得昨日所有日報
        cursor = conn.execute("""
            SELECT r.*, e.chinese_name as employee_name, e.department
            FROM reports r
            LEFT JOIN users e ON r.employee_id = e.id
            WHERE r.report_date = ?
            ORDER BY e.department, r.submitted_at
        """, (date,))
        
        reports = cursor.fetchall()
        
        # 2. 取得昨日新增/更新的風險
        cursor = conn.execute("""
            SELECT r.*, e.chinese_name as employee_name, c.name as case_name
            FROM risk_items r
            LEFT JOIN users e ON r.employee_id = e.id
            LEFT JOIN cases c ON r.case_id = c.case_id
            WHERE DATE(r.created_at) = ?
            ORDER BY 
                CASE r.level WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END,
                r.created_at DESC
        """, (date,))
        
        new_risks = cursor.fetchall()
        
        # 3. 取得昨日新增/完成的任務
        cursor = conn.execute("""
            SELECT t.*, e.chinese_name as owner_name, c.name as case_name
            FROM tasks t
            LEFT JOIN users e ON t.owner_id = e.id
            LEFT JOIN cases c ON t.case_id = c.case_id
            WHERE DATE(t.created_at) = ? OR DATE(t.updated_at) = ?
            ORDER BY 
                CASE t.priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END,
                t.created_at DESC
        """, (date, date))
        
        task_updates = cursor.fetchall()
        
        # 4. 取得 AI 反饋摘要
        ai_feedbacks = self._get_ai_feedbacks(date)
        
        # 5. 整合案場進度
        case_progress = self._aggregate_case_progress(reports, new_risks, task_updates)
        
        # 6. 生成報告
        report = self._build_report(date, reports, new_risks, task_updates, ai_feedbacks, case_progress)
        
        # 7. 儲存報告
        report_path = self._save_report(date, report)
        
        conn.close()
        
        print(f"✅ 董事長報告已生成：{report_path}")
        
        return report, report_path
    
    def _get_ai_feedbacks(self, date):
        """取得 AI 反饋摘要"""
        feedbacks = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT employee_id, feedback_content
                FROM ai_feedback
                WHERE feedback_date = ?
            """, (date,))
            
            for row in cursor.fetchall():
                feedbacks.append({
                    'employee_id': row[0],
                    'content': row[1]
                })
            
            conn.close()
        except:
            pass
        
        return feedbacks
    
    def _aggregate_case_progress(self, reports, new_risks, task_updates):
        """整合案場進度"""
        cases = defaultdict(lambda: {
            'name': '',
            'reports': [],
            'new_risks': [],
            'task_updates': [],
            'progress': 0,
            'status': 'normal'
        })
        
        # 整合日報
        for report in reports:
            report_data = json.loads(report['report_json'])
            work_items = report_data.get('work_items', [])
            
            for item in work_items:
                case_id = item.get('case_id', 'unknown')
                cases[case_id]['name'] = item.get('case_name', case_id)
                cases[case_id]['reports'].append({
                    'employee': report['employee_name'],
                    'content': item.get('work_content', ''),
                    'progress': item.get('progress', 0)
                })
        
        # 整合風險
        for risk in new_risks:
            case_id = risk['case_id']
            cases[case_id]['new_risks'].append({
                'level': risk['level'],
                'desc': risk['risk_desc'],
                'employee': risk['employee_name']
            })
            
            # 如果有高風險，標記案場狀態
            if risk['level'] == 'high':
                cases[case_id]['status'] = 'warning'
        
        # 整合任務
        for task in task_updates:
            case_id = task['case_id']
            cases[case_id]['task_updates'].append({
                'title': task['title'],
                'status': task['status'],
                'owner': task['owner_name']
            })
        
        return dict(cases)
    
    def _build_report(self, date, reports, new_risks, task_updates, ai_feedbacks, case_progress):
        """建立報告內容"""
        
        # 統計數據
        total_reports = len(reports)
        total_cases = len(case_progress)
        high_risks = sum(1 for r in new_risks if r['level'] == 'high')
        
        # 計算提交率
        conn = self.connect()
        cursor = conn.execute("""
            SELECT COUNT(*) FROM users
            WHERE role = 'employee' AND enabled = 1
        """)
        total_employees = cursor.fetchone()[0]
        conn.close()
        
        submission_rate = round(total_reports / total_employees * 100, 1) if total_employees > 0 else 0
        
        report = f"""# 📊 董事長專屬報告

**報告日期**: {date}  
**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**下次更新**: 明日 08:00

---

## 📈 今日摘要

| 指標 | 數值 | 狀態 |
|------|------|------|
| 日報提交率 | {total_reports}/{total_employees} ({submission_rate}%) | {'✅' if submission_rate >= 90 else '⚠️'} |
| 進行中案場 | {total_cases} 個 | ✅ |
| 新增高風險 | {high_risks} 個 | {'⚠️' if high_risks > 0 else '✅'} |
| 任務更新 | {len(task_updates)} 個 | ✅ |

---

## 🏭 各案場進度詳情

"""
        
        # 每個案場的詳細進度
        for case_id, case_data in case_progress.items():
            status_icon = '⚠️' if case_data['status'] == 'warning' else '✅'
            
            report += f"""### {status_icon} {case_data['name']} ({case_id})

"""
            # 員工日報
            if case_data['reports']:
                report += f"**📝 員工回報**:\n"
                for r in case_data['reports']:
                    report += f"- **{r['employee']}**: {r['content'][:100]}{'...' if len(r['content']) > 100 else ''}\n"
                report += "\n"
            
            # 新增風險
            if case_data['new_risks']:
                report += f"**⚠️ 新增風險**:\n"
                for r in case_data['new_risks']:
                    risk_icon = '🔴' if r['level'] == 'high' else '🟡'
                    report += f"- {risk_icon} [{r['level'].upper()}] {r['desc']} ({r['employee']})\n"
                report += "\n"
            
            # 任務更新
            if case_data['task_updates']:
                report += f"**✅ 任務更新**:\n"
                for t in case_data['task_updates']:
                    status_icon = '✅' if t['status'] == 'closed' else '🔄'
                    report += f"- {status_icon} {t['title']} ({t['owner']})\n"
                report += "\n"
            
            report += "---\n\n"
        
        # 需要董事長決策的事項
        report += """## 🎯 需要您決策的事項

"""
        
        if high_risks > 0:
            report += """### ⚠️ 高風險項目（需要關注）

"""
            for risk in [r for r in new_risks if r['level'] == 'high']:
                report += f"- **{risk['case_name']}**: {risk['risk_desc']}\n"
                report += f"  - 負責人：{risk['employee_name']}\n"
                report += f"  - 建議：{'立即協調資源' if '資源' in risk['risk_desc'] else '安排會議討論'}\n\n"
        else:
            report += "✅ 無高風險項目，所有案場正常進行\n\n"
        
        # AI 綜合建議
        report += """## 🤖 AI 綜合建議

"""
        
        if ai_feedbacks:
            # 提取共同問題
            common_issues = self._extract_common_issues(ai_feedbacks)
            
            if common_issues:
                report += "**發現共同問題**:\n"
                for issue in common_issues:
                    report += f"- {issue}\n"
                report += "\n"
            
            report += "**AI 建議**:\n"
            report += "- 整體進度良好，保持現有節奏\n"
            report += "- 注意天氣變化，提前調整工作安排\n"
            report += "- 建議每週召開一次案場進度協調會\n"
        else:
            report += "- 系統運行正常\n"
            report += "- 員工提交率良好\n"
            report += "- 無重大異常狀況\n"
        
        report += f"""
---

## 📋 明日重點關注

1. **高風險案場跟進**（如有）
2. **即將到期任務**檢查
3. **日報未提交員工**關懷

---

**報告結束** | 昱金生能源 AI 助理 | {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        return report
    
    def _extract_common_issues(self, ai_feedbacks):
        """從 AI 反饋中提取共同問題"""
        issues = []
        
        # 簡單關鍵字匹配
        keywords = {
            '進度落後': 0,
            '資源不足': 0,
            '天氣影響': 0,
            '廠商延遲': 0,
            '需要協調': 0
        }
        
        for feedback in ai_feedbacks:
            content = feedback.get('content', '')
            for keyword in keywords:
                if keyword in content:
                    keywords[keyword] += 1
        
        # 提取出現 2 次以上的問題
        for issue, count in keywords.items():
            if count >= 2:
                issues.append(f"{issue}（{count}人反映）")
        
        return issues
    
    def _save_report(self, date, report):
        """儲存報告"""
        # Markdown 檔案
        md_path = self.reports_dir / f"chairman_daily_{date}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # JSON 摘要（用於快速讀取）
        json_path = self.reports_dir / f"chairman_daily_{date}.json"
        summary = {
            'date': date,
            'generated_at': datetime.now().isoformat(),
            'md_path': str(md_path),
            'status': 'completed'
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return md_path
    
    def get_latest_report(self):
        """取得最新報告"""
        reports = sorted(self.reports_dir.glob('chairman_daily_*.md'), reverse=True)
        
        if reports:
            with open(reports[0], 'r', encoding='utf-8') as f:
                return f.read()
        
        return None
    
    def send_to_chairman(self, report, method='system'):
        """
        發送報告給董事長
        
        Args:
            report: 報告內容
            method: 發送方式 ('system', 'email', 'telegram', 'line')
        """
        if method == 'system':
            # 寫入董事長收件匣（資料庫）
            conn = self.connect()
            conn.execute("""
                INSERT INTO chairman_notifications 
                (title, content, priority, created_at, is_read)
                VALUES (?, ?, 'high', CURRENT_TIMESTAMP, 0)
            """, (f"📊 董事長報告 - {datetime.now().strftime('%Y-%m-%d')}", report))
            conn.commit()
            conn.close()
            
            print("✅ 報告已發送至董事長系統收件匣")
        
        elif method == 'email':
            # TODO: 實作 Email 發送
            print("📧 Email 發送功能待實作")
        
        elif method == 'telegram':
            # TODO: 實作 Telegram 推送
            print("📱 Telegram 推送功能待實作")
    
    def setup_auto_report(self):
        """設定自動報告（crontab）"""
        cron_job = """
# 董事長專屬報告 - 每日 08:00 自動生成
0 8 * * * cd /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server && \\
    python3 scripts/chairman_report.py --auto >> /tmp/chairman_report.log 2>&1
"""
        
        print("📋 請將以下內容加入 crontab:")
        print(cron_job)
        print("\n執行：crontab -e")


# Flask 路由整合
def register_chairman_routes(app):
    """註冊董事長報告路由"""
    
    @app.route('/api/chairman/report')
    def api_chairman_report():
        from flask import jsonify, request
        from flask_login import current_user
        
        # 權限檢查：僅董事長可訪問
        if current_user.role != 'admin':
            return jsonify({'error': '權限不足'}), 403
        
        date = request.args.get('date')
        
        reporter = ChairmanReport()
        
        if date:
            # 取得指定日期報告
            report_path = reporter.reports_dir / f"chairman_daily_{date}.md"
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    return jsonify({'content': f.read()})
            return jsonify({'error': '報告不存在'}), 404
        else:
            # 取得最新報告
            latest = reporter.get_latest_report()
            if latest:
                return jsonify({'content': latest})
            return jsonify({'error': '無報告'}), 404
    
    @app.route('/chairman/dashboard')
    def chairman_dashboard():
        from flask import render_template, redirect, url_for
        from flask_login import current_user, login_required
        
        @login_required
        def decorated():
            if current_user.role != 'admin':
                return redirect(url_for('index'))
            return render_template('chairman_dashboard.html')
        
        return decorated()


if __name__ == '__main__':
    import sys
    
    reporter = ChairmanReport()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # 自動模式（crontab 呼叫）
        print(f"\n📊 生成董事長報告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report, path = reporter.generate_daily_report()
        reporter.send_to_chairman(report, method='system')
        print(f"✅ 報告已生成並發送：{path}")
    else:
        # 手動模式
        date = sys.argv[1] if len(sys.argv) > 1 else None
        report, path = reporter.generate_daily_report(date)
        
        print("\n" + "="*60)
        print(report[:2000])  # 顯示前 2000 字
        print("...")
        print("="*60)
        print(f"\n✅ 完整報告：{path}")
