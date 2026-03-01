#!/usr/bin/env python3
"""
昱金生能源 - 附件管理腳本
功能：查看、統計、清理附件
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys

ATTACHMENTS_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments')
DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

def scan_attachments():
    """掃描附件目錄，返回統計資訊"""
    
    if not ATTACHMENTS_DIR.exists():
        print("❌ 附件目錄不存在")
        return {}
    
    stats = {
        'total_files': 0,
        'total_size': 0,
        'by_year': {},
        'by_employee': {},
        'by_type': {}
    }
    
    # 掃描年份目錄
    for year_dir in ATTACHMENTS_DIR.iterdir():
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        
        year = year_dir.name
        year_stats = {'files': 0, 'size': 0, 'employees': {}}
        
        # 掃描員工目錄
        for emp_dir in year_dir.iterdir():
            if not emp_dir.is_dir():
                continue
            
            emp_name = emp_dir.name
            emp_stats = {'files': 0, 'size': 0, 'dates': {}}
            
            # 掃描日期目錄
            for date_dir in emp_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                
                date = date_dir.name
                
                # 掃描類型目錄
                for type_dir in date_dir.iterdir():
                    if not type_dir.is_dir():
                        continue
                    
                    file_type = type_dir.name
                    
                    # 統計檔案
                    for file_path in type_dir.glob('*'):
                        if file_path.is_file():
                            size = file_path.stat().st_size
                            
                            stats['total_files'] += 1
                            stats['total_size'] += size
                            
                            year_stats['files'] += 1
                            year_stats['size'] += size
                            
                            emp_stats['files'] += 1
                            emp_stats['size'] += size
                            
                            # 類型統計
                            if file_type not in stats['by_type']:
                                stats['by_type'][file_type] = {'files': 0, 'size': 0}
                            stats['by_type'][file_type]['files'] += 1
                            stats['by_type'][file_type]['size'] += size
            
            emp_dir_name = emp_name
            year_stats['employees'][emp_dir_name] = emp_stats
            
            # 員工統計
            if emp_name not in stats['by_employee']:
                stats['by_employee'][emp_name] = {'files': 0, 'size': 0, 'years': {}}
            stats['by_employee'][emp_name]['files'] += emp_stats['files']
            stats['by_employee'][emp_name]['size'] += emp_stats['size']
            stats['by_employee'][emp_name]['years'][year] = emp_stats['files']
        
        stats['by_year'][year] = year_stats
    
    return stats


def format_size(size_bytes):
    """格式化檔案大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def print_report(stats):
    """列印統計報告"""
    
    print("\n📊 昱金生能源 - 附件統計報告")
    print("=" * 60)
    print(f"掃描目錄：{ATTACHMENTS_DIR}")
    print(f"報告時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 總計
    print(f"\n📦 總計：")
    print(f"  檔案總數：{stats['total_files']:,}")
    print(f"  總大小：{format_size(stats['total_size'])}")
    
    # 依年份統計
    print(f"\n📅 依年份統計：")
    for year in sorted(stats['by_year'].keys()):
        year_data = stats['by_year'][year]
        print(f"  {year}: {year_data['files']:,} 檔案，{format_size(year_data['size'])}")
        print(f"    員工人數：{len(year_data['employees'])}")
    
    # 依員工統計
    print(f"\n👥 依員工統計：")
    sorted_employees = sorted(stats['by_employee'].items(), 
                            key=lambda x: x[1]['files'], reverse=True)
    
    for emp_name, emp_data in sorted_employees:
        print(f"  {emp_name}: {emp_data['files']:,} 檔案，{format_size(emp_data['size'])}")
        
        # 顯示各年份分佈
        years_str = ', '.join([f"{y}:{c}" for y, c in emp_data['years'].items()])
        print(f"    年份分佈：{years_str}")
    
    # 依類型統計
    print(f"\n📁 依類型統計：")
    sorted_types = sorted(stats['by_type'].items(), 
                         key=lambda x: x[1]['files'], reverse=True)
    
    for file_type, type_data in sorted_types:
        print(f"  {file_type}: {type_data['files']:,} 檔案，{format_size(type_data['size'])}")
    
    print("\n" + "=" * 60)


def print_employee_detail(employee_name):
    """列印特定員工的附件詳情"""
    
    stats = scan_attachments()
    
    if employee_name not in stats['by_employee']:
        print(f"❌ 找不到員工：{employee_name}")
        return
    
    emp_data = stats['by_employee'][employee_name]
    
    print(f"\n📊 {employee_name} - 附件詳情")
    print("=" * 60)
    print(f"總檔案數：{emp_data['files']:,}")
    print(f"總大小：{format_size(emp_data['size'])}")
    
    print(f"\n📅 年份分佈：")
    for year in sorted(emp_data['years'].keys()):
        count = emp_data['years'][year]
        print(f"  {year}: {count:,} 檔案")
    
    # 詳細檔案清單
    print(f"\n📁 檔案清單：")
    emp_folder = f"{employee_name.split('_')[0]}_{employee_name.split('_')[1]}"
    
    for year_dir in ATTACHMENTS_DIR.iterdir():
        if not year_dir.is_dir():
            continue
        
        emp_dir = year_dir / emp_folder
        if not emp_dir.exists():
            continue
        
        print(f"\n  {year_dir.name}/")
        for date_dir in emp_dir.iterdir():
            if not date_dir.is_dir():
                continue
            
            print(f"    {date_dir.name}/")
            for type_dir in date_dir.iterdir():
                if not type_dir.is_dir():
                    continue
                
                files = list(type_dir.glob('*'))
                if files:
                    print(f"      {type_dir.name}/ ({len(files)} 檔案)")
                    for f in files[:5]:  # 只顯示前 5 個
                        size = f.stat().st_size
                        print(f"        - {f.name} ({format_size(size)})")
                    
                    if len(files) > 5:
                        print(f"        ... 還有 {len(files) - 5} 個檔案")


def cleanup_old_files(days=365):
    """清理超過指定天數的檔案（慎用！）"""
    
    print(f"⚠️  警告：此操作將刪除 {days} 天前的檔案")
    print("請確認後輸入 'YES' 繼續：", end='')
    
    confirm = input()
    if confirm != 'YES':
        print("❌ 已取消")
        return
    
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    deleted_count = 0
    deleted_size = 0
    
    for file_path in ATTACHMENTS_DIR.rglob('*'):
        if file_path.is_file():
            mtime = file_path.stat().st_mtime
            if mtime < cutoff:
                size = file_path.stat().st_size
                try:
                    file_path.unlink()
                    deleted_count += 1
                    deleted_size += size
                    print(f"  🗑️  刪除：{file_path}")
                except Exception as e:
                    print(f"  ❌ 失敗：{file_path} - {e}")
    
    print(f"\n✅ 清理完成")
    print(f"  刪除檔案數：{deleted_count:,}")
    print(f"  釋放空間：{format_size(deleted_size)}")


def main():
    if len(sys.argv) < 2:
        print("📊 昱金生能源 - 附件管理腳本")
        print("用法：")
        print("  python3 manage_attachments.py scan          # 掃描並顯示統計")
        print("  python3 manage_attachments.py employee <名稱> # 查看員工詳情")
        print("  python3 manage_attachments.py cleanup <天數>  # 清理舊檔案（慎用！）")
        print("")
        return
    
    command = sys.argv[1]
    
    if command == 'scan':
        stats = scan_attachments()
        print_report(stats)
    
    elif command == 'employee' and len(sys.argv) > 2:
        employee_name = sys.argv[2]
        print_employee_detail(employee_name)
    
    elif command == 'cleanup' and len(sys.argv) > 2:
        days = int(sys.argv[2])
        cleanup_old_files(days)
    
    else:
        print(f"❌ 未知命令：{command}")


if __name__ == '__main__':
    main()
