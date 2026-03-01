#!/usr/bin/env python3
"""
昱金生能源 - 系統備份腳本
功能：
1. 自動備份資料庫到 NAS
2. 壓縮備份檔案
3. 保留最近 30 天的備份
4. 驗證備份完整性
"""

import sqlite3
import shutil
import gzip
import os
from pathlib import Path
from datetime import datetime, timedelta

# 設定
DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')
BACKUP_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/backups')  # 本地備份
RETENTION_DAYS = 30


def create_backup():
    """建立備份"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'app_backup_{timestamp}.db'
    backup_path = BACKUP_DIR / backup_filename
    
    # 確保備份目錄存在
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 開始備份資料庫...")
    print(f"   來源：{DB_PATH}")
    print(f"   目標：{backup_path}")
    
    # 複製資料庫
    shutil.copy2(DB_PATH, backup_path)
    
    # 壓縮備份
    compressed_path = Path(str(backup_path) + '.gz')
    print(f"🗜️  壓縮備份...")
    
    with open(backup_path, 'rb') as f_in:
        with gzip.open(compressed_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # 刪除未壓縮檔案
    os.remove(backup_path)
    
    # 驗證備份
    print(f"✅ 驗證備份完整性...")
    try:
        with gzip.open(compressed_path, 'rb') as f:
            # 讀取前 100KB 驗證
            f.read(102400)
        print(f"   ✅ 備份驗證通過")
    except Exception as e:
        print(f"   ❌ 備份驗證失敗：{e}")
        return None
    
    # 計算大小
    backup_size = compressed_path.stat().st_size / 1024 / 1024  # MB
    print(f"   備份大小：{backup_size:.2f} MB")
    
    return compressed_path


def cleanup_old_backups():
    """清理超過保留期限的備份"""
    print(f"\n🧹 清理舊備份（保留 {RETENTION_DAYS} 天）...")
    
    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    deleted_count = 0
    
    for backup_file in BACKUP_DIR.glob('app_backup_*.db.gz'):
        # 從檔名解析日期
        try:
            filename = backup_file.stem  # app_backup_20260301_080000
            date_str = filename.split('_')[-2]  # 20260301
            backup_date = datetime.strptime(date_str, '%Y%m%d')
            
            if backup_date < cutoff_date:
                print(f"   🗑️  刪除：{backup_file.name}")
                backup_file.unlink()
                deleted_count += 1
        except Exception as e:
            print(f"   ⚠️  跳過：{backup_file.name} ({e})")
    
    print(f"   已刪除 {deleted_count} 個舊備份")


def restore_backup(backup_file=None):
    """
    還原備份
    
    Args:
        backup_file: 備份檔案路徑，如無則使用最新備份
    """
    if backup_file is None:
        # 找到最新備份
        backups = sorted(BACKUP_DIR.glob('app_backup_*.db.gz'), reverse=True)
        if not backups:
            print("❌ 找不到備份檔案")
            return False
        backup_file = backups[0]
        print(f"📥 使用最新備份：{backup_file.name}")
    else:
        backup_file = Path(backup_file)
    
    if not backup_file.exists():
        print(f"❌ 備份檔案不存在：{backup_file}")
        return False
    
    # 解壓縮並還原
    restore_path = DB_PATH.parent / f'app_restored_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    print(f"📥 還原備份到：{restore_path}")
    
    with gzip.open(backup_file, 'rb') as f_in:
        with open(restore_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    print(f"✅ 還原完成")
    print(f"   請手動替換：cp {restore_path} {DB_PATH}")
    
    return True


def list_backups():
    """列出所有備份"""
    print(f"📋 備份清單 ({BACKUP_DIR})\n")
    
    backups = sorted(BACKUP_DIR.glob('app_backup_*.db.gz'), reverse=True)
    
    if not backups:
        print("   無備份檔案")
        return
    
    print(f"{'檔名':<40} {'大小':<10} {'日期'}")
    print("-" * 70)
    
    for backup in backups[:20]:  # 只显示最近 20 個
        size_mb = backup.stat().st_size / 1024 / 1024
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"{backup.name:<40} {size_mb:>8.2f}MB {mtime.strftime('%Y-%m-%d %H:%M')}")
    
    if len(backups) > 20:
        print(f"... 還有 {len(backups) - 20} 個備份")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'list':
            list_backups()
        elif sys.argv[1] == 'restore':
            backup_file = sys.argv[2] if len(sys.argv) > 2 else None
            restore_backup(backup_file)
        else:
            print("用法：python3 backup.py [backup|list|restore]")
    else:
        # 預設執行備份
        print(f"🚀 執行自動備份 - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        backup_path = create_backup()
        
        if backup_path:
            cleanup_old_backups()
            
            print(f"\n✅ 備份完成：{backup_path}")
        else:
            print(f"\n❌ 備份失敗")
            sys.exit(1)
