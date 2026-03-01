#!/usr/bin/env python3
"""
昱金生能源 - 匯入案場資料到 SQLite
將郵件解析產生的案場資料庫匯入到 app.db
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路徑設定
CASE_DB_FILE = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/full_email_analysis/case_database_from_emails.json')
APP_DB = Path('/home/yjsclaw/.openclaw/workspace/daily_report_server/data/app.db')

def load_case_database():
    """載入案場資料庫"""
    if not CASE_DB_FILE.exists():
        logger.error(f"案場資料庫不存在：{CASE_DB_FILE}")
        return None
    
    with open(CASE_DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"載入 {data.get('total_cases', 0)} 個案場")
    return data.get('cases', {})

def create_tables(conn):
    """建立資料表（如果不存在）"""
    c = conn.cursor()
    
    # cases 表
    c.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT UNIQUE NOT NULL,
            case_name TEXT,
            case_type TEXT,
            location TEXT,
            capacity_kw REAL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # case_status 表
    c.execute('''
        CREATE TABLE IF NOT EXISTS case_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            report_count INTEGER DEFAULT 0,
            email_count INTEGER DEFAULT 0,
            first_report DATE,
            last_report DATE,
            has_attachments INTEGER DEFAULT 0,
            employees TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (case_id) REFERENCES cases(case_id)
        )
    ''')
    
    conn.commit()
    logger.info("資料表已建立/確認")

def import_cases(conn, case_db):
    """匯入案場資料"""
    c = conn.cursor()
    
    imported = 0
    updated = 0
    
    for case_id, data in case_db.items():
        try:
            # 插入或更新 cases 表
            c.execute('''
                INSERT OR REPLACE INTO cases (case_id, name, type, enabled, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                case_id,
                data.get('case_name', '未知') or '未知',
                'unknown',
                1,
                datetime.now().isoformat()
            ))
            
            # 插入或更新 case_status 表（如果存在）
            employees = ','.join(data.get('employees', []))
            try:
                c.execute('''
                    INSERT INTO case_status (case_id, report_count, email_count, first_report, last_report, has_attachments, employees, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(case_id) DO UPDATE SET
                        report_count = excluded.report_count,
                        email_count = excluded.email_count,
                        first_report = excluded.first_report,
                        last_report = excluded.last_report,
                        has_attachments = excluded.has_attachments,
                        employees = excluded.employees,
                        updated_at = excluded.updated_at
                ''', (
                    case_id,
                    len(data.get('reports', [])),
                    data.get('email_count', 0),
                    data.get('first_report'),
                    data.get('last_report'),
                    data.get('has_attachments', 0),
                    employees,
                    datetime.now().isoformat()
                ))
            except sqlite3.OperationalError:
                # case_status 表可能不存在，跳過
                pass
            
            if c.rowcount > 0:
                updated += 1
            imported += 1
            
        except Exception as e:
            logger.error(f"匯入 {case_id} 失敗：{e}")
            continue
    
    conn.commit()
    logger.info(f"匯入完成：{imported} 個案場，{updated} 個更新")
    return imported

def main():
    logger.info("=" * 70)
    logger.info("🚀 昱金生能源 - 案場資料匯入")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 載入案場資料庫
    case_db = load_case_database()
    if not case_db:
        return
    
    # 連接資料庫
    conn = sqlite3.connect(APP_DB)
    
    try:
        # 建立資料表
        create_tables(conn)
        
        # 匯入資料
        imported = import_cases(conn, case_db)
        
        # 驗證
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM cases')
        case_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM case_status')
        status_count = c.fetchone()[0]
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 匯入總結")
        logger.info("=" * 70)
        logger.info(f"cases 表：{case_count} 筆")
        logger.info(f"case_status 表：{status_count} 筆")
        logger.info("=" * 70)
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()
