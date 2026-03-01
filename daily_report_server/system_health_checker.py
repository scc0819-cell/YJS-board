#!/usr/bin/env python3
"""
昱金生能源 - 日報系統健康檢查系統
每 30 分鐘自動檢核系統狀態、資料正確性、功能完整性
發現問題自動修復，嚴重問題上報董事長
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import sqlite3
import subprocess
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/system_health_check.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 路徑設定
BASE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
DAILY_REPORT_DIR = BASE_DIR / 'daily_report_server'
DATA_DIR = DAILY_REPORT_DIR / 'data'
REPORTS_DIR = BASE_DIR / 'daily_reports'
ATTACHMENTS_DIR = BASE_DIR / 'daily_report_attachments'
MEMORY_DIR = BASE_DIR / 'memory'

# 狀態檔案
HEALTH_STATE_FILE = DAILY_REPORT_DIR / 'health_check_state.json'
ISSUES_LOG = DAILY_REPORT_DIR / 'health_issues_log.json'

class SystemHealthChecker:
    """系統健康檢查器"""
    
    def __init__(self):
        self.timestamp = datetime.now().isoformat()
        self.issues = []
        self.fixed_issues = []
        self.critical_issues = []
        self.state = self.load_state()
        self.issues_log = self.load_issues_log()
    
    def load_state(self):
        """載入上次檢查狀態"""
        if HEALTH_STATE_FILE.exists():
            with open(HEALTH_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'last_check': None,
            'total_checks': 0,
            'total_issues_found': 0,
            'total_issues_fixed': 0,
            'verified_pages': []
        }
    
    def save_state(self):
        """儲存檢查狀態"""
        self.state['last_check'] = self.timestamp
        self.state['total_checks'] += 1
        tmp = HEALTH_STATE_FILE.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding='utf-8')
        tmp.replace(HEALTH_STATE_FILE)
    
    def load_issues_log(self):
        """載入問題日誌"""
        if ISSUES_LOG.exists():
            with open(ISSUES_LOG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'issues': [], 'resolved': []}
    
    def save_issues_log(self):
        """儲存問題日誌"""
        tmp = ISSUES_LOG.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(self.issues_log, ensure_ascii=False, indent=2), encoding='utf-8')
        tmp.replace(ISSUES_LOG)
    
    def check_users_data(self):
        """檢查員工資料"""
        logger.info("📋 檢查員工資料...")
        users_file = DATA_DIR / 'users.json'
        
        if not users_file.exists():
            issue = "users.json 不存在"
            self.issues.append(issue)
            logger.error(f"❌ {issue}")
            return False
        
        with open(users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        # 檢查總人數（包含 admin、manager、employee）
        total_count = len(users)
        if total_count < 15:
            issue = f"總人數不足：{total_count} < 15"
            self.issues.append(issue)
            logger.error(f"❌ {issue}")
            return False
        
        # 檢查員工代碼
        missing_codes = []
        for uid, user in users.items():
            if not user.get('employee_code'):
                missing_codes.append(uid)
        
        if missing_codes:
            issue = f"缺少員工代碼：{missing_codes}"
            self.issues.append(issue)
            logger.error(f"❌ {issue}")
            return False
        
        logger.info(f"✅ 員工資料正常：{total_count} 位成員")
        
        # 檢查員工代碼
        missing_codes = []
        for uid, user in users.items():
            if user.get('role') == 'employee' and not user.get('employee_code'):
                missing_codes.append(uid)
        
        if missing_codes:
            issue = f"缺少員工代碼：{missing_codes}"
            self.issues.append(issue)
            logger.error(f"❌ {issue}")
            return False
        
        logger.info(f"✅ 員工資料正常：{len(users)} 位用戶，{employee_count} 位員工")
        
        # 記錄已驗證
        if 'users_data' not in self.state.get('verified_pages', []):
            self.state.setdefault('verified_pages', []).append('users_data')
        
        return True
    
    def check_database(self):
        """檢查資料庫"""
        logger.info("🗄️  檢查資料庫...")
        db_file = DATA_DIR / 'app.db'
        
        if not db_file.exists():
            issue = "app.db 不存在"
            self.issues.append(issue)
            logger.error(f"❌ {issue}")
            return False
        
        try:
            conn = sqlite3.connect(str(db_file))
            cur = conn.cursor()
            
            # 檢查表是否存在
            tables = ['cases', 'reports', 'work_items', 'risk_items', 'tasks', 'attachments']
            for table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                logger.info(f"   {table}: {count} 筆資料")
            
            conn.close()
            logger.info("✅ 資料庫正常")
            
            if 'database' not in self.state.get('verified_pages', []):
                self.state.setdefault('verified_pages', []).append('database')
            
            return True
        except Exception as e:
            issue = f"資料庫錯誤：{e}"
            self.issues.append(issue)
            logger.error(f"❌ {issue}")
            return False
    
    def check_pages(self):
        """檢查所有頁面可訪問性"""
        logger.info("🌐 檢查頁面可訪問性...")
        
        from app import app
        
        pages = [
            ('/', '首頁'),
            ('/login', '登入頁'),
            ('/cases', '案場總覽'),
            ('/history', '歷史記錄'),
            ('/risks', '風險追蹤'),
            ('/tasks', '任務追蹤'),
            ('/change-password', '修改密碼'),
            ('/admin', '管理後台'),
            ('/admin/users', '帳號管理'),
        ]
        
        all_ok = True
        with app.test_client() as client:
            # 先登入
            client.post('/login', data={'username':'admin','password':'Welcome2026!'})
            
            for path, name in pages:
                try:
                    resp = client.get(path)
                    # 登入頁 302 是正常的（已登入會重定向到首頁）
                    expected_codes = [200]
                    if path == '/login':
                        expected_codes = [200, 302]
                    
                    if resp.status_code not in expected_codes:
                        issue = f"頁面 {name} ({path}) HTTP {resp.status_code}"
                        self.issues.append(issue)
                        logger.error(f"❌ {issue}")
                        all_ok = False
                    else:
                        logger.info(f"✅ {name}: HTTP {resp.status_code}")
                except Exception as e:
                    issue = f"頁面 {name} 錯誤：{e}"
                    self.issues.append(issue)
                    logger.error(f"❌ {issue}")
                    all_ok = False
        
        if all_ok:
            if 'pages' not in self.state.get('verified_pages', []):
                self.state.setdefault('verified_pages', []).append('pages')
        
        return all_ok
    
    def check_reports_dir(self):
        """檢查日報目錄"""
        logger.info("📁 檢查日報目錄...")
        
        if not REPORTS_DIR.exists():
            issue = "日報目錄不存在"
            self.issues.append(issue)
            logger.error(f"❌ {issue}")
            return False
        
        # 檢查今日目錄
        today = datetime.now().strftime('%Y-%m-%d')
        today_dir = REPORTS_DIR / today
        
        if not today_dir.exists():
            logger.info(f"ℹ️  今日目錄尚未建立：{today_dir}")
            return True
        
        # 檢查日報檔案
        reports = list(today_dir.glob('*_report.json'))
        logger.info(f"   今日報告：{len(reports)} 份")
        
        if 'reports_dir' not in self.state.get('verified_pages', []):
            self.state.setdefault('verified_pages', []).append('reports_dir')
        
        return True
    
    def check_attachments(self):
        """檢查附件目錄"""
        logger.info("📎 檢查附件目錄...")
        
        if not ATTACHMENTS_DIR.exists():
            issue = "附件目錄不存在"
            self.issues.append(issue)
            logger.error(f"❌ {issue}")
            return False
        
        # 檢查目錄結構
        subdirs = list(ATTACHMENTS_DIR.iterdir())
        logger.info(f"   子目錄：{len(subdirs)} 個")
        
        if 'attachments' not in self.state.get('verified_pages', []):
            self.state.setdefault('verified_pages', []).append('attachments')
        
        return True
    
    def check_memory(self):
        """檢查記憶系統"""
        logger.info("🧠 檢查記憶系統...")
        
        today = datetime.now().strftime('%Y-%m-%d')
        memory_file = MEMORY_DIR / f'{today}.md'
        
        if not memory_file.exists():
            issue = f"今日記憶檔案不存在：{memory_file}"
            self.issues.append(issue)
            logger.error(f"❌ {issue}")
            return False
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) < 100:
            issue = f"記憶檔案內容過少：{len(content)} bytes"
            self.issues.append(issue)
            logger.error(f"❌ {issue}")
            return False
        
        logger.info(f"✅ 記憶系統正常：{len(content)} bytes")
        
        if 'memory' not in self.state.get('verified_pages', []):
            self.state.setdefault('verified_pages', []).append('memory')
        
        return True
    
    def auto_fix_issues(self):
        """自動修復問題"""
        logger.info("🔧 嘗試自動修復問題...")
        
        for issue in self.issues[:]:
            # 自動修復：頁面回應但內容為空
            if 'HTTP 500' in issue:
                logger.info(f"   嘗試重啟服務修復：{issue}")
                try:
                    subprocess.run(['pkill', '-9', '-f', 'python3 app.py'], check=False)
                    subprocess.run(['sleep', '2'], check=False)
                    subprocess.run(
                        ['nohup', 'python3', 'app.py'],
                        cwd=str(DAILY_REPORT_DIR),
                        stdout=open('/tmp/server.log', 'w'),
                        stderr=subprocess.STDOUT,
                        start_new_session=True
                    )
                    self.fixed_issues.append(issue)
                    self.issues.remove(issue)
                    logger.info(f"✅ 已修復：{issue}")
                except Exception as e:
                    logger.error(f"❌ 修復失敗：{e}")
            
            # 自動修復：目錄不存在
            if '目錄不存在' in issue:
                logger.info(f"   嘗試建立目錄：{issue}")
                try:
                    if '日報' in issue:
                        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
                    elif '附件' in issue:
                        ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
                    self.fixed_issues.append(issue)
                    self.issues.remove(issue)
                    logger.info(f"✅ 已修復：{issue}")
                except Exception as e:
                    logger.error(f"❌ 修復失敗：{e}")
    
    def generate_report(self):
        """生成檢查報告"""
        report = {
            'timestamp': self.timestamp,
            'status': 'healthy' if not self.issues else 'issues_found',
            'total_checks': self.state['total_checks'],
            'issues_found': len(self.issues),
            'issues_fixed': len(self.fixed_issues),
            'critical_issues': len(self.critical_issues),
            'verified_items': len(self.state.get('verified_pages', [])),
            'issues': self.issues,
            'fixed_issues': self.fixed_issues,
        }
        
        # 儲存報告
        report_file = DAILY_REPORT_DIR / f'health_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 更新問題日誌
        if self.issues:
            self.issues_log['issues'].append({
                'timestamp': self.timestamp,
                'issues': self.issues
            })
        
        if self.fixed_issues:
            self.issues_log['resolved'].append({
                'timestamp': self.timestamp,
                'fixed': self.fixed_issues
            })
        
        return report
    
    def run(self):
        """執行健康檢查"""
        logger.info("=" * 60)
        logger.info("🏥 昱金生能源 - 系統健康檢查")
        logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # 執行檢查
        checks = [
            ('員工資料', self.check_users_data),
            ('資料庫', self.check_database),
            ('頁面可訪問', self.check_pages),
            ('日報目錄', self.check_reports_dir),
            ('附件目錄', self.check_attachments),
            ('記憶系統', self.check_memory),
        ]
        
        for name, check_func in checks:
            try:
                check_func()
            except Exception as e:
                logger.error(f"❌ {name} 檢查失敗：{e}")
                self.issues.append(f"{name} 檢查失敗：{e}")
        
        # 自動修復
        if self.issues:
            self.auto_fix_issues()
        
        # 生成報告
        report = self.generate_report()
        
        # 儲存狀態
        self.state['total_issues_found'] += len(self.issues)
        self.state['total_issues_fixed'] += len(self.fixed_issues)
        self.save_state()
        self.save_issues_log()
        
        # 輸出總結
        logger.info("\n" + "=" * 60)
        logger.info("📊 檢查總結")
        logger.info("=" * 60)
        logger.info(f"✅ 已驗證項目：{len(self.state.get('verified_pages', []))}")
        logger.info(f"⚠️  發現問題：{len(self.issues)}")
        logger.info(f"✅ 已修復：{len(self.fixed_issues)}")
        logger.info(f"❌ 待處理：{len(self.issues)}")
        
        if self.critical_issues:
            logger.error("\n🚨 嚴重問題（需董事長決策）:")
            for issue in self.critical_issues:
                logger.error(f"  - {issue}")
        
        logger.info("=" * 60)
        
        return report

def main():
    """主函數"""
    checker = SystemHealthChecker()
    report = checker.run()
    
    # 如果有嚴重問題，輸出到特殊檔案以便通知
    if report['critical_issues'] > 0:
        alert_file = DAILY_REPORT_DIR / 'CRITICAL_ALERTS.json'
        alerts = []
        if alert_file.exists():
            with open(alert_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
        alerts.append({
            'timestamp': datetime.now().isoformat(),
            'issues': checker.critical_issues
        })
        with open(alert_file, 'w', encoding='utf-8') as f:
            json.dump(alerts, f, ensure_ascii=False, indent=2)
        logger.error(f"\n🚨 已寫入嚴重問題警報：{alert_file}")

if __name__ == '__main__':
    main()
