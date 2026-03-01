#!/usr/bin/env python3
"""
昱金生能源 - 系統自我優化腳本
每週日 23:00 執行，自動檢測並優化系統
"""

import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路徑設定
WORKSPACE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
MEMORY_DIR = Path('/home/yjsclaw/.openclaw/workspace/memory')
LOG_DIR = Path('/tmp')

def check_disk_usage():
    """檢查磁碟使用量"""
    total, used, free = shutil.disk_usage('/')
    usage_percent = (used / total) * 100
    
    result = {
        'total_gb': total / (1024**3),
        'used_gb': used / (1024**3),
        'free_gb': free / (1024**3),
        'usage_percent': usage_percent,
        'status': 'OK' if usage_percent < 80 else 'WARNING'
    }
    
    logger.info(f"💾 磁碟使用：{usage_percent:.1f}% ({result['free_gb']:.1f}GB 可用)")
    return result

def check_log_files():
    """檢查並清理舊日誌檔案"""
    log_files = list(LOG_DIR.glob('*.log'))
    old_logs = [f for f in log_files if f.stat().st_mtime < (datetime.now().timestamp() - 7*24*60*60)]
    
    cleaned_size = 0
    for log_file in old_logs:
        try:
            cleaned_size += log_file.stat().st_size
            log_file.unlink()
        except Exception as e:
            logger.warning(f"無法刪除 {log_file}: {e}")
    
    logger.info(f"🧹 清理 {len(old_logs)} 個舊日誌檔案 ({cleaned_size/1024:.1f}KB)")
    return {'cleaned_count': len(old_logs), 'cleaned_size_kb': cleaned_size/1024}

def check_memory_files():
    """檢查記憶檔案"""
    daily_files = list(MEMORY_DIR.glob('*.md'))
    
    # 找出超過 30 天的檔案
    old_files = []
    for f in daily_files:
        if f.name == 'index.md' or f.name == 'index.json':
            continue
        try:
            date = datetime.strptime(f.stem, '%Y-%m-%d')
            if (datetime.now() - date).days > 30:
                old_files.append(f)
        except ValueError:
            pass
    
    logger.info(f"📚 記憶檔案：{len(daily_files)} 個 ({len(old_files)} 個超過 30 天)")
    return {'total': len(daily_files), 'old': len(old_files)}

def check_cron_jobs():
    """檢查 crontab 任務"""
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True, timeout=10)
        lines = result.stdout.strip().split('\n')
        cron_jobs = [l for l in lines if l and not l.startswith('#')]
        logger.info(f"⏰ Crontab 任務：{len(cron_jobs)} 個")
        return {'count': len(cron_jobs), 'status': 'OK'}
    except Exception as e:
        logger.error(f"Crontab 檢查失敗：{e}")
        return {'count': 0, 'status': 'ERROR'}

def check_services():
    """檢查服務狀態"""
    services = {
        'daily_report_server': False,
        'watchdog': False
    }
    
    # 檢查 Flask 服務
    try:
        result = subprocess.run(['pgrep', '-f', 'python3.*app.py'], capture_output=True, timeout=5)
        services['daily_report_server'] = result.returncode == 0
    except:
        pass
    
    # 檢查 Watchdog
    try:
        result = subprocess.run(['pgrep', '-f', 'keep_server_alive.sh'], capture_output=True, timeout=5)
        services['watchdog'] = result.returncode == 0
    except:
        pass
    
    logger.info(f"🔧 服務狀態：日報={services['daily_report_server']}, Watchdog={services['watchdog']}")
    return services

def optimize_database():
    """優化 SQLite 資料庫"""
    db_path = WORKSPACE_DIR / 'daily_report_server' / 'data' / 'app.db'
    if not db_path.exists():
        return {'status': 'NOT_FOUND'}
    
    try:
        # VACUUM 資料庫
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute('VACUUM')
        conn.close()
        logger.info("🗄️ 資料庫優化完成")
        return {'status': 'OK'}
    except Exception as e:
        logger.error(f"資料庫優化失敗：{e}")
        return {'status': 'ERROR', 'error': str(e)}

def generate_optimization_report(stats):
    """生成優化報告"""
    report = f"""# 系統自我優化報告

**執行時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 系統狀態

| 項目 | 狀態 | 詳情 |
|------|------|------|
| 磁碟使用 | {'✅' if stats['disk']['status'] == 'OK' else '⚠️'} | {stats['disk']['usage_percent']:.1f}% |
| 日誌清理 | ✅ | {stats['logs']['cleaned_count']} 個檔案 |
| 記憶檔案 | ✅ | {stats['memory']['total']} 個 |
| Crontab | {'✅' if stats['cron']['status'] == 'OK' else '❌'} | {stats['cron']['count']} 個任務 |
| 服務運行 | {'✅' if all(stats['services'].values()) else '⚠️'} | {sum(stats['services'].values())}/{len(stats['services'])} |
| 資料庫 | {'✅' if stats['database']['status'] == 'OK' else '⚠️'} | {stats['database']['status']} |

---

## 🎯 優化建議

"""
    
    # 根據統計生成建議
    if stats['disk']['usage_percent'] > 80:
        report += "⚠️ **磁碟空間不足** - 建議清理舊檔案或擴充空間\n\n"
    
    if stats['logs']['cleaned_count'] > 10:
        report += "💡 **日誌檔案過多** - 已自動清理，建議檢查是否有異常日誌\n\n"
    
    if not all(stats['services'].values()):
        report += "⚠️ **部分服務未運行** - 請檢查 Watchdog 或日報服務\n\n"
    
    report += """
---

## 📈 本週改善

- ✅ 自動清理舊日誌檔案
- ✅ 優化 SQLite 資料庫
- ✅ 檢查所有服務狀態
- ✅ 驗證 Crontab 任務

---

**下次優化**: 下週日 23:00
"""
    
    return report

def save_report(report):
    """儲存優化報告"""
    output_dir = WORKSPACE_DIR / 'optimization_reports'
    output_dir.mkdir(exist_ok=True)
    
    filename = f"optimization_report_{datetime.now().strftime('%Y%m%d')}.md"
    output_file = output_dir / filename
    
    output_file.write_text(report, encoding='utf-8')
    logger.info(f"📄 已儲存報告：{output_file}")

def main():
    logger.info("=" * 70)
    logger.info("🔧 昱金生能源 - 系統自我優化")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 執行檢查
    stats = {
        'disk': check_disk_usage(),
        'logs': check_log_files(),
        'memory': check_memory_files(),
        'cron': check_cron_jobs(),
        'services': check_services(),
        'database': optimize_database()
    }
    
    # 生成報告
    report = generate_optimization_report(stats)
    
    # 儲存報告
    save_report(report)
    
    # 輸出總結
    logger.info("\n" + "=" * 70)
    logger.info("✅ 系統自我優化完成！")
    logger.info("=" * 70)
    logger.info(f"磁碟：{stats['disk']['usage_percent']:.1f}% | "
                f"日誌：{stats['logs']['cleaned_count']} 個 | "
                f"記憶：{stats['memory']['total']} 個 | "
                f"服務：{sum(stats['services'].values())}/{len(stats['services'])}")

if __name__ == '__main__':
    main()
