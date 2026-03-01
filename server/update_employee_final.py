#!/usr/bin/env python3
"""
昱金生能源 - 員工完整資料更新
根據董事長提供的完整清單更新系統（含部門）
"""

import sqlite3
from pathlib import Path

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

# 完整員工清單（董事長提供）
EMPLOYEES = [
    # (員工編號，中文名，系統 ID, 部門)
    ('20101', '宋啓綸', 'admin', '管理部'),
    ('20102', '游若誼', 'you_ruo_yi', '管理部'),
    ('22104', '洪淑嫆', 'hong_shu_rong', '管理部'),
    ('23102', '楊宗衛', 'yang_zong_wei', '工程部'),
    ('24106', '楊傑麟', 'yang_jie_lin', '管理部'),
    ('24108', '褚佩瑜', 'chu_pei_yu', '管理部'),
    ('25105', '陳明德', 'chen_ming_de', '工程部'),
    ('25106', '林天睛', 'lin_tian_jing', '行政部'),
    ('25107', '顏呈晞', 'yan_cheng_xi', '設計部'),
    ('25108', '陳靜儒', 'chen_jing_ru', '維運部'),
    ('25110', '高竹妤', 'gao_zhu_yu', '設計部'),
    ('24302', '張億峖', 'zhang_yi_chuan', '工程部'),
    ('25305', '李雅婷', 'li_ya_ting', '工程部'),
    ('25308', '陳谷濱', 'chen_gu_bin', '工程部'),
    ('25311', '呂宜芹', 'lu_yi_qin', '行政部'),
]


def update_employees():
    """更新員工資料（編號 + 部門）"""
    conn = sqlite3.connect(DB_PATH)
    
    print("🔄 開始更新員工資料...\n")
    
    updated_count = 0
    not_found_count = 0
    need_create = []
    
    for emp_code, chinese_name, system_id, department in EMPLOYEES:
        # 檢查用戶是否存在
        cursor = conn.execute("""
            SELECT id, employee_code, chinese_name, department FROM users
            WHERE id = ?
        """, (system_id,))
        
        user = cursor.fetchone()
        
        if user:
            # 用戶存在，更新編號和部門
            updates = []
            values = []
            
            if user[1] != emp_code:
                updates.append("employee_code = ?")
                values.append(emp_code)
            
            if user[3] != department:
                updates.append("department = ?")
                values.append(department)
            
            if updates:
                values.append(system_id)
                sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
                conn.execute(sql, values)
                
                old_code = user[1] or '無'
                old_dept = user[3] or '無'
                print(f"✅ 更新：{chinese_name} ({system_id})")
                print(f"   編號：{old_code} → {emp_code}")
                print(f"   部門：{old_dept} → {department}")
                updated_count += 1
            else:
                print(f"✅ 正確：{chinese_name} ({system_id}) - {department}")
        else:
            # 用戶不存在，記錄需要建立的
            print(f"⚠️  用戶不存在：{chinese_name} ({system_id})")
            print(f"   編號：{emp_code}, 部門：{department}")
            need_create.append((emp_code, chinese_name, system_id, department))
            not_found_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 更新完成:")
    print(f"   已更新：{updated_count} 人")
    print(f"   不存在：{not_found_count} 人（需要建立帳號）")
    print(f"   總人數：{len(EMPLOYEES)} 人")
    
    if need_create:
        print(f"\n📋 需要建立的帳號清單:")
        print(f"   | 編號 | 姓名 | 系統 ID | 部門 |")
        print(f"   |------|------|---------|------|")
        for emp_code, chinese_name, system_id, department in need_create:
            print(f"   | {emp_code} | {chinese_name} | {system_id} | {department} |")
        
        # 詢問是否建立
        print(f"\n💡 是否立即建立這些帳號？")
        print(f"   執行：python3 create_new_employees.py")


def export_employee_list():
    """匯出員工清單供參考"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.execute("""
        SELECT id, employee_code, chinese_name, department, role, enabled
        FROM users
        ORDER BY department, employee_code
    """)
    
    users = cursor.fetchall()
    conn.close()
    
    print("\n📋 系統當前員工清單:\n")
    
    # 依部門分組
    by_dept = {}
    for user in users:
        dept = user['department'] or '未分類'
        if dept not in by_dept:
            by_dept[dept] = []
        by_dept[dept].append(dict(user))
    
    for dept, employees in sorted(by_dept.items()):
        print(f"\n### {dept} ({len(employees)}人)\n")
        print(f"{'編號':<10} {'姓名':<10} {'系統 ID':<20} {'角色':<10} {'狀態'}")
        print("-" * 60)
        
        for user in employees:
            status = '✅' if user['enabled'] else '❌'
            role = user['role'] or 'employee'
            code = user['employee_code'] or '未設定'
            name = user['chinese_name'] or 'N/A'
            print(f"{code:<10} {name:<10} {user['id']:<20} {role:<10} {status}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        export_employee_list()
    else:
        update_employees()
        print("\n💡 提示：執行 'python3 update_employee_final.py list' 查看完整清單")
