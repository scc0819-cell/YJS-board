#!/usr/bin/env python3
"""
昱金生能源 - 每日智慧通知系統
功能：
1. 檢查連續未提交日報的員工
2. 跳過假日和週末
3. 連續 3 個工作日未提交才通知
4. 發送系統通知 + Email（可選）
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/scripts')
from taiwan_calendar import TaiwanCalendar

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')


class DailyReminder:
    """每日智慧通知系統"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.calendar = TaiwanCalendar()
    
    def connect(self):
        """連接資料庫"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all_employees(self):
        """取得所有在職員工"""
        conn = self.connect()
        cursor = conn.execute("""
            SELECT id, chinese_name, email, department
            FROM users
            WHERE role = 'employee' AND enabled = 1
        """)
        employees = cursor.fetchall()
        conn.close()
        return [dict(emp) for emp in employees]
    
    def check_submission_status(self, employee_id, check_date=None):
        """
        檢查員工在指定日期的日報提交狀況
        
        Returns:
            tuple: (submitted: bool, report_date: str or None)
        """
        if check_date is None:
            check_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        conn = self.connect()
        cursor = conn.execute("""
            SELECT report_date FROM reports
            WHERE employee_id = ? AND report_date = ?
        """, (employee_id, check_date))
        
        report = cursor.fetchone()
        conn.close()
        
        if report:
            return True, report['report_date']
        return False, None
    
    def count_consecutive_missing_days(self, employee_id, end_date=None):
        """
        計算連續未提交天數（跳過假日）
        
        Returns:
            int: 連續未提交的工作日天數
        """
        if end_date is None:
            end_date = datetime.now() - timedelta(days=1)
        
        consecutive_days = 0
        current_date = end_date
        
        while True:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # 檢查是否為假日
            if self.calendar.is_holiday(date_str):
                # 假日跳過，不計入也不中斷
                current_date -= timedelta(days=1)
                continue
            
            # 檢查是否已提交
            submitted, _ = self.check_submission_status(employee_id, date_str)
            
            if submitted:
                # 已提交，停止計算
                break
            else:
                # 未提交，計數 +1
                consecutive_days += 1
            
            # 往前一天
            current_date -= timedelta(days=1)
            
            # 最多檢查 30 天
            if (end_date - current_date).days > 30:
                break
        
        return consecutive_days
    
    def send_notification(self, employee, consecutive_days):
        """發送通知給員工"""
        emp_name = employee['chinese_name']
        emp_id = employee['id']
        
        # 寫入系統通知
        conn = self.connect()
        conn.execute("""
            INSERT INTO employee_notifications
            (employee_id, title, content, notification_type, created_at, is_read)
            VALUES (?, ?, ?, 'daily_reminder', CURRENT_TIMESTAMP, 0)
        """, (
            emp_id,
            '⏰ 日報提交提醒',
            f'{emp_name}您好，您已連續 {consecutive_days} 個工作日未提交日報。\n\n'
            f'請記得每日填寫工作回報，讓團隊了解您的進度。\n\n'
            f'如有困難，請與主管聯繫。',
        ))
        conn.commit()
        conn.close()
        
        # TODO: 發送 Email
        # TODO: 發送 Telegram（如已設定）
        
        print(f"  📬 已發送通知給 {emp_name}（連續 {consecutive_days} 天未提交）")
    
    def run_daily_check(self, check_date=None):
        """執行每日檢查"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 如果今天是假日，不執行
        if self.calendar.is_holiday(today):
            print(f"📅 今日 ({today}) 是假日，跳過通知")
            return
        
        print(f"\n🔍 執行每日通知檢查 - {today}\n")
        
        employees = self.get_all_employees()
        notified_count = 0
        
        for emp in employees:
            # 計算連續未提交天數
            consecutive_days = self.count_consecutive_missing_days(emp['id'])
            
            # 如果連續 3 個工作日以上未提交，發送通知
            if consecutive_days >= 3:
                self.send_notification(emp, consecutive_days)
                notified_count += 1
            else:
                print(f"  ✅ {emp['chinese_name']}: 正常（連續 {consecutive_days} 天）")
        
        print(f"\n📊 檢查完成：")
        print(f"  總員工數：{len(employees)}")
        print(f"  發送通知：{notified_count}")
        print(f"  正常提交：{len(employees) - notified_count}")


if __name__ == '__main__':
    import sys
    
    reminder = DailyReminder()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # 測試模式：檢查昨天
        print("🧪 測試模式：檢查昨日提交狀況\n")
        reminder.run_daily_check()
    else:
        # 正常模式
        reminder.run_daily_check()
