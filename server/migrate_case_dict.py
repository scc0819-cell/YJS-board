#!/usr/bin/env python3
"""
改善 A：案場字典/命名一致化
1. 建立標準案場代碼
2. 增加同義詞管理
3. 日報表單改為下拉選單（禁止自由輸入）
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

def migrate_case_catalog():
    """升級案場表結構，增加代碼和同義詞欄位"""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 1. 檢查是否已有 case_code 欄位
    cursor = conn.execute("PRAGMA table_info(cases)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'case_code' not in columns:
        print("📋 增加 case_code 欄位...")
        conn.execute("ALTER TABLE cases ADD COLUMN case_code TEXT")
        
    if 'aliases' not in columns:
        print("📋 增加 aliases 欄位（同義詞，JSON 格式）...")
        conn.execute("ALTER TABLE cases ADD COLUMN aliases TEXT")
    
    # 2. 為現有案場產生代碼
    cursor = conn.execute("SELECT case_id, name, case_code FROM cases WHERE case_code IS NULL")
    cases_to_update = cursor.fetchall()
    
    print(f"\n📝 將為 {len(cases_to_update)} 個案場產生代碼...")
    
    for case in cases_to_update:
        case_id = case['case_id']
        name = case['name']
        
        # 產生代碼：取名稱前兩個字 + 類型縮寫
        # 例：仁豐國小屋頂型 → RF-GF
        # 例：彰化停車場 → CH-PC
        
        # 簡單規則：取中文名稱前 2-3 個字的拼音首字母
        # 這裡先用簡單映射，後續可優化
        code_map = {
            '仁豐': 'RF', '馬偕': 'MK', '彰化': 'CH', '北斗': 'BD',
            '溪湖': 'XH', '二林': 'EL', '芳苑': 'FY', '大城': 'DC',
            '竹塘': 'ZT', '埤頭': 'PT', '鹿港': 'LG', '和美': 'HM',
            '線西': 'XX', '伸港': 'SG', '福興': 'FX', '秀水': 'SS',
            '花壇': 'HT', '芬園': 'FY', '員林': 'YL', '社頭': 'ST',
            '永靖': 'YJ', '田尾': 'TW', '田中': 'TZ', '大村': 'DC',
            '埔鹽': 'PY', '埔心': 'PX', '溪州': 'XZ', '二水': 'ES',
            '名間': 'MJ', '集集': 'JJ', '水里': 'SL', '信義': 'XY',
            '魚池': 'YC', '國姓': 'GX', '埔里': 'PL', '仁愛': 'RA',
        }
        
        # 從名稱中提取關鍵字
        code_prefix = 'XX'  # 預設
        for key, code in code_map.items():
            if key in name:
                code_prefix = code
                break
        
        # 判斷類型
        type_suffix = 'GF'  # 預設屋頂型
        if '停車場' in name or '停車' in name:
            type_suffix = 'PC'
        elif '球場' in name or '風雨' in name:
            type_suffix = 'BC'
        elif '地面' in name:
            type_suffix = 'GM'
        elif '立面' in name:
            type_suffix = 'LM'
        
        case_code = f"{code_prefix}-{type_suffix}"
        
        # 檢查是否重複，若重複則加序號
        cursor2 = conn.execute("SELECT case_code FROM cases WHERE case_code = ?", (case_code,))
        if cursor2.fetchone():
            # 已有相同代碼，加序號
            cursor3 = conn.execute("SELECT COUNT(*) as cnt FROM cases WHERE case_code LIKE ?", (f"{case_code}-%",))
            cnt = cursor3.fetchone()['cnt'] + 1
            case_code = f"{case_code}-{cnt:02d}"
        
        conn.execute("""
            UPDATE cases 
            SET case_code = ?, aliases = ?
            WHERE case_id = ?
        """, (case_code, '[]', case_id))
        
        print(f"  ✓ {name} → {case_code}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 案場字典升級完成！")

if __name__ == '__main__':
    migrate_case_catalog()
