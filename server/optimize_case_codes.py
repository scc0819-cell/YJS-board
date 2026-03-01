#!/usr/bin/env python3
"""
改善 A（續）：優化案場代碼 + 更新日報表單為下拉選單
"""

import sqlite3
from pathlib import Path

DB_PATH = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/data/app.db')

def optimize_case_codes():
    """優化案場代碼，使其更有意義"""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 手動修正幾個重要的案場代碼
    updates = [
        ('陸豐國小', 'LF-GF'),
        ('媽厝國小', 'MC-GF'),
        ('萬合國小', 'WH-GF'),
        ('長安國小', 'CA-GF'),
        ('線西國小 H 區', 'XX-GF'),
        ('伸東國小', 'SD-GF'),
        ('鹿東國小二校區', 'LD-GF'),
        ('台積電 PPA 綠電轉供', 'TSMC-PPA'),
        ('永豐銀行融資展延', 'ESUN-FIN'),
        ('其他/行政事務', 'ADMIN-XX'),
    ]
    
    print("📝 優化案場代碼...")
    for name, code in updates:
        conn.execute("UPDATE cases SET case_code = ? WHERE name = ?", (code, name))
        print(f"  ✓ {name} → {code}")
    
    conn.commit()
    conn.close()
    print("\n✅ 案場代碼優化完成！")

if __name__ == '__main__':
    optimize_case_codes()
