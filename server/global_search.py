#!/usr/bin/env python3
"""
昱金生能源 - 全域搜尋系統
功能：
1. 跨表搜尋（日報、案場、風險、任務、郵件）
2. 全文檢索
3. 關鍵字高亮
4. 搜尋建議
5. 搜尋歷史
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
EMAIL_ANALYSIS_DB = DB_PATH


class GlobalSearch:
    """全域搜尋引擎"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.search_history = []
    
    def connect(self):
        """連接資料庫"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def search(self, query, filters=None, limit=50):
        """
        全域搜尋
        
        Args:
            query: 搜尋關鍵字
            filters: 篩選條件 {'type': 'reports', 'date_from': '2026-01-01', ...}
            limit: 結果數量限制
        
        Returns:
            搜尋結果（分頁）
        """
        if not query or len(query) < 2:
            return {'error': '搜尋關鍵字至少 2 個字元', 'results': []}
        
        results = {
            'query': query,
            'total': 0,
            'by_type': defaultdict(int),
            'results': [],
            'suggestions': self._get_suggestions(query)
        }
        
        # 搜尋日報
        if not filters or filters.get('type') in [None, 'reports']:
            report_results = self._search_reports(query, limit)
            results['results'].extend(report_results)
            results['by_type']['reports'] = len(report_results)
            results['total'] += len(report_results)
        
        # 搜尋案場
        if not filters or filters.get('type') in [None, 'cases']:
            case_results = self._search_cases(query, limit)
            results['results'].extend(case_results)
            results['by_type']['cases'] = len(case_results)
            results['total'] += len(case_results)
        
        # 搜尋風險
        if not filters or filters.get('type') in [None, 'risks']:
            risk_results = self._search_risks(query, limit)
            results['results'].extend(risk_results)
            results['by_type']['risks'] = len(risk_results)
            results['total'] += len(risk_results)
        
        # 搜尋任務
        if not filters or filters.get('type') in [None, 'tasks']:
            task_results = self._search_tasks(query, limit)
            results['results'].extend(task_results)
            results['by_type']['tasks'] = len(task_results)
            results['total'] += len(task_results)
        
        # 搜尋郵件分析
        if not filters or filters.get('type') in [None, 'emails']:
            email_results = self._search_emails(query, limit)
            results['results'].extend(email_results)
            results['by_type']['emails'] = len(email_results)
            results['total'] += len(email_results)
        
        # 記錄搜尋歷史
        self._save_search_history(query, results['total'])
        
        # 排序（依相關性）
        results['results'].sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        return results
    
    def _search_reports(self, query, limit):
        """搜尋日報"""
        conn = self.connect()
        
        # 搜尋日報內容
        cursor = conn.execute("""
            SELECT r.*, e.chinese_name as employee_name
            FROM reports r
            LEFT JOIN users e ON r.employee_id = e.id
            WHERE r.report_json LIKE ?
               OR r.report_date LIKE ?
            ORDER BY r.submitted_at DESC
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            report_data = dict(row)
            
            # 提取關鍵字
            highlights = self._highlight_matches(report_data.get('report_json', ''), query)
            
            results.append({
                'type': 'report',
                'id': report_data['report_key'],
                'title': f"{report_data['employee_name']} - {report_data['report_date']} 日報",
                'date': report_data['report_date'],
                'employee': report_data['employee_name'],
                'snippet': highlights[:200],
                'relevance': self._calculate_relevance(report_data.get('report_json', ''), query),
                'url': f"/history?date={report_data['report_date']}&employee={report_data['employee_id']}"
            })
        
        conn.close()
        return results
    
    def _search_cases(self, query, limit):
        """搜尋案場"""
        conn = self.connect()
        
        cursor = conn.execute("""
            SELECT * FROM cases
            WHERE name LIKE ?
               OR case_id LIKE ?
               OR type LIKE ?
            ORDER BY name
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            case_data = dict(row)
            
            results.append({
                'type': 'case',
                'id': case_data['case_id'],
                'title': f"🏭 {case_data['name']}",
                'date': case_data.get('created_at', ''),
                'snippet': f"案場類型：{case_data.get('type', '未分類')}",
                'relevance': 10,
                'url': f"/cases?case_id={case_data['case_id']}"
            })
        
        conn.close()
        return results
    
    def _search_risks(self, query, limit):
        """搜尋風險項目"""
        conn = self.connect()
        
        cursor = conn.execute("""
            SELECT r.*, e.chinese_name as employee_name, c.name as case_name
            FROM risk_items r
            LEFT JOIN users e ON r.employee_id = e.id
            LEFT JOIN cases c ON r.case_id = c.case_id
            WHERE r.risk_desc LIKE ?
               OR r.risk_impact LIKE ?
               OR r.need_help LIKE ?
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            risk_data = dict(row)
            
            highlights = self._highlight_matches(risk_data.get('risk_desc', ''), query)
            
            results.append({
                'type': 'risk',
                'id': risk_data['id'],
                'title': f"⚠️ {risk_data.get('case_name', '未知案場')} - 風險項目",
                'date': risk_data.get('created_at', ''),
                'employee': risk_data.get('employee_name', ''),
                'snippet': highlights[:200],
                'status': risk_data.get('status', 'open'),
                'level': risk_data.get('level', 'medium'),
                'relevance': self._calculate_relevance(risk_data.get('risk_desc', ''), query),
                'url': f"/risks?risk_id={risk_data['id']}"
            })
        
        conn.close()
        return results
    
    def _search_tasks(self, query, limit):
        """搜尋任務"""
        conn = self.connect()
        
        cursor = conn.execute("""
            SELECT t.*, e.chinese_name as owner_name, c.name as case_name
            FROM tasks t
            LEFT JOIN users e ON t.owner_id = e.id
            LEFT JOIN cases c ON t.case_id = c.case_id
            WHERE t.title LIKE ?
               OR t.description LIKE ?
            ORDER BY t.created_at DESC
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            task_data = dict(row)
            
            highlights = self._highlight_matches(task_data.get('description', ''), query)
            
            results.append({
                'type': 'task',
                'id': task_data['id'],
                'title': f"✅ {task_data.get('case_name', '未知案場')} - 任務",
                'date': task_data.get('created_at', ''),
                'owner': task_data.get('owner_name', ''),
                'snippet': highlights[:200],
                'status': task_data.get('status', 'open'),
                'priority': task_data.get('priority', 'medium'),
                'relevance': self._calculate_relevance(task_data.get('task_desc', ''), query),
                'url': f"/tasks?task_id={task_data['id']}"
            })
        
        conn.close()
        return results
    
    def _search_emails(self, query, limit):
        """搜尋郵件分析"""
        conn = self.connect()
        
        try:
            cursor = conn.execute("""
                SELECT * FROM email_analysis
                WHERE subject LIKE ?
                   OR summary LIKE ?
                ORDER BY email_date DESC
                LIMIT ?
            """, (f'%{query}%', f'%{query}%', limit))
            
            results = []
            for row in cursor.fetchall():
                email_data = dict(row)
                
                highlights = self._highlight_matches(email_data.get('summary', ''), query)
                
                results.append({
                    'type': 'email',
                    'id': email_data['id'],
                    'title': f"📧 {email_data.get('subject', '無主旨')}",
                    'date': email_data.get('email_date', ''),
                    'sender': email_data.get('sender', ''),
                    'snippet': highlights[:200],
                    'event_type': email_data.get('event_type', 'general'),
                    'relevance': self._calculate_relevance(email_data.get('summary', ''), query),
                    'url': f"/email-analysis?id={email_data['id']}"
                })
            
            return results
            
        except sqlite3.OperationalError:
            # email_analysis 表可能不存在
            return []
        finally:
            conn.close()
    
    def _highlight_matches(self, text, query):
        """高亮匹配關鍵字"""
        if not text:
            return ''
        
        # 忽略大小寫替換
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        highlighted = pattern.sub(r'<mark>\g<0></mark>', text)
        
        return highlighted
    
    def _calculate_relevance(self, text, query):
        """計算相關性分數"""
        if not text:
            return 0
        
        text_lower = text.lower()
        query_lower = query.lower()
        
        # 完全匹配
        if query_lower in text_lower:
            return 100
        
        # 部分匹配
        score = 0
        words = query_lower.split()
        for word in words:
            if word in text_lower:
                score += 10
        
        return min(score, 99)
    
    def _get_suggestions(self, query):
        """取得搜尋建議"""
        suggestions = []
        
        conn = self.connect()
        
        # 案場名稱建議
        cursor = conn.execute("""
            SELECT name FROM cases
            WHERE name LIKE ?
            LIMIT 5
        """, (f'%{query}%',))
        
        for row in cursor.fetchall():
            suggestions.append({
                'type': 'case',
                'text': row[0],
                'icon': '🏭'
            })
        
        # 員工姓名建議
        cursor = conn.execute("""
            SELECT chinese_name FROM users
            WHERE chinese_name LIKE ?
            LIMIT 5
        """, (f'%{query}%',))
        
        for row in cursor.fetchall():
            suggestions.append({
                'type': 'employee',
                'text': row[0],
                'icon': '👤'
            })
        
        conn.close()
        
        return suggestions
    
    def _save_search_history(self, query, result_count):
        """記錄搜尋歷史"""
        self.search_history.append({
            'query': query,
            'time': datetime.now().isoformat(),
            'results': result_count
        })
        
        # 限制歷史記錄數量
        if len(self.search_history) > 100:
            self.search_history = self.search_history[-100:]
    
    def get_popular_searches(self, limit=10):
        """取得熱門搜尋"""
        from collections import Counter
        
        queries = [item['query'] for item in self.search_history]
        counter = Counter(queries)
        
        return counter.most_common(limit)
    
    def optimize_search(self):
        """優化搜尋效能（建立索引）"""
        conn = self.connect()
        
        # 為常用搜尋欄位建立索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_reports_search ON reports(report_json)",
            "CREATE INDEX IF NOT EXISTS idx_risks_search ON risk_items(risk_desc, risk_impact)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_search ON tasks(title, description)",
            "CREATE INDEX IF NOT EXISTS idx_cases_search ON cases(name, type)",
        ]
        
        for idx_sql in indexes:
            try:
                conn.execute(idx_sql)
            except Exception as e:
                print(f"⚠️ 建立索引失敗：{e}")
        
        conn.commit()
        conn.close()
        
        print("✅ 搜尋索引已建立")


# Flask 路由整合
def register_search_routes(app):
    """註冊搜尋路由到 Flask app"""
    
    @app.route('/api/search')
    def api_search():
        from flask import request, jsonify
        
        query = request.args.get('q', '')
        search_type = request.args.get('type', None)
        limit = int(request.args.get('limit', 50))
        
        searcher = GlobalSearch()
        
        filters = {}
        if search_type:
            filters['type'] = search_type
        
        results = searcher.search(query, filters, limit)
        
        return jsonify(results)
    
    @app.route('/api/search/suggestions')
    def api_search_suggestions():
        from flask import request, jsonify
        
        query = request.args.get('q', '')
        
        searcher = GlobalSearch()
        suggestions = searcher._get_suggestions(query)
        
        return jsonify({'suggestions': suggestions})
    
    @app.route('/search')
    def search_page():
        from flask import render_template, request
        
        query = request.args.get('q', '')
        search_type = request.args.get('type', '')
        
        return render_template('search.html', query=query, search_type=search_type)


if __name__ == '__main__':
    import sys
    
    searcher = GlobalSearch()
    
    # 優化搜尋
    searcher.optimize_search()
    
    # 測試搜尋
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        print(f"\n🔍 搜尋：{query}\n")
        
        results = searcher.search(query)
        
        print(f"📊 總結果：{results['total']} 筆\n")
        
        print(f"📋 分類統計:")
        for type_name, count in results['by_type'].items():
            print(f"  {type_name}: {count} 筆")
        
        print(f"\n📌 搜尋建議:")
        for sug in results['suggestions']:
            print(f"  {sug['icon']} {sug['text']}")
        
        print(f"\n🎯 前 10 筆結果:")
        for i, item in enumerate(results['results'][:10], 1):
            print(f"{i}. [{item['type']}] {item['title']}")
            print(f"   {item['snippet'][:100]}...")
            print()
    else:
        print("用法：python3 global_search.py [搜尋關鍵字]")
        print("\n範例:")
        print("  python3 global_search.py 仁豐國小")
        print("  python3 global_search.py 楊宗衛")
        print("  python3 global_search.py 併聯")
