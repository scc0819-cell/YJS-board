#!/usr/bin/env python3
"""
昱金生能源 - 員工編號批量更新
根據董事長提供的完整清單更新系統
"""

import sqlite3
from pathlib import Path

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

# 完整員工清單（董事長提供）
EMPLOYEES = [
    # (員工編號，中文名，系統 ID)
    ('20101', '宋啓綸', 'admin'),
    ('20102', '游若誼', 'you_ruo_yi'),
    ('22104', '洪淑嫆', 'hong_shu_rong'),
    ('23102', '楊宗衛', 'yang_zong_wei'),
    ('24106', '楊傑麟', 'yang_jie_lin'),
    ('24108', '褚佩瑜', 'chu_pei_yu'),
    ('25105', '陳明德', 'chen_ming_de'),
    ('25106', '林天睛', 'lin_tian_jing'),
    ('25107', '顏呈晞', 'yan_cheng_xi'),
    ('25108', '陳靜儒', 'chen_jing_ru'),
    ('25110', '高竹妤', 'gao_zhu_yu'),
    ('24302', '張億峖', 'zhang_yi_chuan'),
    ('25305', '李雅婷', 'li_ya_ting'),
    ('25308', '陳谷濱', 'chen_gu_bin'),
    ('25311', '呂宜芹', 'lu_yi_qin'),
]


def update_employee_codes():
    """更新員工編號"""
    conn = sqlite3.connect(DB_PATH)
    
    print("🔄 開始更新員工編號...\n")
    
    updated_count = 0
    not_found_count = 0
    
    for emp_code, chinese_name, system_id in EMPLOYEES:
        # 檢查用戶是否存在
        cursor = conn.execute("""
            SELECT id, employee_code, chinese_name FROM users
            WHERE id = ?
        """, (system_id,))
        
        user = cursor.fetchone()
        
        if user:
            # 用戶存在，更新編號
            if user[1] != emp_code:
                conn.execute("""
                    UPDATE users
                    SET employee_code = ?
                    WHERE id = ?
                """, (emp_code, system_id))
                old_code = user[1] or '無'
                print(f"✅ 更新：{chinese_name} ({system_id}) - {old_code} → {emp_code}")
                updated_count += 1
            else:
                print(f"✅ 正確：{chinese_name} ({system_id}) - {emp_code}")
        else:
            # 用戶不存在
            print(f"⚠️  用戶不存在：{chinese_name} ({system_id}) - 編號：{emp_code}")
            print(f"    可能需要建立帳號")
            not_found_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 更新完成:")
    print(f"   已更新：{updated_count} 人")
    print(f"   不存在：{not_found_count} 人")
    print(f"   總人數：{len(EMPLOYEES)} 人")


def export_employee_list():
    """匯出員工清單供參考"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.execute("""
        SELECT id, employee_code, chinese_name, department, role, enabled
        FROM users
        ORDER BY employee_code
    """)
    
    users = cursor.fetchall()
    conn.close()
    
    print("\n📋 系統當前員工清單:\n")
    print(f"{'編號':<10} {'姓名':<10} {'系統 ID':<20} {'部門':<10} {'角色':<10} {'狀態'}")
    print("-" * 70)
    
    for user in users:
        status = '✅' if user['enabled'] else '❌'
        role = user['role'] or 'employee'
        dept = user['department'] or '未分類'
        code = user['employee_code'] or '未設定'
        print(f"{code:<10} {user['chinese_name'] or 'N/A':<10} {user['id']:<20} {dept:<10} {role:<10} {status}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        export_employee_list()
    else:
        update_employee_codes()
        print("\n💡 提示：執行 'python3 update_employee_codes_20260301.py list' 查看完整清單")
