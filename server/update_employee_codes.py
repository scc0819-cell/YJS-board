#!/usr/bin/env python3
"""
昱金生能源 - 員工工號更新腳本
使用真實員工編號（非 A/B/C 前綴）

員工編號對照表（依據董事長提供）：
| 姓名   | 員工編號 | 部門   | 職稱   |
| ------ | -------- | ------ | ------ |
| 宋啓綸  | [待填寫]  | 管理部  | 董事長  |
| 李雅婷  | [待填寫]  | 管理部  | 管理員  |
| 陳明德  | [待填寫]  | 工程部  | 工程專員 |
| 楊宗衛  | 23102    | 工程部  | 工程專員 |
| 洪淑嫆  | [待填寫]  | 工程部  | 工程專員 |
| 陳谷濱  | 25308    | 財務部  | 財務專員 |
| 張億峖  | [待填寫]  | 維運部  | 維運專員 |
| 林坤誼  | [待填寫]  | 維運部  | 維運專員 |
| 黃振豪  | [待填寫]  | 維運部  | 維運專員 |
| 許惠玲  | [待填寫]  | 維運部  | 維運專員 |
"""

import json
from pathlib import Path

USERS_JSON = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/users.json')

# 員工編號對照表（請董事長確認完整清單）
EMPLOYEE_CODES = {
    'admin': '10001',      # 宋啓綸（董事長）- 範例
    'li_ya_ting': '10002', # 李雅婷（管理員）- 範例
    'chen_ming_de': '20001', # 陳明德 - 範例
    'yang_zong_wei': '23102', # ✅ 楊宗衛
    'hong_shu_rong': '20003', # 洪淑嫆 - 範例
    'chen_gu_bin': '25308',   # ✅ 陳谷濱
    'zhang_yi_chuan': '30001', # 張億峖 - 範例
    'lin_kun_yi': '30002',     # 林坤誼 - 範例
    'huang_zhen_hao': '30003', # 黃振豪 - 範例
    'xu_hui_ling': '30004',    # 許惠玲 - 範例
}

def update_employee_codes():
    """更新員工編號"""
    print("📋 昱金生能源 - 員工工號更新")
    print("="*60)
    
    if not USERS_JSON.exists():
        print("❌ users.json 不存在")
        return
    
    with open(USERS_JSON, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    print("\n🔄 更新員工編號...\n")
    
    updated = 0
    for uid, user in users.items():
        if uid in EMPLOYEE_CODES:
            old_code = user.get('employee_code', 'N/A')
            new_code = EMPLOYEE_CODES[uid]
            user['employee_code'] = new_code
            print(f"  {user.get('chinese_name', user.get('name', uid)):10} | {uid:20} | {old_code:10} → {new_code}")
            updated += 1
    
    # 寫回
    with open(USERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已更新 {updated} 位員工編號")
    print("\n💡 請確認員工編號是否正確，如有需要請提供完整清單！")
    print("\n📊 系統顯示格式：")
    print("  - 工號：23102（真實員工編號）")
    print("  - 姓名：楊宗衛")
    print("  - 顯示：23102 - 楊宗衛")

if __name__ == '__main__':
    update_employee_codes()
