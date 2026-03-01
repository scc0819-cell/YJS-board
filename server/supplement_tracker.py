#!/usr/bin/env python3
"""
昱金生能源 - 補充請求追蹤系統
功能：
1. 追蹤發送給員工的補充請求
2. 記錄董事長判斷（需要/不需要）
3. 監控員工回覆狀態
4. 依過期天數提醒董事長
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
REQUESTS_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/supplement_requests')


class SupplementRequestTracker:
    """補充請求追蹤系統"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.requests_dir = REQUESTS_DIR
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """初始化資料庫表"""
        conn = sqlite3.connect(self.db_path)
        
        # 補充請求表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS supplement_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                case_id TEXT,
                question TEXT NOT NULL,
                source_email_subject TEXT,
                source_email_date TEXT,
                status TEXT DEFAULT 'pending',
                chairman_judgment TEXT,
                chairman_judgment_date TEXT,
                employee_response TEXT,
                employee_response_date TEXT,
                due_date TEXT,
                overdue_days INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 建立索引
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_requests_status
            ON supplement_requests(status, due_date)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_requests_employee
            ON supplement_requests(employee_id, status)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ 補充請求追蹤系統已初始化")
    
    def add_request(self, employee_id, question, case_id=None, 
                    source_email_subject=None, source_email_date=None,
                    due_date=None):
        """新增補充請求"""
        conn = sqlite3.connect(self.db_path)
        
        if due_date is None:
            due_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        
        conn.execute("""
            INSERT INTO supplement_requests 
            (employee_id, case_id, question, source_email_subject, 
             source_email_date, due_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (employee_id, case_id, question, source_email_subject,
              source_email_date, due_date))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 已新增補充請求：{employee_id} - {question[:50]}...")
    
    def update_chairman_judgment(self, request_id, judgment):
        """
        更新董事長判斷
        
        Args:
            request_id: 請求 ID
            judgment: 'needed' (需要) / 'not_needed' (不需要)
        """
        conn = sqlite3.connect(self.db_path)
        
        conn.execute("""
            UPDATE supplement_requests
            SET chairman_judgment = ?,
                chairman_judgment_date = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (judgment, request_id))
        
        conn.commit()
        conn.close()
        
        judgment_text = "需要" if judgment == 'needed' else "不需要"
        print(f"✅ 已更新董事長判斷：{judgment_text}")
    
    def update_employee_response(self, request_id, response):
        """更新員工回覆"""
        conn = sqlite3.connect(self.db_path)
        
        conn.execute("""
            UPDATE supplement_requests
            SET employee_response = ?,
                employee_response_date = CURRENT_TIMESTAMP,
                status = 'completed',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (response, request_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 已更新員工回覆")
    
    def check_overdue(self):
        """檢查逾期請求並生成提醒"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # 找出逾期且董事長判斷為「需要」的請求
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor = conn.execute("""
            SELECT *, 
                   julianday(?) - julianday(due_date) as overdue_days
            FROM supplement_requests
            WHERE due_date < ?
              AND chairman_judgment = 'needed'
              AND status != 'completed'
            ORDER BY overdue_days DESC
        """, (today, today))
        
        overdue_requests = cursor.fetchall()
        conn.close()
        
        if not overdue_requests:
            print("✅ 無逾期請求")
            return []
        
        # 生成提醒報告
        reminder = self._generate_overdue_reminder(overdue_requests)
        
        # 儲存提醒
        reminder_path = self.requests_dir / f"overdue_reminder_{today}.md"
        with open(reminder_path, 'w', encoding='utf-8') as f:
            f.write(reminder)
        
        print(f"\n⚠️ 發現 {len(overdue_requests)} 筆逾期請求")
        print(f"   提醒報告：{reminder_path}")
        
        return overdue_requests
    
    def _generate_overdue_reminder(self, overdue_requests):
        """生成逾期提醒"""
        reminder = f"""# ⚠️ 補充請求逾期提醒

**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

> 以下補充請求已逾期，員工尚未回覆。
> 這些項目經您判斷為**需要**，請協助要求員工提供。

---

## 📊 統計

- 總逾期筆數：{len(overdue_requests)}
- 最長逾期：{max(r['overdue_days'] for r in overdue_requests):.0f} 天
- 涉及員工：{len(set(r['employee_id'] for r in overdue_requests))} 人

---

## 📋 逾期清單

"""
        
        # 依員工分組
        by_employee = defaultdict(list)
        for req in overdue_requests:
            by_employee[req['employee_id']].append(req)
        
        for emp_id, requests in by_employee.items():
            reminder += f"### 👤 員工：{emp_id}\n\n"
            
            for req in requests:
                overdue_days = int(req['overdue_days'])
                urgency = '🔴' if overdue_days >= 7 else '🟡'
                
                reminder += f"{urgency} **逾期 {overdue_days} 天**\n"
                reminder += f"- **問題**: {req['question']}\n"
                reminder += f"- **案場**: {req['case_id'] or 'N/A'}\n"
                reminder += f"- **來源郵件**: {req['source_email_subject'] or 'N/A'}\n"
                reminder += f"- **期限**: {req['due_date']}\n"
                reminder += f"- **建議行動**: "
                
                if overdue_days >= 14:
                    reminder += "📞 立即電話聯繫\n"
                elif overdue_days >= 7:
                    reminder += "📧 發送催交通知\n"
                else:
                    reminder += "💬 系統內提醒\n"
                
                reminder += "\n---\n\n"
        
        reminder += """## 💡 建議行動

1. **立即處理**（逾期≥7 天）：
   - 電話聯繫員工
   - 了解未回覆原因
   - 確認是否需要協助

2. **發送催交通知**（逾期 3-6 天）：
   - 透過系統發送提醒
   - 副本通知主管

3. **持續追蹤**（逾期<3 天）：
   - 等待員工回覆
   - 適時提供協助

---

**下次檢查**: 明日 08:00
"""
        
        return reminder
    
    def get_pending_requests(self, employee_id=None):
        """取得待處理請求"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        if employee_id:
            cursor = conn.execute("""
                SELECT * FROM supplement_requests
                WHERE employee_id = ? AND status = 'pending'
                ORDER BY due_date
            """, (employee_id,))
        else:
            cursor = conn.execute("""
                SELECT * FROM supplement_requests
                WHERE status = 'pending'
                ORDER BY due_date
            """)
        
        requests = cursor.fetchall()
        conn.close()
        
        return [dict(req) for req in requests]
    
    def get_chairman_summary(self):
        """取得董事長摘要報告"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # 統計
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN chairman_judgment = 'needed' THEN 1 ELSE 0 END) as needed,
                SUM(CASE WHEN chairman_judgment = 'not_needed' THEN 1 ELSE 0 END) as not_needed,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN due_date < date('now') AND status != 'completed' THEN 1 ELSE 0 END) as overdue
            FROM supplement_requests
        """)
        
        stats = dict(cursor.fetchone())
        
        # 最近待判斷
        cursor = conn.execute("""
            SELECT * FROM supplement_requests
            WHERE chairman_judgment IS NULL
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        pending_judgment = cursor.fetchall()
        
        conn.close()
        
        return {
            'stats': stats,
            'pending_judgment': [dict(req) for req in pending_judgment]
        }
    
    def export_report(self):
        """匯出完整報告"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT * FROM supplement_requests
            ORDER BY created_at DESC
        """)
        
        requests = cursor.fetchall()
        conn.close()
        
        report_path = self.requests_dir / f"supplement_report_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 📊 補充請求完整報告\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            f.write(f"**總請求數**: {len(requests)}\n\n")
            
            f.write("## 📋 請求清單\n\n")
            
            for req in requests:
                status_icon = {
                    'pending': '⏳',
                    'completed': '✅',
                    'overdue': '🔴'
                }.get(req['status'], '⏳')
                
                f.write(f"{status_icon} **{req['question'][:80]}**\n")
                f.write(f"- 員工：{req['employee_id']}\n")
                f.write(f"- 案場：{req['case_id'] or 'N/A'}\n")
                f.write(f"- 狀態：{req['status']}\n")
                f.write(f"- 董事長判斷：{req['chairman_judgment'] or '待確認'}\n")
                f.write(f"- 員工回覆：{req['employee_response'] or '尚未回覆'}\n")
                f.write(f"- 期限：{req['due_date']}\n")
                f.write("\n---\n\n")
        
        print(f"✅ 報告已匯出：{report_path}")


# Flask 路由整合
def register_supplement_routes(app):
    """註冊補充請求路由"""
    
    @app.route('/api/supplement/requests')
    def api_get_requests():
        from flask import request, jsonify
        from flask_login import current_user, login_required
        
        @login_required
        def decorated():
            tracker = SupplementRequestTracker()
            
            employee_id = request.args.get('employee_id')
            requests = tracker.get_pending_requests(employee_id)
            
            return jsonify({'requests': requests})
        
        return decorated()
    
    @app.route('/api/supplement/judgment', methods=['POST'])
    def api_update_judgment():
        from flask import request, jsonify
        from flask_login import current_user, login_required
        
        @login_required
        def decorated():
            if current_user.role != 'admin':
                return jsonify({'error': '權限不足'}), 403
            
            data = request.json
            request_id = data.get('request_id')
            judgment = data.get('judgment')  # 'needed' or 'not_needed'
            
            if not request_id or judgment not in ['needed', 'not_needed']:
                return jsonify({'error': '參數錯誤'}), 400
            
            tracker = SupplementRequestTracker()
            tracker.update_chairman_judgment(request_id, judgment)
            
            return jsonify({'success': True})
        
        return decorated()
    
    @app.route('/api/supplement/summary')
    def api_summary():
        from flask import jsonify
        from flask_login import current_user, login_required
        
        @login_required
        def decorated():
            if current_user.role != 'admin':
                return jsonify({'error': '權限不足'}), 403
            
            tracker = SupplementRequestTracker()
            summary = tracker.get_chairman_summary()
            
            return jsonify(summary)
        
        return decorated()


if __name__ == '__main__':
    import sys
    
    tracker = SupplementRequestTracker()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'check':
            # 檢查逾期
            print("\n🔍 檢查逾期請求...\n")
            tracker.check_overdue()
        
        elif sys.argv[1] == 'report':
            # 匯出報告
            print("\n📊 匯出完整報告...\n")
            tracker.export_report()
        
        elif sys.argv[1] == 'summary':
            # 董事長摘要
            print("\n📋 董事長摘要報告\n")
            summary = tracker.get_chairman_summary()
            
            print(f"**總請求數**: {summary['stats']['total']}")
            print(f"**需要**: {summary['stats']['needed']}")
            print(f"**不需要**: {summary['stats']['not_needed']}")
            print(f"**已完成**: {summary['stats']['completed']}")
            print(f"**逾期**: {summary['stats']['overdue']}")
            
            if summary['pending_judgment']:
                print(f"\n⏳ 待您判斷 ({len(summary['pending_judgment'])} 筆):")
                for req in summary['pending_judgment']:
                    print(f"- {req['question'][:60]}...")
    else:
        print("用法：python3 supplement_tracker.py [check|report|summary]")
        print("\n範例:")
        print("  python3 supplement_tracker.py check")
        print("  python3 supplement_tracker.py summary")
        print("  python3 supplement_tracker.py report")
