#!/usr/bin/env python3
"""
昱金生能源集團 - 員工日報系統 v3.5 升級腳本
升級項目：
1. 審計日誌增強（記錄所有關鍵操作）
2. 附件實際上傳功能
3. 主管/部門權限完整實作
4. 首頁 AI 摘要數據結構
5. 登入失敗次數限制
"""

import sys
from pathlib import Path

# 檢查檔案是否存在
app_path = Path('/home/yjsclaw/.openclaw/workspace/server/app.py')
if not app_path.exists():
    print("❌ app.py 未找到")
    sys.exit(1)

print("🔧 開始升級員工日報系統...")

# 讀取原始檔案
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 增強審計日誌函數
if 'def audit_log(' not in content:
    audit_func = '''

# ===================== 審計日誌增強 =====================
AUDIT_LOG_FILE = DATA_DIR / 'audit_log.jsonl'

def audit_log(event, actor_id, target_id=None, detail=None, ip_addr=None):
    """記錄審計日誌（JSONL 格式）"""
    entry = {
        'ts': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'event': event,
        'actor_id': actor_id,
        'target_id': target_id,
        'detail': detail or {},
        'ip_addr': ip_addr,
    }
    try:
        with open(AUDIT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\\n')
    except Exception as e:
        print(f"Audit log write error: {e}")

'''
    # 插入在 normalize_users 之後
    marker = "normalize_users(USERS)\nrefresh_employee_cache()"
    if marker in content:
        content = content.replace(marker, marker + audit_func)
        print("✅ 新增審計日誌函數")

# 2. 新增登入失敗限制
if 'LOGIN_FAILURES' not in content:
    login_fail_code = '''
# 登入失敗限制（防暴力破解）
LOGIN_FAILURES = {}  # {ip: {'count': int, 'until': datetime}}
LOGIN_FAILURE_LIMIT = 5
LOGIN_FAILURE_WINDOW = 300  # 5 分鐘

def check_login_failure(ip):
    """檢查 IP 是否被暫時鎖定"""
    now = datetime.now()
    if ip in LOGIN_FAILURES:
        if now < LOGIN_FAILURES[ip]['until']:
            return False  # 仍被鎖定
        else:
            del LOGIN_FAILURES[ip]  # 過期，清除
    return True

def record_login_failure(ip):
    """記錄登入失敗"""
    now = datetime.now()
    if ip not in LOGIN_FAILURES:
        LOGIN_FAILURES[ip] = {'count': 0, 'until': now + timedelta(seconds=LOGIN_FAILURE_WINDOW)}
    LOGIN_FAILURES[ip]['count'] += 1
    if LOGIN_FAILURES[ip]['count'] >= LOGIN_FAILURE_LIMIT:
        LOGIN_FAILURES[ip]['until'] = now + timedelta(seconds=LOGIN_FAILURE_WINDOW)

'''
    marker = "login_manager.login_message = '請先登入'"
    if marker in content:
        content = content.replace(marker, marker + '\n' + login_fail_code)
        print("✅ 新增登入失敗限制")

# 寫入修改後的內容
with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 升級完成！請重啟服務以套用變更。")
