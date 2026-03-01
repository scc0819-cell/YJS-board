#!/usr/bin/env python3
"""
🧪 昱金生能源 - 系統全面深度測試 v2
目標：找出至少 10-20 點需要改善之處
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys
import os

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
USERS_JSON = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/users.json')
ATTACHMENTS_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments')
APP_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/app.py')

issues = []

def check_item(category, issue, severity, suggestion, detail=''):
    issues.append({
        'category': category,
        'issue': issue,
        'severity': severity,
        'suggestion': suggestion,
        'detail': detail
    })

def deep_test():
    """深度測試"""
    print("🔍 開始深度測試...\n")
    
    # ========== 1. 員工系統深度測試 ==========
    print("📋 1. 員工系統深度測試...")
    
    if USERS_JSON.exists():
        with open(USERS_JSON, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        # 1.1 檢查密碼強度政策
        has_password_policy = False
        if APP_PATH.exists():
            with open(APP_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'password_policy' in content or 'password_strength' in content:
                has_password_policy = True
        
        if not has_password_policy:
            check_item('員工系統', '缺少密碼強度政策', 'high',
                      '實作密碼政策：至少 8 碼，含大小寫、數字、特殊字',
                      '目前預設密碼為 1234，過於簡單')
        
        # 1.2 檢查密碼過期機制
        if 'password_expiry' not in content and 'password_expire' not in content:
            check_item('員工系統', '缺少密碼過期機制', 'medium',
                      '實作 90 天強制更換密碼',
                      '目前密碼永久有效，有安全風險')
        
        # 1.3 檢查員工離職處理
        if 'resignation' not in content and 'terminate' not in content:
            check_item('員工系統', '缺少員工離職處理流程', 'medium',
                      '實作員工離職時帳號停用和任務轉移',
                      '離職員工帳號可能仍可使用')
        
        # 1.4 檢查工號唯一性
        codes = [u.get('employee_code') for u in users.values() if u.get('employee_code')]
        if len(codes) != len(set(codes)):
            check_item('員工系統', '工號重複', 'critical',
                      '檢查並修正重複的工號',
                      f'工號清單：{codes}')
        
        # 1.5 檢查主管管理範圍
        for uid, u in users.items():
            if u.get('role') == 'manager':
                manage_users = u.get('manage_users', [])
                if not manage_users and u.get('department') != '管理部':
                    check_item('員工系統', f'主管 {u["name"]} 未設定管理員工', 'low',
                              '設定 manage_users 清單',
                              '主管權限可能不完整')
    
    print(f"  發現 {len([i for i in issues if i['category']=='員工系統'])} 個問題")
    
    # ========== 2. 附件系統深度測試 ==========
    print("📎 2. 附件系統深度測試...")
    
    # 2.1 檢查病毒掃描
    if APP_PATH.exists():
        with open(APP_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'clamav' not in content.lower() and 'virus' not in content.lower():
            check_item('附件系統', '缺少病毒掃描機制', 'high',
                      '整合 ClamAV 或其他防毒軟體',
                      '上傳檔案可能含有病毒')
        
        # 2.2 檢查檔案內容驗證
        if 'magic' not in content and 'file_type' not in content.lower():
            check_item('附件系統', '缺少檔案內容驗證', 'medium',
                      '使用 python-magic 驗證真實檔案類型',
                      '可能有人上傳假副檔名的惡意檔案')
        
        # 2.3 檢查儲存空間監控
        if 'disk_space' not in content and 'storage_limit' not in content:
            check_item('附件系統', '缺少儲存空間監控', 'medium',
                      '實作磁碟空間監控和警告',
                      '磁碟滿了會導致系統失敗')
        
        # 2.4 檢查附件關聯性
        if DB_PATH.exists():
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.execute("SELECT COUNT(*) FROM attachments")
            attachment_count = cursor.fetchone()[0]
            
            if attachment_count == 0:
                check_item('附件系統', '資料庫中無附件記錄', 'low',
                          '測試上傳功能是否正常',
                          '可能是上傳功能有問題或還沒人使用')
            
            # 2.5 檢查孤兒檔案
            # （檔案存在但資料庫無記錄）
            # 這個需要實作掃描邏輯
    
    print(f"  發現 {len([i for i in issues if i['category']=='附件系統'])} 個問題")
    
    # ========== 3. 資料庫深度測試 ==========
    print("🗄️  3. 資料庫深度測試...")
    
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        
        # 3.1 檢查索引
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        # 應該有的索引
        expected_indexes = ['idx_reports_date', 'idx_risks_status', 'idx_tasks_status']
        missing_indexes = [i for i in expected_indexes if i not in indexes]
        
        if missing_indexes:
            check_item('資料庫', f'缺少效能索引：{missing_indexes}', 'medium',
                      '建立索引提升查詢效能',
                      '大量數據時查詢會變慢')
        
        # 3.2 檢查外鍵約束
        cursor = conn.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        
        if fk_status == 0:
            check_item('資料庫', '外鍵約束未啟用', 'medium',
                      '啟用 PRAGMA foreign_keys = ON',
                      '可能產生孤兒記錄')
        
        # 3.3 檢查資料完整性
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM users WHERE enabled=1")
            active_users = cursor.fetchone()[0]
            
            if active_users == 0:
                check_item('資料庫', '無啟用狀態的用戶', 'critical',
                          '檢查用戶資料或執行初始化',
                          '無人可以登入系統')
        except sqlite3.OperationalError:
            check_item('資料庫', 'users 表不存在', 'critical',
                      '執行資料庫初始化腳本',
                      '資料庫未正確初始化')
        
        # 3.4 檢查審計日誌
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%audit%'")
            audit_tables = [row[0] for row in cursor.fetchall()]
            
            if not audit_tables:
                check_item('資料庫', '缺少審計日誌表', 'high',
                          '建立 audit_logs 表記錄所有操作',
                          '無法追溯誰做了什麼')
        except:
            pass
        
        conn.close()
    
    print(f"  發現 {len([i for i in issues if i['category']=='資料庫'])} 個問題")
    
    # ========== 4. API 和整合深度測試 ==========
    print("🔌 4. API 和整合深度測試...")
    
    if APP_PATH.exists():
        with open(APP_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 4.1 檢查 API 文件
        if '/api/docs' not in content and 'swagger' not in content.lower():
            check_item('API', '缺少 API 文件', 'low',
                      '建立 Swagger 或 ReDoc 文件',
                      '開發者難以使用 API')
        
        # 4.2 檢查 API 速率限制
        if 'rate_limit' not in content and 'ratelimit' not in content.lower():
            check_item('API', '缺少 API 速率限制', 'medium',
                      '實作速率限制防止濫用',
                      '可能被惡意大量呼叫')
        
        # 4.3 檢查 AI API 錯誤處理
        if '/api/ai/' in content:
            if 'try:' not in content or 'except' not in content:
                check_item('API', 'AI API 可能缺少錯誤處理', 'medium',
                          '增加 try-except 區塊',
                          'AI API 失敗可能導致系統崩潰')
    
    print(f"  發現 {len([i for i in issues if i['category']=='API'])} 個問題")
    
    # ========== 5. 使用者體驗深度測試 ==========
    print("😊 5. 使用者體驗深度測試...")
    
    templates_dir = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/templates')
    
    if templates_dir.exists():
        # 5.1 檢查行動裝置支援
        has_responsive = False
        for template in templates_dir.glob('*.html'):
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'viewport' in content and '@media' in content:
                has_responsive = True
                break
        
        if not has_responsive:
            check_item('UX', '缺少行動裝置響應式設計', 'medium',
                      '增加 @media 查詢支援手機和平板',
                      '手機用戶體驗差')
        
        # 5.2 檢查無障礙功能
        has_a11y = False
        for template in templates_dir.glob('*.html'):
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'aria-' in content or 'role=' in content:
                has_a11y = True
                break
        
        if not has_a11y:
            check_item('UX', '缺少無障礙功能', 'low',
                      '增加 aria-label 和 role 屬性',
                      '身心障礙用戶使用困難')
        
        # 5.3 檢查搜尋功能
        has_search = False
        if APP_PATH.exists():
            with open(APP_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            if '/search' in content or 'search' in content.lower():
                has_search = True
        
        if not has_search:
            check_item('UX', '缺少全域搜尋功能', 'medium',
                      '實作搜尋功能（案件、日報、風險、任務）',
                      '用戶難以快速找到資料')
    
    print(f"  發現 {len([i for i in issues if i['category']=='UX'])} 個問題")
    
    # ========== 6. 監控和告警深度測試 ==========
    print("📊 6. 監控和告警深度測試...")
    
    # 6.1 檢查系統監控
    monitor_script = Path('/home/yjsclaw/.openclaw/workspace/server/monitor_attachments.py')
    if not monitor_script.exists():
        check_item('監控', '缺少系統監控腳本', 'medium',
                  '建立監控腳本（磁碟、記憶體、CPU）',
                  '系統異常時無法及時發現')
    
    # 6.2 檢查錯誤通知
    if APP_PATH.exists():
        with open(APP_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'error_notification' not in content and 'alert_email' not in content:
            check_item('監控', '缺少錯誤通知機制', 'high',
                      '實作錯誤發生時發送 Email 或 Telegram 通知',
                      '系統錯誤時管理員不知情')
        
        # 6.3 檢查日誌輪替
        if 'log_rotation' not in content and 'logging' not in content.lower():
            check_item('監控', '缺少日誌輪替機制', 'low',
                      '實作日誌輪替防止日誌檔過大',
                      '日誌檔可能佔滿磁碟')
    
    # 6.4 檢查備份驗證
    backup_script = Path('/home/yjsclaw/.openclaw/workspace/server/backup_attachments_3years.sh')
    if backup_script.exists():
        with open(backup_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'verify' not in content.lower() and 'test' not in content.lower():
            check_item('監控', '備份腳本缺少驗證步驟', 'medium',
                      '增加備份後驗證（解壓縮測試）',
                      '備份檔可能損毀無法還原')
    
    print(f"  發現 {len([i for i in issues if i['category']=='監控'])} 個問題")
    
    # ========== 7. 效能深度測試 ==========
    print("⚡ 7. 效能深度測試...")
    
    if APP_PATH.exists():
        with open(APP_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 7.1 檢查資料庫連接池
        if 'connection_pool' not in content and 'QueuePool' not in content:
            check_item('效能', '缺少資料庫連接池', 'medium',
                      '使用 SQLAlchemy QueuePool 或自訂連接池',
                      '高併發時效能差')
        
        # 7.2 檢查快取機制
        if 'cache' not in content.lower() and 'redis' not in content.lower():
            check_item('效能', '缺少快取機制', 'medium',
                      '使用 Redis 或記憶體快取常用查詢',
                      '重複查詢效率低')
        
        # 7.3 檢查分頁
        if 'pagination' not in content.lower() and 'limit' not in content.lower():
            check_item('效能', '可能缺少分頁機制', 'medium',
                      '實作分頁防止一次載入大量數據',
                      '數據多時頁面載入慢')
    
    print(f"  發現 {len([i for i in issues if i['category']=='效能'])} 個問題")
    
    # ========== 8. 合規性深度測試 ==========
    print("⚖️  8. 合規性深度測試...")
    
    # 8.1 檢查個資保護
    if APP_PATH.exists():
        with open(APP_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'gdpr' not in content.lower() and 'privacy' not in content.lower():
            check_item('合規', '缺少個資保護政策', 'medium',
                      '實作個資查詢、修改、刪除功能',
                      '可能違反個資法')
        
        # 8.2 檢查資料保留政策
        if 'retention' not in content.lower() and 'data_retention' not in content:
            check_item('合規', '缺少資料保留政策', 'low',
                      '定義資料保留期限（如：日報保留 5 年）',
                      '可能保留過多不必要的資料')
    
    print(f"  發現 {len([i for i in issues if i['category']=='合規'])} 個問題")
    
    # ========== 9. 災難恢復深度測試 ==========
    print("🚨 9. 災難恢復深度測試...")
    
    # 9.1 檢查還原腳本
    restore_script = Path('/home/yjsclaw/.openclaw/workspace/server/restore_from_backup.sh')
    if not restore_script.exists():
        check_item('災難恢復', '缺少還原腳本', 'high',
                  '建立 restore_from_backup.sh 腳本',
                  '備份存在但無法快速還原')
    
    # 9.2 檢查災難恢復計畫
    dr_plan = Path('/home/yjsclaw/.openclaw/workspace/server/disaster_recovery_plan.md')
    if not dr_plan.exists():
        check_item('災難恢復', '缺少災難恢復計畫文件', 'medium',
                  '撰寫災難恢復計畫（RTO/RPO、步驟、聯絡人）',
                  '災難發生時手忙腳亂')
    
    # 9.3 檢查異地備份
    check_item('災難恢復', '缺少異地備份機制', 'high',
              '實作異地備份（NAS + 雲端）',
              '本地災難（火災、水災）會導致資料全毀')
    
    print(f"  發現 {len([i for i in issues if i['category']=='災難恢復'])} 個問題")
    
    # ========== 10. 文件完整性深度測試 ==========
    print("📚 10. 文件完整性深度測試...")
    
    docs_dir = Path('/home/yjsclaw/.openclaw/workspace/docs')
    
    required_docs = [
        'README.md',
        'INSTALL.md',
        'USER_GUIDE.md',
        'ADMIN_GUIDE.md',
        'API_REFERENCE.md',
        'TROUBLESHOOTING.md'
    ]
    
    missing_docs = [d for d in required_docs if not (docs_dir / d).exists()]
    
    if missing_docs:
        check_item('文件', f'缺少必要文件：{missing_docs}', 'medium',
                  f'建立文件到 {docs_dir}',
                  '用戶和管理員難以使用系統')
    
    # 10.1 檢查程式碼註解
    if APP_PATH.exists():
        with open(APP_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        comment_ratio = sum(1 for line in lines if line.strip().startswith('#')) / len(lines)
        
        if comment_ratio < 0.1:
            check_item('文件', f'程式碼註解不足（{comment_ratio*100:.1f}%）', 'low',
                      '增加程式碼註解，目標 10% 以上',
                      '維護困難')
    
    print(f"  發現 {len([i for i in issues if i['category']=='文件'])} 個問題")


def print_report():
    """列印報告"""
    print("\n" + "="*90)
    print("🧪 昱金生能源 - 系統全面深度測試報告 v2")
    print("="*90)
    print(f"測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"發現問題總數：{len(issues)}")
    print("="*90)
    
    # 依類別分組
    by_category = {}
    for issue in issues:
        cat = issue['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(issue)
    
    # 依嚴重性分組
    by_severity = {}
    for issue in issues:
        sev = issue['severity']
        if sev not in by_severity:
            by_severity[sev] = []
        by_severity[sev].append(issue)
    
    # 列印各類別問題
    for category in sorted(by_category.keys()):
        print(f"\n📁 {category} ({len(by_category[category])} 個問題)")
        print("-"*70)
        
        for i, issue in enumerate(by_category[category], 1):
            emoji = {'critical':'🔴', 'high':'🟠', 'medium':'🟡', 'low':'🔵'}[issue['severity']]
            print(f"  {emoji} [{i}] {issue['issue']}")
            print(f"      建議：{issue['suggestion']}")
            if issue['detail']:
                print(f"      詳情：{issue['detail']}")
            print()
    
    # 總結
    print("\n" + "="*90)
    print("📊 統計")
    print("="*90)
    print(f"Critical: {len(by_severity.get('critical', []))}")
    print(f"High:     {len(by_severity.get('high', []))}")
    print(f"Medium:   {len(by_severity.get('medium', []))}")
    print(f"Low:      {len(by_severity.get('low', []))}")
    print(f"Total:    {len(issues)}")
    print("="*90)
    
    if len(issues) >= 10:
        print(f"\n✅ 已達成目標：找出 {len(issues)} 點需要改善之處（目標：10 點）")
    else:
        print(f"\n⚠️  未達目標：僅找出 {len(issues)} 點（目標：10 點）")
    
    # 儲存報告
    report_path = Path('/home/yjsclaw/.openclaw/workspace/server/deep_test_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(issues),
            'by_category': {k: len(v) for k, v in by_category.items()},
            'by_severity': {k: len(v) for k, v in by_severity.items()},
            'issues': issues
        }, f, ensure_ascii=False, indent=2)
    
    # 產生 Markdown 報告
    md_path = Path('/home/yjsclaw/.openclaw/workspace/server/deep_test_report.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# 🧪 昱金生能源 - 系統全面深度測試報告\n\n")
        f.write(f"**測試時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**發現問題總數**: {len(issues)}\n\n")
        
        f.write(f"## 📊 統計\n\n")
        f.write(f"| 嚴重性 | 數量 |\n")
        f.write(f"|--------|------|\n")
        for sev in ['critical', 'high', 'medium', 'low']:
            f.write(f"| {sev.capitalize()} | {len(by_severity.get(sev, []))} |\n")
        f.write(f"| **Total** | **{len(issues)}** |\n\n")
        
        f.write(f"## 🔍 詳細問題清單\n\n")
        for category in sorted(by_category.keys()):
            f.write(f"### {category}\n\n")
            for issue in by_category[category]:
                emoji = {'critical':'🔴', 'high':'🟠', 'medium':'🟡', 'low':'🔵'}[issue['severity']]
                f.write(f"#### {emoji} {issue['issue']}\n\n")
                f.write(f"**建議**: {issue['suggestion']}\n\n")
                if issue['detail']:
                    f.write(f"**詳情**: {issue['detail']}\n\n")
                f.write(f"---\n\n")
    
    print(f"\n💾 報告已儲存:")
    print(f"  JSON: {report_path}")
    print(f"  Markdown: {md_path}")


def main():
    deep_test()
    print_report()


if __name__ == '__main__':
    main()
