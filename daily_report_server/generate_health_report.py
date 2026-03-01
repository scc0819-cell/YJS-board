#!/usr/bin/env python3
"""
生成每日健康報告
"""

import json
from pathlib import Path
from datetime import datetime

health_file = Path('/home/yjsclaw/.openclaw/workspace/daily_report_server/health_issues_log.json')
if health_file.exists():
    with open(health_file, 'r', encoding='utf-8') as f:
        log = json.load(f)
    
    report_file = Path('/home/yjsclaw/.openclaw/workspace/daily_report_server/weekly_health_report.json')
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_issues': len(log.get('issues', [])),
        'total_resolved': len(log.get('resolved', [])),
        'recent_issues': log.get('issues', [])[-10:],
        'recent_resolved': log.get('resolved', [])[-10:]
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已生成健康報告：{report_file}")
else:
    print("ℹ️  尚無健康檢查日誌")
