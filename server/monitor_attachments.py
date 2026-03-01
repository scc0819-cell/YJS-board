#!/usr/bin/env python3
"""
昱金生能源集團 - 附件空間監控腳本

用途：監控附件目錄空間使用情況，產生報表
用法：python3 monitor_attachments.py [--alert]
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

ATTACHMENTS_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_attachments')
REPORT_FILE = Path('/tmp/attachments_monitor_report.json')

def get_dir_size(path):
    """計算目錄總大小（bytes）"""
    total = 0
    try:
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except Exception as e:
        print(f"⚠️  計算 {path} 大小時出錯：{e}")
    return total

def format_size(size_bytes):
    """格式化檔案大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def scan_attachments():
    """掃描附件目錄，產生統計報表"""
    
    if not ATTACHMENTS_DIR.exists():
        print("❌ 附件目錄不存在")
        return None
    
    report = {
        'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_size': 0,
        'total_files': 0,
        'by_year': {},
        'by_month': {},
        'by_employee': {},
        'large_files': [],
        'recent_uploads': []
    }
    
    # 依年份統計
    for year_dir in sorted(ATTACHMENTS_DIR.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        
        year = year_dir.name
        year_size = get_dir_size(year_dir)
        year_files = len(list(year_dir.rglob('*')))
        
        report['by_year'][year] = {
            'size': year_size,
            'size_formatted': format_size(year_size),
            'files': year_files
        }
        
        report['total_size'] += year_size
        report['total_files'] += year_files
        
        # 依月份統計（最近 6 個月）
        for month_dir in sorted(year_dir.iterdir()):
            if not month_dir.is_dir():
                continue
            
            # 解析日期
            try:
                date_obj = datetime.strptime(month_dir.name, '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
            except ValueError:
                continue
            
            if month_key not in report['by_month']:
                report['by_month'][month_key] = {'size': 0, 'files': 0}
            
            month_size = get_dir_size(month_dir)
            report['by_month'][month_key]['size'] += month_size
            report['by_month'][month_key]['files'] += len(list(month_dir.rglob('*')))
            
            # 依員工統計（最近 30 天）
            days_ago = (datetime.now() - date_obj).days
            if days_ago <= 30:
                for emp_dir in month_dir.iterdir():
                    if not emp_dir.is_dir():
                        continue
                    
                    emp_id = emp_dir.name
                    if emp_id not in report['by_employee']:
                        report['by_employee'][emp_id] = {'size': 0, 'files': 0}
                    
                    emp_size = get_dir_size(emp_dir)
                    report['by_employee'][emp_id]['size'] += emp_size
                    report['by_employee'][emp_id]['files'] += len(list(emp_dir.rglob('*')))
    
    # 找出大檔案（>10MB）
    for file_path in ATTACHMENTS_DIR.rglob('*'):
        if file_path.is_file():
            try:
                size = file_path.stat().st_size
                if size > 10 * 1024 * 1024:  # 10MB
                    report['large_files'].append({
                        'path': str(file_path.relative_to(ATTACHMENTS_DIR)),
                        'size': size,
                        'size_formatted': format_size(size)
                    })
            except Exception:
                pass
    
    # 排序大檔案
    report['large_files'].sort(key=lambda x: x['size'], reverse=True)
    report['large_files'] = report['large_files'][:20]  # 只保留前 20 個
    
    # 最近上傳（最近 7 天）
    seven_days_ago = datetime.now() - timedelta(days=7)
    for file_path in ATTACHMENTS_DIR.rglob('*'):
        if file_path.is_file():
            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime > seven_days_ago:
                    report['recent_uploads'].append({
                        'path': str(file_path.relative_to(ATTACHMENTS_DIR)),
                        'size': file_path.stat().st_size,
                        'time': mtime.strftime('%Y-%m-%d %H:%M:%S')
                    })
            except Exception:
                pass
    
    report['recent_uploads'].sort(key=lambda x: x['time'], reverse=True)
    report['recent_uploads'] = report['recent_uploads'][:50]  # 只保留最近 50 個
    
    return report

def print_report(report):
    """列印報表"""
    if not report:
        return
    
    print("=" * 70)
    print("📊 昱金生能源集團 - 附件空間監控報表")
    print("=" * 70)
    print(f"掃描時間：{report['scan_time']}")
    print()
    
    print(f"📦 總空間使用：{format_size(report['total_size'])}")
    print(f"📄 總檔案數：{report['total_files']:,}")
    print()
    
    print("📅 依年度統計:")
    for year, data in sorted(report['by_year'].items()):
        print(f"  {year}: {data['size_formatted']} ({data['files']:,} 個檔案)")
    print()
    
    print("📅 最近 6 個月統計:")
    for month, data in sorted(report['by_month'].items(), reverse=True)[:6]:
        print(f"  {month}: {format_size(data['size'])} ({data['files']:,} 個檔案)")
    print()
    
    print("👥 最近 30 天員工上傳統計:")
    sorted_emp = sorted(report['by_employee'].items(), key=lambda x: x[1]['size'], reverse=True)[:10]
    for emp_id, data in sorted_emp:
        print(f"  {emp_id}: {format_size(data['size'])} ({data['files']:,} 個檔案)")
    print()
    
    if report['large_files']:
        print("⚠️  大檔案 Top 10 (>10MB):")
        for i, f in enumerate(report['large_files'][:10], 1):
            print(f"  {i}. {f['path']} ({f['size_formatted']})")
        print()
    
    # 警告：空間成長過快
    months = list(report['by_month'].keys())
    if len(months) >= 2:
        recent_month = months[-1]
        prev_month = months[-2]
        recent_size = report['by_month'][recent_month]['size']
        prev_size = report['by_month'][prev_month]['size']
        
        if prev_size > 0:
            growth_rate = (recent_size - prev_size) / prev_size * 100
            if growth_rate > 50:
                print(f"🚨 警告：空間使用成長過快（{prev_month}→{recent_month}: +{growth_rate:.1f}%）")
            elif growth_rate > 20:
                print(f"⚠️  注意：空間使用成長（{prev_month}→{recent_month}: +{growth_rate:.1f}%）")

def check_alerts(report, threshold_gb=100):
    """檢查是否需要發出警告"""
    alerts = []
    
    total_gb = report['total_size'] / 1024 / 1024 / 1024
    if total_gb > threshold_gb:
        alerts.append(f"🚨 總空間超過 {threshold_gb}GB (目前：{total_gb:.2f}GB)")
    
    # 檢查大檔案數量
    if len(report['large_files']) > 50:
        alerts.append(f"⚠️  大檔案超過 50 個 (目前：{len(report['large_files'])}個)")
    
    # 檢查空間成長
    months = list(report['by_month'].keys())
    if len(months) >= 2:
        recent_size = report['by_month'][months[-1]]['size']
        prev_size = report['by_month'][months[-2]]['size']
        if prev_size > 0:
            growth_rate = (recent_size - prev_size) / prev_size * 100
            if growth_rate > 100:
                alerts.append(f"🚨 空間使用翻倍成長（+{growth_rate:.1f}%）")
    
    return alerts

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='附件空間監控')
    parser.add_argument('--alert', action='store_true', help='僅在需要警告時輸出')
    parser.add_argument('--json', action='store_true', help='輸出 JSON 格式')
    args = parser.parse_args()
    
    report = scan_attachments()
    
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        if args.alert:
            alerts = check_alerts(report)
            if alerts:
                for alert in alerts:
                    print(alert)
                sys.exit(1)
        else:
            print_report(report)
    
    # 儲存報表
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 報表已儲存：{REPORT_FILE}")
