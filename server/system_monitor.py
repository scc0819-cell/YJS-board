#!/usr/bin/env python3
"""
昱金生能源 - 系統健康監控
功能：
1. 檢查服務運行狀態
2. 監控資料庫大小
3. 檢查磁碟空間
4. 監控錯誤日誌
5. 發送健康報告
"""

import sqlite3
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
LOG_DIR = Path('/tmp')


class SystemMonitor:
    """系統健康監控"""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    def check_database(self):
        """檢查資料庫健康狀況"""
        print("📊 資料庫檢查:")
        
        if not self.db_path.exists():
            print("  ❌ 資料庫不存在")
            return False
        
        # 檢查大小
        db_size_mb = self.db_path.stat().st_size / 1024 / 1024
        print(f"  ✅ 資料庫大小：{db_size_mb:.2f} MB")
        
        if db_size_mb > 1000:
            print("  ⚠️  警告：資料庫超過 1GB，建議清理")
        
        # 檢查完整性
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            
            if result == 'ok':
                print("  ✅ 資料庫完整性：正常")
            else:
                print(f"  ❌ 資料庫完整性：{result}")
                return False
        except Exception as e:
            print(f"  ❌ 資料庫檢查失敗：{e}")
            return False
        
        # 檢查表數量
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            conn.close()
            print(f"  ✅ 資料表數量：{table_count}")
        except:
            pass
        
        return True
    
    def check_disk_space(self):
        """檢查磁碟空間"""
        print("\n💾 磁碟空間檢查:")
        
        total, used, free = shutil.disk_usage('/mnt/c')
        total_gb = total / 1024 / 1024 / 1024
        used_gb = used / 1024 / 1024 / 1024
        free_gb = free / 1024 / 1024 / 1024
        used_percent = (used / total) * 100
        
        print(f"  總容量：{total_gb:.2f} GB")
        print(f"  已使用：{used_gb:.2f} GB ({used_percent:.1f}%)")
        print(f"  可用：{free_gb:.2f} GB")
        
        if used_percent > 90:
            print("  🔴 嚴重：磁碟空間不足 10%")
            return False
        elif used_percent > 80:
            print("  🟡 警告：磁碟空間不足 20%")
            return True
        else:
            print("  ✅ 磁碟空間：正常")
            return True
    
    def check_services(self):
        """檢查服務運行狀態"""
        print("\n🔧 服務狀態檢查:")
        
        # 檢查 AI 反饋服務
        result = os.system("pgrep -f 'ai_feedback_system.py' > /dev/null 2>&1")
        if result == 0:
            print("  ✅ AI 即時反饋：運行中")
        else:
            print("  ❌ AI 即時反饋：未運行")
        
        # 檢查 Flask 服務
        result = os.system("pgrep -f 'python.*app.py' > /dev/null 2>&1")
        if result == 0:
            print("  ✅ Web 伺服器：運行中")
        else:
            print("  ❌ Web 伺服器：未運行")
    
    def check_recent_errors(self):
        """檢查近期錯誤"""
        print("\n⚠️  近期錯誤檢查:")
        
        # 檢查錯誤日誌
        error_log = LOG_DIR / 'daily_report_errors.log'
        if error_log.exists():
            try:
                with open(error_log, 'r') as f:
                    lines = f.readlines()
                
                # 檢查最近 10 行的錯誤
                recent_errors = [l for l in lines[-10:] if 'ERROR' in l or 'Exception' in l]
                
                if recent_errors:
                    print(f"  🟡 發現 {len(recent_errors)} 個錯誤:")
                    for err in recent_errors[:3]:
                        print(f"     {err.strip()[:80]}...")
                else:
                    print("  ✅ 無近期錯誤")
            except:
                print("  ⚠️  無法讀取錯誤日誌")
        else:
            print("  ✅ 無錯誤日誌檔案")
    
    def check_data_freshness(self):
        """檢查資料新鮮度"""
        print("\n📅 資料新鮮度檢查:")
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # 檢查最新日報日期
            cursor = conn.execute("""
                SELECT MAX(report_date) FROM reports
            """)
            latest_report = cursor.fetchone()[0]
            
            if latest_report:
                days_ago = (datetime.now().strftime('%Y-%m-%d') > latest_report)
                print(f"  最新日報：{latest_report}")
                if days_ago:
                    print("  ⚠️  警告：最新日報不是今天")
                else:
                    print("  ✅ 日報更新：正常")
            else:
                print("  ⚠️  無日報資料")
            
            # 檢查用戶數量
            cursor = conn.execute("""
                SELECT COUNT(*) FROM users WHERE enabled = 1
            """)
            user_count = cursor.fetchone()[0]
            print(f"  在職員工：{user_count} 人")
            
            conn.close()
        except Exception as e:
            print(f"  ❌ 檢查失敗：{e}")
    
    def generate_health_report(self):
        """生成健康報告"""
        print("\n" + "="*60)
        print("📊 系統健康報告")
        print("="*60)
        print(f"檢查時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        self.check_database()
        self.check_disk_space()
        self.check_services()
        self.check_recent_errors()
        self.check_data_freshness()
        
        print("\n" + "="*60)
        print("✅ 檢查完成")
        print("="*60)


if __name__ == '__main__':
    monitor = SystemMonitor()
    monitor.generate_health_report()
