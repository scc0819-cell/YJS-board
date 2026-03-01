#!/usr/bin/env python3
"""
🧪 昱金生能源 - 系統全面自我測試
目標：找出至少 10 點需要改善之處
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
USERS_JSON = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/users.json')
ATTACHMENTS_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments')
APP_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/app.py')

issues = []

def check_item(category, issue, severity, suggestion):
    """記錄問題"""
    issues.append({
        'category': category,
        'issue': issue,
        'severity': severity,  # critical/high/medium/low
        'suggestion': suggestion
    })

def test_employee_system():
    """測試員工系統"""
    print("📋 測試員工系統...")
    
    # 1. 檢查 users.json
    if not USERS_JSON.exists():
        check_item('員工系統', 'users.json 不存在', 'critical', '執行 setup_employee_system.py 建立檔案')
        return
    
    with open(USERS_JSON, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    # 2. 檢查工號欄位
    missing_codes = []
    for uid, u in users.items():
        if 'employee_code' not in u:
            missing_codes.append(uid)
    
    if missing_codes:
        check_item('員工系統', f'{len(missing_codes)} 個員工缺少 employee_code 欄位', 'high', 
                  f'更新 users.json，為 {missing_codes} 增加工號')
    
    # 3. 檢查中文人名
    missing_names = []
    for uid, u in users.items():
        if 'chinese_name' not in u:
            missing_names.append(uid)
    
    if missing_names:
        check_item('員工系統', f'{len(missing_names)} 個員工缺少 chinese_name 欄位', 'medium',
                  '增加 chinese_name 欄位以便顯示')
    
    # 4. 檢查主管設定
    managers_without_departments = []
    for uid, u in users.items():
        if u.get('role') == 'manager' and not u.get('manage_departments'):
            managers_without_departments.append(uid)
    
    if managers_without_departments:
        check_item('員工系統', f'{len(managers_without_departments)} 位主管未設定管理部門', 'medium',
                  f'為 {managers_without_departments} 設定 manage_departments')
    
    print(f"  ✅ 發現 {len([i for i in issues if i['category']=='員工系統'])} 個問題")


def test_attachment_system():
    """測試附件系統"""
    print("📎 測試附件系統...")
    
    # 5. 檢查附件目錄結構
    if not ATTACHMENTS_DIR.exists():
        check_item('附件系統', '附件目錄不存在', 'critical', '建立附件目錄')
        return
    
    # 6. 檢查年份目錄
    years = [d.name for d in ATTACHMENTS_DIR.iterdir() if d.is_dir() and d.name.isdigit()]
    if not years:
        check_item('附件系統', '無年份目錄（2026-2030）', 'high', '執行 setup_employee_system.py 建立目錄結構')
    
    # 7. 檢查員工目錄
    emp_count = 0
    for year_dir in ATTACHMENTS_DIR.iterdir():
        if year_dir.is_dir() and year_dir.name.isdigit():
            emp_count = len([d for d in year_dir.iterdir() if d.is_dir()])
            break
    
    if emp_count < 10:
        check_item('附件系統', f'員工目錄不足（目前 {emp_count} 個，應為 10 個）', 'high',
                  '執行 setup_employee_system.py 建立完整目錄結構')
    
    # 8. 檢查上傳功能
    if APP_PATH.exists():
        with open(APP_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'ppt' not in content and 'pptx' not in content:
            check_item('附件系統', 'PPT/PPTX 可能未加入白名單', 'medium',
                      '確認 ALLOWED_EXTENSIONS 包含 ppt 和 pptx')
    
    print(f"  ✅ 發現 {len([i for i in issues if i['category']=='附件系統'])} 個問題")


def test_database():
    """測試資料庫"""
    print("🗄️  測試資料庫...")
    
    if not DB_PATH.exists():
        check_item('資料庫', 'app.db 不存在', 'critical', '檢查資料庫初始化')
        return
    
    conn = sqlite3.connect(DB_PATH)
    
    # 9. 檢查必要表格
    required_tables = ['users', 'cases', 'reports', 'risk_items', 'tasks', 'attachments']
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    missing_tables = [t for t in required_tables if t not in tables]
    if missing_tables:
        check_item('資料庫', f'缺少必要表格：{missing_tables}', 'critical',
                  '執行資料庫初始化腳本')
    
    # 10. 檢查 AI 視圖
    required_views = ['v_case_progress', 'v_risk_trend', 'v_employee_performance', 
                      'v_high_risk_alerts', 'v_overdue_tasks_alerts']
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = [row[0] for row in cursor.fetchall()]
    
    missing_views = [v for v in required_views if v not in views]
    if missing_views:
        check_item('資料庫', f'缺少 AI 分析視圖：{missing_views}', 'high',
                  '執行 create_ai_views.py 建立視圖')
    
    # 11. 檢查員工工號視圖
    if 'v_employee_codes' not in views:
        check_item('資料庫', '缺少 v_employee_codes 視圖', 'medium',
                  '執行 setup_employee_system.py 建立視圖')
    
    conn.close()
    print(f"  ✅ 發現 {len([i for i in issues if i['category']=='資料庫'])} 個問題")


def test_templates():
    """測試模板"""
    print("🎨 測試模板...")
    
    templates_dir = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/templates')
    
    if not templates_dir.exists():
        check_item('模板系統', 'templates 目錄不存在', 'critical', '檢查模板安裝')
        return
    
    # 12. 檢查必要模板
    required_templates = ['index_v4.html', 'report_form_v3.html', 'cases.html', 
                         'executive_dashboard.html', 'admin_users.html']
    
    missing_templates = [t for t in required_templates if not (templates_dir / t).exists()]
    if missing_templates:
        check_item('模板系統', f'缺少必要模板：{missing_templates}', 'high',
                  f'複製缺失模板到 {templates_dir}')
    
    # 13. 檢查統一導航
    nav_component = templates_dir / 'components' / 'nav_top.html'
    if not nav_component.exists():
        check_item('模板系統', '缺少統一導航組件（nav_top.html）', 'high',
                  '建立 components/nav_top.html')
    
    # 14. 檢查基礎模板
    base_template = templates_dir / 'base.html'
    if not base_template.exists():
        check_item('模板系統', '缺少基礎模板（base.html）', 'medium',
                  '建立 base.html 作為模板繼承基礎')
    
    print(f"  ✅ 發現 {len([i for i in issues if i['category']=='模板系統'])} 個問題")


def test_scripts():
    """測試腳本"""
    print("📜 測試腳本...")
    
    scripts_dir = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/scripts')
    
    required_scripts = [
        'setup_employee_system.py',
        'create_ai_views.py',
        'backup_attachments_3years.sh',
        'manage_attachments.py'
    ]
    
    missing_scripts = [s for s in required_scripts if not (scripts_dir / s).exists()]
    if missing_scripts:
        check_item('腳本系統', f'缺少必要腳本：{missing_scripts}', 'medium',
                  f'複製腳本到 {scripts_dir}')
    
    # 15. 檢查備份腳本執行權限
    backup_script = scripts_dir / 'backup_attachments_3years.sh'
    if backup_script.exists():
        import os
        if not os.access(backup_script, os.X_OK):
            check_item('腳本系統', '備份腳本無執行權限', 'low',
                      'chmod +x backup_attachments_3years.sh')
    
    print(f"  ✅ 發現 {len([i for i in issues if i['category']=='腳本系統'])} 個問題")


def test_security():
    """測試安全性"""
    print("🔒 測試安全性...")
    
    if not APP_PATH.exists():
        return
    
    with open(APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 16. 檢查登入失敗鎖定
    if 'login_failures' not in content and 'failed_login' not in content:
        check_item('安全性', '可能缺少登入失敗鎖定機制', 'high',
                  '實作 5 次失敗鎖定 15 分鐘')
    
    # 17. 檢查 Session 設定
    if 'SESSION_COOKIE_HTTPONLY' not in content:
        check_item('安全性', '未設定 Session Cookie 安全參數', 'medium',
                  '設定 HTTPOnly=True, SameSite=Lax')
    
    # 18. 檢查附件副檔名驗證
    if 'ALLOWED_EXTENSIONS' not in content:
        check_item('安全性', '缺少附件副檔名白名單', 'critical',
                  '實作副檔名白名單驗證')
    
    print(f"  ✅ 發現 {len([i for i in issues if i['category']=='安全性'])} 個問題")


def test_backup_readiness():
    """測試備份就緒"""
    print("📦 測試備份就緒...")
    
    # 19. 檢查備份腳本
    backup_script = Path('/home/yjsclaw/.openclaw/workspace/server/backup_attachments_3years.sh')
    if not backup_script.exists():
        check_item('備份系統', '缺少三年備份腳本', 'medium',
                  '建立 backup_attachments_3years.sh')
    
    # 20. 檢查備份目錄
    backup_dir = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/attachments_backup')
    if not backup_dir.exists():
        check_item('備份系統', '備份目錄不存在', 'low',
                  '建立 attachments_backup 目錄')
    
    print(f"  ✅ 發現 {len([i for i in issues if i['category']=='備份系統'])} 個問題")


def print_report():
    """列印測試報告"""
    print("\n" + "="*80)
    print("🧪 昱金生能源 - 系統全面自我測試報告")
    print("="*80)
    print(f"測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"發現問題總數：{len(issues)}")
    print("="*80)
    
    # 依嚴重性分組
    by_severity = {}
    for issue in issues:
        sev = issue['severity']
        if sev not in by_severity:
            by_severity[sev] = []
        by_severity[sev].append(issue)
    
    # 列印問題
    for severity in ['critical', 'high', 'medium', 'low']:
        if severity in by_severity:
            emoji = {'critical':'🔴', 'high':'🟠', 'medium':'🟡', 'low':'🔵'}[severity]
            print(f"\n{emoji} {severity.upper()} ({len(by_severity[severity])} 個問題)")
            print("-"*60)
            
            for i, issue in enumerate(by_severity[severity], 1):
                print(f"\  [{i}] {issue['category']}: {issue['issue']}")
                print(f"      建議：{issue['suggestion']}")
    
    # 總結
    print("\n" + "="*80)
    print("📊 統計")
    print("="*80)
    print(f"Critical: {len(by_severity.get('critical', []))}")
    print(f"High:     {len(by_severity.get('high', []))}")
    print(f"Medium:   {len(by_severity.get('medium', []))}")
    print(f"Low:      {len(by_severity.get('low', []))}")
    print(f"Total:    {len(issues)}")
    print("="*80)
    
    if len(issues) >= 10:
        print(f"\n✅ 已達成目標：找出 {len(issues)} 點需要改善之處（目標：10 點）")
    else:
        print(f"\n⚠️  未達目標：僅找出 {len(issues)} 點（目標：10 點）")
    
    # 儲存報告
    report_path = Path('/home/yjsclaw/.openclaw/workspace/server/self_test_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(issues),
            'issues': issues
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 報告已儲存：{report_path}")


def main():
    print("🧪 開始系統全面自我測試...\n")
    
    test_employee_system()
    test_attachment_system()
    test_database()
    test_templates()
    test_scripts()
    test_security()
    test_backup_readiness()
    
    print_report()


if __name__ == '__main__':
    main()
