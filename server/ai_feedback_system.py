#!/usr/bin/env python3
"""
昱金生能源 - AI 即時反饋系統
功能：員工上傳日報後半小時，AI 自動分析並給予建議

工作流程：
1. 監控新提交的日報
2. 等待 30 分鐘
3. 整合該員工的日報內容 + 案場進度 + 風險/任務狀態
4. AI 分析並生成建議
5. 推播給員工（系統通知 + Email/Telegram）

員工使用場景：
- 每天早上上班第一件事：打開系統查看 AI 建議
- AI 扮演「師傅」或「副駕駛」角色
- 給予工作指導、建議、下一步行動
- 提升效率、獲得成就感、明確方向
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
import time
import threading

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
USERS_JSON = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/users.json')
AI_FEEDBACK_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/ai_feedback')

# AI 反饋提示詞模板
AI_PROMPT_TEMPLATE = """
你是一位經驗豐富的太陽能光電工程顧問，擔任員工的「師傅」和「副駕駛」角色。

請根據以下資料，給予員工具體、實用、鼓勵性的工作建議：

## 員工資訊
- 姓名：{employee_name}
- 工號：{employee_code}
- 部門：{department}
- 職稱：{title}

## 今日日報內容
{report_content}

## 相關案場進度
{case_progress}

## 進行中風險
{risks}

## 進行中任務
{tasks}

## 分析要求

請提供以下建議：

### 🎯 今日工作亮點
- 表揚員工做得好的地方（具體、真誠）

### ⚠️ 需要注意的事項
- 潛在風險提醒
- 需要跟進的事項

### 💡 明日工作建議
- 具體的下一步行動
- 優先級建議
- 資源協調建議

### 📚 學習與成長
- 相關知識或技能建議
- 經驗分享

### 🔧 需要的支持
- 是否需要協調其他部門
- 是否需要上級協助

請用鼓勵、正向、專業的語氣，讓員工感受到支持而非壓力。
"""

class AIFeedbackSystem:
    """AI 即時反饋系統"""
    
    def __init__(self):
        self.check_interval = 300  # 每 5 分鐘檢查一次
        self.delay_minutes = 30    # 延遲 30 分鐘分析
        self.running = False
    
    def get_employee_info(self, employee_id: str) -> dict:
        """取得員工資訊"""
        if USERS_JSON.exists():
            with open(USERS_JSON, 'r', encoding='utf-8') as f:
                users = json.load(f)
            user = users.get(employee_id, {})
            return {
                'name': user.get('chinese_name', user.get('name', employee_id)),
                'employee_code': user.get('employee_code', employee_id),
                'department': user.get('department', '未分類'),
                'title': user.get('title', '員工')
            }
        return {'name': employee_id, 'employee_code': employee_id}
    
    def get_daily_report(self, employee_id: str, date: str) -> dict:
        """取得員工日報"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        report_key = f"{date}_{employee_id}"
        cursor = conn.execute("""
            SELECT * FROM reports WHERE report_key = ?
        """, (report_key,))
        
        report = cursor.fetchone()
        conn.close()
        
        if report:
            return {
                'work_items': json.loads(report['report_json']).get('work_items', []),
                'plan_items': json.loads(report['report_json']).get('plan_items', []),
                'raw': dict(report)
            }
        return None
    
    def get_case_progress(self, case_ids: list) -> list:
        """取得案場進度"""
        if not case_ids:
            return []
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        placeholders = ','.join('?' * len(case_ids))
        cursor = conn.execute(f"""
            SELECT c.*, 
                   (SELECT COUNT(*) FROM risk_items r WHERE r.case_id = c.case_id AND r.status != 'closed') as active_risks,
                   (SELECT COUNT(*) FROM tasks t WHERE t.case_id = c.case_id AND t.status != 'closed') as active_tasks
            FROM cases c
            WHERE c.case_id IN ({placeholders})
        """, case_ids)
        
        cases = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return cases
    
    def get_active_risks(self, employee_id: str) -> list:
        """取得員工相關的進行中風險"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT * FROM risk_items
            WHERE (owner_id = ? OR employee_id = ?) AND status != 'closed'
            ORDER BY 
                CASE WHEN due_date != '' AND due_date < date('now') THEN 0
                     WHEN due_date != '' THEN 1
                     ELSE 2 END,
                due_date ASC
            LIMIT 10
        """, (employee_id, employee_id))
        
        risks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return risks
    
    def get_active_tasks(self, employee_id: str) -> list:
        """取得員工相關的進行中任務"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT * FROM tasks
            WHERE owner_id = ? AND status != 'closed'
            ORDER BY 
                CASE WHEN due_date != '' AND due_date < date('now') THEN 0
                     WHEN due_date != '' THEN 1
                     ELSE 2 END,
                priority DESC, due_date ASC
            LIMIT 10
        """, (employee_id,))
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return tasks
    
    def generate_ai_feedback(self, employee_id: str, date: str) -> str:
        """生成 AI 反饋建議"""
        # 取得資料
        emp_info = self.get_employee_info(employee_id)
        report = self.get_daily_report(employee_id, date)
        
        if not report:
            return None
        
        # 提取案場 ID
        case_ids = list(set([
            item.get('case_id') 
            for item in report['work_items'] + report['plan_items']
            if item.get('case_id')
        ]))
        
        case_progress = self.get_case_progress(case_ids)
        risks = self.get_active_risks(employee_id)
        tasks = self.get_active_tasks(employee_id)
        
        # 格式化內容
        report_content = json.dumps(report, ensure_ascii=False, indent=2)
        case_progress_str = json.dumps(case_progress, ensure_ascii=False, indent=2) if case_progress else "無相關案場"
        risks_str = json.dumps(risks, ensure_ascii=False, indent=2) if risks else "無進行中風險"
        tasks_str = json.dumps(tasks, ensure_ascii=False, indent=2) if tasks else "無進行中任務"
        
        # 組合提示詞
        prompt = AI_PROMPT_TEMPLATE.format(
            employee_name=emp_info['name'],
            employee_code=emp_info['employee_code'],
            department=emp_info['department'],
            title=emp_info['title'],
            report_content=report_content,
            case_progress=case_progress_str,
            risks=risks_str,
            tasks=tasks_str
        )
        
        # TODO: 呼叫 AI API 生成建議
        # 目前先返回範例
        feedback = f"""
# 🎯 AI 工作建議 - {emp_info['name']} ({emp_info['employee_code']})

**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## ✨ 今日工作亮點

- 感謝您今日提交的詳細日報
- 記錄完整，有助於團隊協作和進度追蹤

## ⚠️ 需要注意的事項

- 請持續關注進行中的風險項目
- 如有需要協助的事項，請及時提出

## 💡 明日工作建議

1. **優先處理**: 查看是否有即將到期的任務
2. **案場進度**: 跟進相關案場的進展
3. **風險管控**: 主動回報潛在問題

## 📚 學習與成長

- 建議定期檢視歷史日報，累積經驗
- 與團隊成員分享最佳實踐

## 🔧 需要的支持

- 如有任何問題，歡迎隨時與主管討論
- 系統會持續追蹤並提供協助

---

*此建議由 AI 生成，如有疑問請與主管討論*
        """.strip()
        
        return feedback
    
    def save_feedback(self, employee_id: str, date: str, feedback: str):
        """儲存 AI 反饋"""
        AI_FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
        
        filename = f"{date}_{employee_id}.md"
        filepath = AI_FEEDBACK_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(feedback)
        
        # 同時寫入資料庫
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT OR REPLACE INTO ai_feedback (
                employee_id, feedback_date, feedback_content, generated_at
            ) VALUES (?, ?, ?, ?)
        """, (employee_id, date, feedback, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        print(f"  ✅ 已儲存 AI 反饋：{filepath}")
    
    def check_new_reports(self):
        """檢查新提交的日報"""
        now = datetime.now()
        check_time = now - timedelta(minutes=self.delay_minutes)
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        # 找出 30 分鐘內提交的日報
        cursor = conn.execute("""
            SELECT DISTINCT employee_id, report_date, submitted_at
            FROM reports
            WHERE submitted_at >= ?
            AND submitted_at < ?
        """, (check_time.isoformat(), now.isoformat()))
        
        reports = cursor.fetchall()
        conn.close()
        
        if reports:
            print(f"\n📊 發現 {len(reports)} 筆新日報，開始生成 AI 反饋...")
            
            for report in reports:
                employee_id = report['employee_id']
                date = report['report_date']
                
                print(f"\n  處理：{employee_id} - {date}")
                
                # 檢查是否已生成
                if self.feedback_exists(employee_id, date):
                    print(f"    ⏭️  已存在，跳過")
                    continue
                
                # 生成反饋
                feedback = self.generate_ai_feedback(employee_id, date)
                
                if feedback:
                    self.save_feedback(employee_id, date, feedback)
                    self.notify_employee(employee_id, feedback)
                else:
                    print(f"    ⚠️  生成失敗")
    
    def feedback_exists(self, employee_id: str, date: str) -> bool:
        """檢查是否已存在反饋"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute("""
            SELECT COUNT(*) FROM ai_feedback
            WHERE employee_id = ? AND feedback_date = ?
        """, (employee_id, date))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def notify_employee(self, employee_id: str, feedback: str):
        """通知員工有新反饋"""
        # 寫入員工通知表
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO employee_notifications 
                (employee_id, title, content, notification_type, created_at, is_read)
                VALUES (?, ?, ?, 'ai_feedback', CURRENT_TIMESTAMP, 0)
            """, (employee_id, '🤖 AI 工作建議已生成', feedback[:500]))
            conn.commit()
            print(f"  📬 已通知員工 {employee_id} 查看 AI 建議")
        except Exception as e:
            print(f"  ⚠️ 通知失敗：{e}")
        finally:
            conn.close()
    
    def run(self):
        """啟動監控"""
        self.running = True
        print("🚀 AI 即時反饋系統已啟動")
        print(f"   - 檢查間隔：{self.check_interval}秒")
        print(f"   - 延遲時間：{self.delay_minutes}分鐘")
        print(f"   - 反饋儲存：{AI_FEEDBACK_DIR}")
        
        while self.running:
            try:
                self.check_new_reports()
            except Exception as e:
                print(f"❌ 錯誤：{e}")
            
            time.sleep(self.check_interval)
    
    def stop(self):
        """停止監控"""
        self.running = False
        print("\n🛑 AI 即時反饋系統已停止")

# 資料庫初始化
def init_ai_feedback_table():
    """建立 ai_feedback 表"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            feedback_date TEXT NOT NULL,
            feedback_content TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            viewed_at TIMESTAMP,
            UNIQUE(employee_id, feedback_date)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_ai_feedback_employee
        ON ai_feedback(employee_id, feedback_date)
    """)
    conn.commit()
    conn.close()
    print("✅ ai_feedback 表已建立")

if __name__ == '__main__':
    import sys
    
    # 初始化資料庫表
    init_ai_feedback_table()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # 測試模式
        print("🧪 測試 AI 反饋系統")
        feedback_system = AIFeedbackSystem()
        
        # 測試生成
        today = datetime.now().strftime('%Y-%m-%d')
        feedback = feedback_system.generate_ai_feedback('yang_zong_wei', today)
        
        if feedback:
            print("\n" + "="*60)
            print(feedback)
            print("="*60)
        else:
            print("❌ 生成失敗")
    else:
        # 啟動監控
        feedback_system = AIFeedbackSystem()
        
        try:
            feedback_system.run()
        except KeyboardInterrupt:
            feedback_system.stop()
