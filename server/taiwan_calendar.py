#!/usr/bin/env python3
"""
昱金生能源 - 日曆連動系統
功能：
1. 整合台灣國定假日日曆
2. 自動跳過連假、週末
3. 可自訂「免提交日期」
4. 智慧通知規則（連續 3 個工作日未提交才通知）
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
HOLIDAY_CACHE_FILE = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/holiday_cache.json')


class TaiwanCalendar:
    """台灣日曆系統"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.holiday_cache = self._load_holiday_cache()
        self.custom_holidays = self._load_custom_holidays()
    
    def _load_holiday_cache(self):
        """載入假日快取"""
        if HOLIDAY_CACHE_FILE.exists():
            try:
                with open(HOLIDAY_CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_holiday_cache(self):
        """儲存假日快取"""
        with open(HOLIDAY_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.holiday_cache, f, ensure_ascii=False, indent=2)
    
    def _load_custom_holidays(self):
        """載入自訂假日"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT date, reason, is_holiday FROM custom_holidays
                WHERE is_holiday = 1
            """)
            return {row[0]: row[1] for row in cursor.fetchall()}
        except sqlite3.OperationalError:
            # 表不存在
            return {}
        finally:
            conn.close()
    
    def fetch_holidays_from_api(self, year=None):
        """從政府 API 抓取假日資料"""
        if year is None:
            year = datetime.now().year
        
        try:
            # 台灣政府開放資料 API
            url = f"https://data.ntu.edu.tw/api/holidays/{year}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 解析假日
                holidays = {}
                for item in data:
                    date = item['date']
                    name = item['name']
                    holidays[date] = name
                
                # 更新快取
                self.holiday_cache[str(year)] = holidays
                self._save_holiday_cache()
                
                print(f"✅ 已抓取 {year} 年 {len(holidays)} 個假日")
                return holidays
            
        except Exception as e:
            print(f"⚠️ 抓取假日失敗：{e}")
        
        # 如果 API 失敗，使用內建基本假日
        return self._get_builtin_holidays(year)
    
    def _get_builtin_holidays(self, year):
        """內建基本假日（備援）"""
        holidays = {}
        
        # 元旦
        holidays[f"{year}-01-01"] = "中華民國開國紀念日"
        
        # 春節（簡化，實際日期需查曆法）
        lunar_new_year = self._get_lunar_new_year(year)
        for i in range(3):
            date = lunar_new_year + timedelta(days=i)
            holidays[date.strftime('%Y-%m-%d')] = "春節"
        
        # 228
        holidays[f"{year}-02-28"] = "和平紀念日"
        
        # 清明節（簡化為 4/4 或 4/5）
        holidays[f"{year}-04-04"] = "兒童節"
        holidays[f"{year}-04-05"] = "清明節"
        
        # 勞動節
        holidays[f"{year}-05-01"] = "勞動節"
        
        # 端午節（簡化）
        dragon_boat = self._get_dragon_boat_festival(year)
        holidays[dragon_boat.strftime('%Y-%m-%d')] = "端午節"
        
        # 中秋節（簡化）
        mid_autumn = self._get_mid_autumn_festival(year)
        holidays[mid_autumn.strftime('%Y-%m-%d')] = "中秋節"
        
        # 國慶日
        holidays[f"{year}-10-10"] = "國慶日"
        
        return holidays
    
    def _get_lunar_new_year(self, year):
        """取得春節日期（簡化）"""
        # 實際應使用農曆轉換庫
        # 這裡使用近似值
        dates = {
            2025: datetime(2025, 1, 29),
            2026: datetime(2026, 2, 17),
            2027: datetime(2027, 2, 6),
        }
        return dates.get(year, datetime(year, 1, 29))
    
    def _get_dragon_boat_festival(self, year):
        """取得端午節日期（簡化）"""
        # 農曆五月初五
        dates = {
            2025: datetime(2025, 5, 31),
            2026: datetime(2026, 6, 19),
            2027: datetime(2027, 6, 9),
        }
        return dates.get(year, datetime(year, 6, 1))
    
    def _get_mid_autumn_festival(self, year):
        """取得中秋節日期（簡化）"""
        # 農曆八月十五
        dates = {
            2025: datetime(2025, 10, 6),
            2026: datetime(2026, 9, 25),
            2027: datetime(2027, 9, 15),
        }
        return dates.get(year, datetime(year, 9, 1))
    
    def is_holiday(self, date=None):
        """判斷是否為假日"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        elif isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')
        
        # 檢查是否為週末
        dt = datetime.strptime(date, '%Y-%m-%d')
        if dt.weekday() >= 5:  # 星期六或日
            return True
        
        # 檢查國定假日
        year = str(dt.year)
        if year not in self.holiday_cache:
            self.fetch_holidays_from_api(dt.year)
        
        if date in self.holiday_cache.get(year, {}):
            return True
        
        # 檢查自訂假日
        if date in self.custom_holidays:
            return True
        
        return False
    
    def is_workday(self, date=None):
        """判斷是否為工作日"""
        return not self.is_holiday(date)
    
    def get_workdays_in_range(self, start_date, end_date):
        """取得日期範圍內的工作日"""
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        workdays = []
        current = start_date
        
        while current <= end_date:
            if self.is_workday(current):
                workdays.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return workdays
    
    def get_consecutive_workdays_without_report(self, employee_id, end_date=None, max_days=10):
        """
        計算員工連續多少個工作日未提交日報
        
        Returns:
            (consecutive_days, should_notify)
            consecutive_days: 連續未提交天數
            should_notify: 是否應該發送通知（連續 3 天以上）
        """
        if end_date is None:
            end_date = datetime.now()
        
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        
        consecutive = 0
        current = end_date
        
        # 往回推算
        while consecutive < max_days:
            date_str = current.strftime('%Y-%m-%d')
            
            # 如果是假日，跳過
            if self.is_holiday(current):
                current -= timedelta(days=1)
                continue
            
            # 檢查是否有提交日報
            report_key = f"{date_str}_{employee_id}"
            cursor = conn.execute("""
                SELECT COUNT(*) FROM reports
                WHERE report_key = ?
            """, (report_key,))
            
            count = cursor.fetchone()[0]
            
            if count > 0:
                # 有提交，停止計算
                break
            else:
                # 未提交，繼續累加
                consecutive += 1
            
            current -= timedelta(days=1)
        
        conn.close()
        
        # 連續 3 個工作日以上才通知
        should_notify = consecutive >= 3
        
        return consecutive, should_notify
    
    def add_custom_holiday(self, date, reason, is_holiday=True):
        """新增自訂假日"""
        conn = sqlite3.connect(self.db_path)
        
        # 建立表（如果不存在）
        conn.execute("""
            CREATE TABLE IF NOT EXISTS custom_holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE,
                reason TEXT,
                is_holiday INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 插入或更新
        conn.execute("""
            INSERT OR REPLACE INTO custom_holidays (date, reason, is_holiday)
            VALUES (?, ?, ?)
        """, (date, reason, 1 if is_holiday else 0))
        
        conn.commit()
        conn.close()
        
        # 更新快取
        self.custom_holidays = self._load_custom_holidays()
        
        print(f"✅ 已新增自訂假日：{date} - {reason}")
    
    def get_next_workday(self, date=None):
        """取得下一個工作日"""
        if date is None:
            date = datetime.now()
        
        current = date + timedelta(days=1)
        
        while self.is_holiday(current):
            current += timedelta(days=1)
        
        return current
    
    def get_previous_workday(self, date=None):
        """取得上一個工作日"""
        if date is None:
            date = datetime.now()
        
        current = date - timedelta(days=1)
        
        while self.is_holiday(current):
            current -= timedelta(days=1)
        
        return current
    
    def get_workday_summary(self, year=None, month=None):
        """取得工作日統計"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        # 該月所有天數
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        
        current = datetime(year, month, 1)
        
        total_days = 0
        workdays = 0
        weekends = 0
        holidays = 0
        
        while current < next_month:
            total_days += 1
            date_str = current.strftime('%Y-%m-%d')
            
            if current.weekday() >= 5:
                weekends += 1
            elif date_str in self.holiday_cache.get(str(year), {}):
                holidays += 1
            else:
                workdays += 1
            
            current += timedelta(days=1)
        
        return {
            'year': year,
            'month': month,
            'total_days': total_days,
            'workdays': workdays,
            'weekends': weekends,
            'holidays': holidays
        }


# Flask 路由整合
def register_calendar_routes(app):
    """註冊日曆路由到 Flask app"""
    
    @app.route('/api/calendar/holidays')
    def api_get_holidays():
        from flask import request, jsonify
        
        year = request.args.get('year', datetime.now().year, type=int)
        
        calendar = TaiwanCalendar()
        holidays = calendar.holiday_cache.get(str(year), {})
        
        return jsonify({
            'year': year,
            'holidays': holidays
        })
    
    @app.route('/api/calendar/workdays')
    def api_get_workdays():
        from flask import request, jsonify
        
        start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end = request.args.get('end', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        
        calendar = TaiwanCalendar()
        workdays = calendar.get_workdays_in_range(start, end)
        
        return jsonify({
            'start': start,
            'end': end,
            'workdays': workdays,
            'count': len(workdays)
        })
    
    @app.route('/api/calendar/check-notification')
    def api_check_notification():
        from flask import request, jsonify
        
        employee_id = request.args.get('employee_id')
        
        if not employee_id:
            return jsonify({'error': '需要員工 ID'}), 400
        
        calendar = TaiwanCalendar()
        consecutive, should_notify = calendar.get_consecutive_workdays_without_report(employee_id)
        
        return jsonify({
            'employee_id': employee_id,
            'consecutive_days': consecutive,
            'should_notify': should_notify
        })


if __name__ == '__main__':
    import sys
    
    calendar = TaiwanCalendar()
    
    # 抓取今年假日
    print("📅 抓取 2026 年假日資料...")
    holidays = calendar.fetch_holidays_from_api(2026)
    
    print(f"\n✅ 已載入 {len(holidays)} 個假日\n")
    
    # 測試功能
    today = datetime.now()
    
    print(f"📊 今日資訊:")
    print(f"  日期：{today.strftime('%Y-%m-%d')}")
    print(f"  是否假日：{'✅ 是' if calendar.is_holiday() else '❌ 否'}")
    print(f"  是否工作日：{'✅ 是' if calendar.is_workday() else '❌ 否'}")
    
    # 下個月工作日統計
    next_month = today.month + 1 if today.month < 12 else 1
    next_year = today.year if today.month < 12 else today.year + 1
    
    summary = calendar.get_workday_summary(next_year, next_month)
    
    print(f"\n📊 {next_year}年{next_month}月 工作日統計:")
    print(f"  總天數：{summary['total_days']}")
    print(f"  工作日：{summary['workdays']}")
    print(f"  週末：{summary['weekends']}")
    print(f"  假日：{summary['holidays']}")
    
    # 測試連續未提交
    if len(sys.argv) > 1:
        employee_id = sys.argv[1]
        consecutive, should_notify = calendar.get_consecutive_workdays_without_report(employee_id)
        
        print(f"\n📬 員工 {employee_id} 未提交日報:")
        print(f"  連續天數：{consecutive} 天")
        print(f"  是否通知：{'✅ 是' if should_notify else '❌ 否'}")
