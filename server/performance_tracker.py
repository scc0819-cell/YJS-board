#!/usr/bin/env python3
"""
昱金生能源 - 績效管考系統
功能：
1. 日報提交率統計
2. 任務完成率分析
3. 風險處理效率
4. AI 生成績效報告
5. 個人/團隊績效比較
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
PERFORMANCE_REPORTS_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/performance_reports')


class PerformanceTracker:
    """績效追蹤系統"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.reports_dir = PERFORMANCE_REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def connect(self):
        """連接資料庫"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_employee_stats(self, employee_id, start_date=None, end_date=None):
        """取得員工績效統計"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        conn = self.connect()
        
        stats = {
            'employee_id': employee_id,
            'period': {'start': start_date, 'end': end_date},
            'reports': self._get_report_stats(conn, employee_id, start_date, end_date),
            'tasks': self._get_task_stats(conn, employee_id, start_date, end_date),
            'risks': self._get_risk_stats(conn, employee_id, start_date, end_date),
            'overall_score': 0
        }
        
        # 計算總分
        stats['overall_score'] = self._calculate_overall_score(stats)
        
        conn.close()
        
        return stats
    
    def _get_report_stats(self, conn, employee_id, start_date, end_date):
        """取得日報統計"""
        # 計算期間內應提交天數（扣除假日）
        import sys
        sys.path.insert(0, '/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/scripts')
        from taiwan_calendar import TaiwanCalendar
        calendar = TaiwanCalendar()
        workdays = len(calendar.get_workdays_in_range(start_date, end_date))
        
        # 實際提交天數
        cursor = conn.execute("""
            SELECT COUNT(DISTINCT report_date) as submitted_days
            FROM reports
            WHERE employee_id = ?
              AND report_date BETWEEN ? AND ?
        """, (employee_id, start_date, end_date))
        
        submitted_days = cursor.fetchone()['submitted_days']
        
        # 提交率
        submission_rate = round(submitted_days / workdays * 100, 1) if workdays > 0 else 0
        
        # 平均提交時間
        cursor = conn.execute("""
            SELECT AVG(julianday(submitted_at) - julianday(report_date)) as avg_delay
            FROM reports
            WHERE employee_id = ?
              AND report_date BETWEEN ? AND ?
        """, (employee_id, start_date, end_date))
        
        avg_delay = cursor.fetchone()['avg_delay'] or 0
        
        return {
            'workdays': workdays,
            'submitted_days': submitted_days,
            'submission_rate': submission_rate,
            'avg_delay_days': round(avg_delay, 2),
            'score': min(submission_rate, 100)  # 提交率分數
        }
    
    def _get_task_stats(self, conn, employee_id, start_date, end_date):
        """取得任務統計"""
        # 總任務數
        cursor = conn.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as completed
            FROM tasks
            WHERE owner_id = ?
              AND created_at BETWEEN ? AND ?
        """, (employee_id, start_date, end_date))
        
        row = cursor.fetchone()
        total = row['total'] or 0
        completed = row['completed'] or 0
        
        # 完成率
        completion_rate = round(completed / total * 100, 1) if total > 0 else 0
        
        # 平均完成天數
        cursor = conn.execute("""
            SELECT AVG(julianday(closed_at) - julianday(created_at)) as avg_days
            FROM tasks
            WHERE owner_id = ?
              AND status = 'closed'
              AND created_at BETWEEN ? AND ?
        """, (employee_id, start_date, end_date))
        
        avg_days = cursor.fetchone()['avg_days'] or 0
        
        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': completion_rate,
            'avg_completion_days': round(avg_days, 2),
            'score': min(completion_rate, 100)  # 完成率分數
        }
    
    def _get_risk_stats(self, conn, employee_id, start_date, end_date):
        """取得風險統計"""
        # 總風險數
        cursor = conn.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as resolved
            FROM risk_items
            WHERE employee_id = ?
              AND created_at BETWEEN ? AND ?
        """, (employee_id, start_date, end_date))
        
        row = cursor.fetchone()
        total = row['total'] or 0
        resolved = row['resolved'] or 0
        
        # 解決率
        resolution_rate = round(resolved / total * 100, 1) if total > 0 else 0
        
        # 高風險數量
        cursor = conn.execute("""
            SELECT COUNT(*) as high_risk_count
            FROM risk_items
            WHERE employee_id = ?
              AND level = 'high'
              AND status != 'closed'
              AND created_at BETWEEN ? AND ?
        """, (employee_id, start_date, end_date))
        
        high_risk = cursor.fetchone()['high_risk_count'] or 0
        
        return {
            'total_risks': total,
            'resolved_risks': resolved,
            'resolution_rate': resolution_rate,
            'active_high_risks': high_risk,
            'score': min(resolution_rate, 100) if high_risk == 0 else max(0, resolution_rate - high_risk * 10)
        }
    
    def _calculate_overall_score(self, stats):
        """計算總分"""
        report_score = stats['reports']['score']
        task_score = stats['tasks']['score']
        risk_score = stats['risks']['score']
        
        # 權重：日報 40%、任務 40%、風險 20%
        overall = (
            report_score * 0.4 +
            task_score * 0.4 +
            risk_score * 0.2
        )
        
        return round(overall, 1)
    
    def get_team_performance(self, start_date=None, end_date=None):
        """取得團隊績效"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        conn = self.connect()
        
        # 取得所有員工
        cursor = conn.execute("""
            SELECT id, chinese_name, department, role
            FROM users
            WHERE role = 'employee' AND enabled = 1
        """)
        
        employees = cursor.fetchall()
        
        team_stats = {
            'period': {'start': start_date, 'end': end_date},
            'total_employees': len(list(employees)),
            'employees': [],
            'averages': {},
            'rankings': {}
        }
        
        # 計算每個員工的績效
        all_scores = []
        for emp in employees:
            emp_stats = self.get_employee_stats(emp['id'], start_date, end_date)
            emp_stats['name'] = emp['chinese_name']
            emp_stats['department'] = emp['department']
            team_stats['employees'].append(emp_stats)
            all_scores.append(emp_stats['overall_score'])
        
        # 計算平均
        if all_scores:
            team_stats['averages'] = {
                'overall_score': round(sum(all_scores) / len(all_scores), 1),
                'submission_rate': round(sum(e['reports']['submission_rate'] for e in team_stats['employees']) / len(team_stats['employees']), 1),
                'completion_rate': round(sum(e['tasks']['completion_rate'] for e in team_stats['employees']) / len(team_stats['employees']), 1),
                'resolution_rate': round(sum(e['risks']['resolution_rate'] for e in team_stats['employees']) / len(team_stats['employees']), 1)
            }
        
        # 排名
        sorted_employees = sorted(team_stats['employees'], key=lambda x: x['overall_score'], reverse=True)
        team_stats['rankings'] = {
            'top_performers': [e['name'] for e in sorted_employees[:3]],
            'needs_improvement': [e['name'] for e in sorted_employees[-3:]]
        }
        
        conn.close()
        
        return team_stats
    
    def generate_performance_report(self, employee_id=None, period='monthly'):
        """生成績效報告"""
        if period == 'monthly':
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        elif period == 'quarterly':
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        if employee_id:
            # 個人報告
            stats = self.get_employee_stats(employee_id, start_str, end_str)
            report = self._generate_individual_report(stats, period)
        else:
            # 團隊報告
            stats = self.get_team_performance(start_str, end_str)
            report = self._generate_team_report(stats, period)
        
        # 儲存報告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.reports_dir / f"performance_{timestamp}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 績效報告已儲存：{report_path}")
        
        return report, report_path
    
    def _generate_individual_report(self, stats, period):
        """生成個人績效報告"""
        report = f"""# 📊 個人績效報告

**員工**: {stats.get('name', stats['employee_id'])}  
**期間**: {stats['period']['start']} ~ {stats['period']['end']} ({period})  
**總分**: {stats['overall_score']}/100

---

## 📈 總評

"""
        # 根據分數給予評語
        score = stats['overall_score']
        if score >= 90:
            comment = "🌟 表現優異，繼續保持！"
        elif score >= 80:
            comment = "✅ 表現良好，仍有進步空間"
        elif score >= 70:
            comment = "📈 表現中等，需要加強"
        else:
            comment = "⚠️ 需要立即改進"
        
        report += f"**{comment}**\n\n"
        
        # 日報提交
        report += f"""## 📝 日報提交

- 應提交：{stats['reports']['workdays']} 天
- 已提交：{stats['reports']['submitted_days']} 天
- 提交率：**{stats['reports']['submission_rate']}%**
- 平均延遲：{stats['reports']['avg_delay_days']} 天

"""
        
        # 任務完成
        report += f"""## ✅ 任務執行

- 總任務：{stats['tasks']['total_tasks']} 個
- 已完成：{stats['tasks']['completed_tasks']} 個
- 完成率：**{stats['tasks']['completion_rate']}%**
- 平均完成天數：{stats['tasks']['avg_completion_days']} 天

"""
        
        # 風險處理
        report += f"""## ⚠️ 風險管理

- 總風險：{stats['risks']['total_risks']} 個
- 已解決：{stats['risks']['resolved_risks']} 個
- 解決率：**{stats['risks']['resolution_rate']}%**
- 進行中高風險：{stats['risks']['active_high_risks']} 個

"""
        
        # 改進建議
        report += """## 💡 改進建議

"""
        if stats['reports']['submission_rate'] < 90:
            report += "- 📝 提高日報提交率，養成每日記錄習慣\n"
        if stats['tasks']['completion_rate'] < 80:
            report += "- ✅ 加強任務執行力，優先處理重要任務\n"
        if stats['risks']['resolution_rate'] < 70:
            report += "- ⚠️ 積極處理風險項目，避免問題擴大\n"
        if stats['reports']['avg_delay_days'] > 1:
            report += "- ⏰ 減少日報延遲，當日事當日記\n"
        
        report += f"\n---\n\n**報告生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        
        return report
    
    def _generate_team_report(self, stats, period):
        """生成團隊績效報告"""
        report = f"""# 📊 團隊績效報告

**期間**: {stats['period']['start']} ~ {stats['period']['end']} ({period})  
**員工人數**: {stats['total_employees']} 人

---

## 📈 團隊平均

- 總平均分：{stats['averages'].get('overall_score', 0)}/100
- 平均日報提交率：{stats['averages'].get('submission_rate', 0)}%
- 平均任務完成率：{stats['averages'].get('completion_rate', 0)}%
- 平均風險解決率：{stats['averages'].get('resolution_rate', 0)}%

---

## 🏆 表現優異者

"""
        for i, name in enumerate(stats['rankings']['top_performers'], 1):
            medal = ['🥇', '🥈', '🥉'][i-1]
            report += f"{medal} {name}\n"
        
        report += f"""
## ⚠️ 需要加強者

"""
        for name in stats['rankings']['needs_improvement']:
            report += f"- {name}\n"
        
        report += f"""
## 📊 詳細排名

| 排名 | 姓名 | 部門 | 總分 | 日報率 | 任務率 | 風險率 |
|------|------|------|------|--------|--------|--------|
"""
        
        sorted_employees = sorted(stats['employees'], key=lambda x: x['overall_score'], reverse=True)
        for i, emp in enumerate(sorted_employees, 1):
            report += f"| {i} | {emp.get('name', 'N/A')} | {emp.get('department', 'N/A')} | {emp['overall_score']} | {emp['reports']['submission_rate']}% | {emp['tasks']['completion_rate']}% | {emp['risks']['resolution_rate']}% |\n"
        
        report += f"\n---\n\n**報告生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        
        return report


# Flask 路由整合
def register_performance_routes(app):
    """註冊績效路由到 Flask app"""
    
    @app.route('/api/performance/employee/<employee_id>')
    def api_employee_performance(employee_id):
        from flask import request, jsonify
        
        start = request.args.get('start')
        end = request.args.get('end')
        period = request.args.get('period', 'monthly')
        
        tracker = PerformanceTracker()
        stats = tracker.get_employee_stats(employee_id, start, end)
        
        return jsonify(stats)
    
    @app.route('/api/performance/team')
    def api_team_performance():
        from flask import request, jsonify
        
        start = request.args.get('start')
        end = request.args.get('end')
        
        tracker = PerformanceTracker()
        stats = tracker.get_team_performance(start, end)
        
        return jsonify(stats)
    
    @app.route('/api/performance/report')
    def api_performance_report():
        from flask import request, jsonify
        
        employee_id = request.args.get('employee_id')
        period = request.args.get('period', 'monthly')
        
        tracker = PerformanceTracker()
        report, path = tracker.generate_performance_report(employee_id, period)
        
        return jsonify({
            'report': report,
            'path': str(path)
        })


if __name__ == '__main__':
    import sys
    
    tracker = PerformanceTracker()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'team':
            # 團隊報告
            report, path = tracker.generate_performance_report(period='monthly')
            print(f"\n📊 團隊績效報告\n")
            print(report)
        else:
            # 個人報告
            employee_id = sys.argv[1]
            report, path = tracker.generate_performance_report(employee_id, period='monthly')
            print(f"\n📊 個人績效報告：{employee_id}\n")
            print(report)
    else:
        print("用法：python3 performance_tracker.py [employee_id|team]")
        print("\n範例:")
        print("  python3 performance_tracker.py yang_zong_wei")
        print("  python3 performance_tracker.py team")
