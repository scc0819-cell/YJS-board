#!/usr/bin/env python3
"""
改善：將人員 ID 改為工號，存檔路徑改為「工號 + 中文人名」
目的：
1. 使用公司內部工號系統
2. 存檔路徑更直觀（工號 + 中文人名）
3. 保持系統內部仍使用 employee_id 作為主鍵
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
USERS_JSON = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/users.json')

# 昱金生能源集團 - 員工工號對照表
# 格式：工號 (EMP-XXX)
EMPLOYEE_CODES = {
    'admin': 'EMP-001',      # 宋董事長
    'li_ya_ting': 'EMP-002', # 李雅婷
    'chen_ming_de': 'EMP-003', # 陳明德
    'yang_zong_wei': 'EMP-004', # 楊宗衛
    'hong_shu_rong': 'EMP-005', # 洪淑嫆
    'chen_gu_bin': 'EMP-006', # 陳谷濱
    'zhang_yi_chuan': 'EMP-007', # 張億峖
    'lin_kun_yi': 'EMP-008', # 林坤誼
    'huang_zhen_hao': 'EMP-009', # 黃振豪
    'xu_hui_ling': 'EMP-010', # 許惠玲
}

# 中文人名對照
EMPLOYEE_NAMES = {
    'admin': '宋董事長',
    'li_ya_ting': '李雅婷',
    'chen_ming_de': '陳明德',
    'yang_zong_wei': '楊宗衛',
    'hong_shu_rong': '洪淑嫆',
    'chen_gu_bin': '陳谷濱',
    'zhang_yi_chuan': '張億峖',
    'lin_kun_yi': '林坤誼',
    'huang_zhen_hao': '黃振豪',
    'xu_hui_ling': '許惠玲',
}

def get_employee_folder_name(employee_id: str) -> str:
    """
    產生員工資料夾名稱（工號 + 中文人名）
    
    範例：
    - EMP-003_陳明德
    - EMP-007_張億峖
    """
    emp_code = EMPLOYEE_CODES.get(employee_id, 'EMP-XXX')
    emp_name = EMPLOYEE_NAMES.get(employee_id, employee_id)
    return f"{emp_code}_{emp_name}"


def update_users_json():
    """更新 users.json，增加 employee_code 和 chinese_name 欄位"""
    
    print("📋 開始更新員工工號系統...")
    
    if USERS_JSON.exists():
        with open(USERS_JSON, 'r', encoding='utf-8') as f:
            users = json.load(f)
    else:
        users = {}
    
    # 更新每個員工的資料
    for emp_id in EMPLOYEE_CODES.keys():
        if emp_id not in users:
            users[emp_id] = {
                'id': emp_id,
                'name': EMPLOYEE_NAMES.get(emp_id, emp_id),
                'employee_code': EMPLOYEE_CODES[emp_id],
                'chinese_name': EMPLOYEE_NAMES.get(emp_id, emp_id),
                'department': '未分類',
                'role': 'employee',
                'enabled': True,
                'password_temp': False
            }
        else:
            # 增加工號和中文人名欄位
            users[emp_id]['employee_code'] = EMPLOYEE_CODES.get(emp_id, 'EMP-XXX')
            users[emp_id]['chinese_name'] = EMPLOYEE_NAMES.get(emp_id, emp_id)
            # 更新姓名為中文
            users[emp_id]['name'] = EMPLOYEE_NAMES.get(emp_id, users[emp_id].get('name', emp_id))
    
    # 寫入 users.json
    with open(USERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 {len(users)} 個員工資料")
    
    # 顯示更新後的資料
    print("\n📊 員工工號對照表：")
    print(f"{'系統 ID':20} | {'工號':10} | {'中文人名':10} | {'部門':10}")
    print("-" * 60)
    for emp_id, emp_code in EMPLOYEE_CODES.items():
        emp_name = EMPLOYEE_NAMES.get(emp_id, emp_id)
        dept = users.get(emp_id, {}).get('department', '未分類')
        print(f"{emp_id:20} | {emp_code:10} | {emp_name:10} | {dept:10}")
    
    return users


def get_attachment_path(employee_id: str, report_date: str = None) -> Path:
    """
    產生附件存放路徑（工號 + 中文人名）
    
    格式：/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments/年份/日期/工號_人名/時間戳/類型/
    
    範例：
    /mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments/2026/2026-03-01/EMP-003_陳明德/20260301_143022/photo/
    """
    base_path = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments')
    
    if report_date:
        # 有指定日期
        date_obj = datetime.strptime(report_date, '%Y-%m-%d')
        year = date_obj.year
        folder_name = get_employee_folder_name(employee_id)
        return base_path / str(year) / report_date / folder_name
    else:
        # 沒有指定日期，只到員工資料夾
        folder_name = get_employee_folder_name(employee_id)
        return base_path / folder_name


def migrate_existing_attachments():
    """遷移現有附件到新路徑（選用）"""
    
    old_base = Path('/home/yjsclaw/.openclaw/workspace/daily_report_attachments')
    new_base = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments')
    
    if not old_base.exists():
        print("ℹ️  舊路徑不存在，跳過遷移")
        return
    
    print("\n📦 開始遷移現有附件...")
    
    migrated_count = 0
    for year_dir in old_base.iterdir():
        if not year_dir.is_dir():
            continue
        
        for date_dir in year_dir.iterdir():
            if not date_dir.is_dir():
                continue
            
            # 舊路徑：年份/日期/employee_id/時間戳/類型/
            # 新路徑：年份/日期/EMP-XXX_人名/時間戳/類型/
            
            for emp_id_dir in date_dir.iterdir():
                if not emp_id_dir.is_dir():
                    continue
                
                emp_id = emp_id_dir.name
                if emp_id in EMPLOYEE_CODES:
                    new_folder_name = get_employee_folder_name(emp_id)
                    new_path = date_dir.parent / date_dir.name / new_folder_name
                    
                    if not new_path.exists():
                        emp_id_dir.rename(new_path)
                        migrated_count += 1
                        print(f"  ✅ {emp_id} → {new_folder_name}")
    
    print(f"✅ 已遷移 {migrated_count} 個員工資料夾")


if __name__ == '__main__':
    # 1. 更新 users.json
    users = update_users_json()
    
    # 2. 測試新路徑產生
    print("\n📁 新路徑範例：")
    for emp_id in ['chen_ming_de', 'zhang_yi_chuan', 'li_ya_ting']:
        old_path = f"/home/yjsclaw/.openclaw/workspace/daily_report_attachments/2026/2026-03-01/{emp_id}/20260301_143022/photo/"
        new_path = get_attachment_path(emp_id, '2026-03-01') / "20260301_143022" / "photo"
        print(f"\n  {EMPLOYEE_NAMES.get(emp_id, emp_id)} ({EMPLOYEE_CODES.get(emp_id, 'N/A')})")
        print(f"  舊：{old_path}")
        print(f"  新：{new_path}")
    
    # 3. 遷移現有附件（選用）
    # migrate_existing_attachments()
    
    print("\n✅ 工號系統設定完成！")
    print("\n💡 使用說明：")
    print("  1. 系統內部仍使用 employee_id (chen_ming_de) 作為主鍵")
    print("  2. 顯示層面使用工號 + 中文人名 (EMP-003_陳明德)")
    print("  3. 附件路徑更直觀，方便人工查找")
