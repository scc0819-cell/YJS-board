#!/usr/bin/env python3
"""
昱金生能源 - 電廠監控自動化
每日執行：檢查案場異常、生成摘要、發送告警
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
import logging
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路徑設定
WORKSPACE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
OUTPUT_DIR = WORKSPACE_DIR / 'daily_report_attachments' / 'plant_monitoring'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 監控規則（根據實際需求調整）
MONITORING_RULES = {
    'generation_drop': {
        'name': '發電量異常下降',
        'threshold': 0.3,  # 下降超過 30%
        'severity': 'high'
    },
    'inverter_fault': {
        'name': '逆變器故障',
        'threshold': 1,  # 任何故障
        'severity': 'critical'
    },
    'communication_loss': {
        'name': '通訊中斷',
        'threshold': 30,  # 中斷超過 30 分鐘
        'severity': 'medium'
    },
    'efficiency_low': {
        'name': '系統效率過低',
        'threshold': 0.6,  # PR 低於 60%
        'severity': 'medium'
    }
}

def load_case_database():
    """載入案場資料庫"""
    db_path = WORKSPACE_DIR / 'daily_report_server' / 'data' / 'case_database_from_emails.json'
    if db_path.exists():
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def simulate_plant_data(cases):
    """
    模擬案場數據（待替換為真實 API 串接）
    TODO: 串接 AUO 真實數據源
    """
    import random
    
    simulated_data = []
    for case in cases[:20]:  # 先測試前 20 個案場
        data = {
            'case_id': case.get('case_id', case.get('id', 'UNKNOWN')),
            'case_name': case.get('case_name', '未知案場'),
            'timestamp': datetime.now().isoformat(),
            'current_power_kw': random.uniform(50, 500),
            'daily_energy_kwh': random.uniform(200, 2000),
            'pr_value': random.uniform(0.65, 0.85),
            'inverter_status': random.choice(['normal', 'normal', 'normal', 'warning', 'fault']),
            'communication_status': random.choice(['online', 'online', 'online', 'offline']),
            'alerts': []
        }
        
        # 根據規則檢查異常
        if data['pr_value'] < MONITORING_RULES['efficiency_low']['threshold']:
            data['alerts'].append({
                'rule': 'efficiency_low',
                'message': f"系統效率 {data['pr_value']:.1%} 低於標準",
                'severity': MONITORING_RULES['efficiency_low']['severity']
            })
        
        if data['inverter_status'] == 'fault':
            data['alerts'].append({
                'rule': 'inverter_fault',
                'message': '逆變器故障',
                'severity': MONITORING_RULES['inverter_fault']['severity']
            })
        
        if data['communication_status'] == 'offline':
            data['alerts'].append({
                'rule': 'communication_loss',
                'message': '通訊中斷',
                'severity': MONITORING_RULES['communication_loss']['severity']
            })
        
        simulated_data.append(data)
    
    return simulated_data

def generate_daily_summary(monitoring_data):
    """生成每日監控摘要"""
    summary = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_cases': len(monitoring_data),
        'normal_cases': 0,
        'warning_cases': 0,
        'critical_cases': 0,
        'alerts_by_type': defaultdict(int),
        'alerts': []
    }
    
    for data in monitoring_data:
        if not data['alerts']:
            summary['normal_cases'] += 1
        else:
            has_critical = False
            for alert in data['alerts']:
                summary['alerts_by_type'][alert['rule']] += 1
                summary['alerts'].append({
                    'case_id': data['case_id'],
                    'case_name': data['case_name'],
                    **alert
                })
                if alert['severity'] == 'critical':
                    has_critical = True
            
            if has_critical:
                summary['critical_cases'] += 1
            else:
                summary['warning_cases'] += 1
    
    return summary

def generate_report(monitoring_data, summary):
    """生成監控報告（Markdown + JSON）"""
    report_md = f"""# 🏭 電廠監控日報

**日期**: {summary['date']}
**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 總覽

| 指標 | 數值 | 狀態 |
|------|------|------|
| 監控案場數 | {summary['total_cases']} | - |
| 正常運行 | {summary['normal_cases']} | ✅ |
| 警告 | {summary['warning_cases']} | ⚠️ |
| 嚴重異常 | {summary['critical_cases']} | 🚨 |

---

## 🚨 異常告警

"""
    
    if summary['alerts']:
        # 按嚴重性排序
        sorted_alerts = sorted(summary['alerts'], key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x['severity'], 4))
        
        for alert in sorted_alerts[:20]:  # 最多顯示 20 筆
            severity_icon = {'critical': '🚨', 'high': '⚠️', 'medium': '⚡', 'low': 'ℹ️'}.get(alert['severity'], '•')
            report_md += f"{severity_icon} **{alert['case_name']}** ({alert['case_id']})\n"
            report_md += f"   - {alert['message']}\n"
            report_md += f"   - 嚴重性：{alert['severity']}\n\n"
    else:
        report_md += "✅ 今日無異常告警\n\n"
    
    report_md += """
---

## 📈 異常統計

| 異常類型 | 數量 |
|----------|------|
"""
    
    for rule_key, count in summary['alerts_by_type'].items():
        rule_name = MONITORING_RULES.get(rule_key, {}).get('name', rule_key)
        report_md += f"| {rule_name} | {count} |\n"
    
    report_md += f"""
---

## 💡 建議行動

"""
    
    if summary['critical_cases'] > 0:
        report_md += f"1. 🚨 **立即處理** {summary['critical_cases']} 個嚴重異常案場\n"
    if summary['warning_cases'] > 0:
        report_md += f"2. ⚠️ **追蹤檢查** {summary['warning_cases']} 個警告案場\n"
    if summary['alerts_by_type'].get('communication_loss', 0) > 0:
        report_md += "3. 📡 **檢查通訊設備** - 多個案場通訊中斷\n"
    if summary['alerts_by_type'].get('efficiency_low', 0) > 0:
        report_md += "4. 🔍 **檢查系統效率** - PR 值低於標準\n"
    
    report_md += f"""
---

**下次更新**: 明日 08:00
**數據來源**: 模擬數據（待串接 AUO 真實 API）
"""
    
    return report_md

def save_reports(monitoring_data, summary, report_md):
    """儲存報告檔案"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 儲存 Markdown 報告
    md_path = OUTPUT_DIR / f'plant_monitoring_{timestamp}.md'
    md_path.write_text(report_md, encoding='utf-8')
    logger.info(f"📄 已儲存 Markdown 報告：{md_path}")
    
    # 儲存 JSON 數據
    json_path = OUTPUT_DIR / f'plant_monitoring_{timestamp}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'monitoring_data': monitoring_data,
            'summary': summary
        }, f, ensure_ascii=False, indent=2)
    logger.info(f"📊 已儲存 JSON 數據：{json_path}")
    
    # 更新最新報告（方便讀取）
    latest_md = OUTPUT_DIR / 'plant_monitoring_latest.md'
    latest_md.write_text(report_md, encoding='utf-8')
    latest_json = OUTPUT_DIR / 'plant_monitoring_latest.json'
    with open(latest_json, 'w', encoding='utf-8') as f:
        json.dump({
            'monitoring_data': monitoring_data,
            'summary': summary
        }, f, ensure_ascii=False, indent=2)
    logger.info("📄 已更新最新報告")

def main():
    logger.info("=" * 70)
    logger.info("🏭 昱金生能源 - 電廠監控自動化")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 載入案場資料庫
    cases = load_case_database()
    logger.info(f"📚 載入 {len(cases)} 個案場")
    
    if not cases:
        logger.warning("沒有案場資料，跳過監控")
        return
    
    # 模擬監控數據（TODO: 替換為真實 API）
    monitoring_data = simulate_plant_data(cases)
    logger.info(f"📊 生成 {len(monitoring_data)} 筆監控數據")
    
    # 生成摘要
    summary = generate_daily_summary(monitoring_data)
    logger.info(f"📈 生成摘要：正常={summary['normal_cases']}, 警告={summary['warning_cases']}, 嚴重={summary['critical_cases']}")
    
    # 生成報告
    report_md = generate_report(monitoring_data, summary)
    
    # 儲存報告
    save_reports(monitoring_data, summary, report_md)
    
    # 輸出總結
    logger.info("\n" + "=" * 70)
    logger.info("✅ 電廠監控完成！")
    logger.info("=" * 70)
    logger.info(f"監控案場：{summary['total_cases']} | "
                f"正常：{summary['normal_cases']} | "
                f"警告：{summary['warning_cases']} | "
                f"嚴重：{summary['critical_cases']}")
    
    # 如果有嚴重異常，發送通知（TODO: 整合通知系統）
    if summary['critical_cases'] > 0:
        logger.warning(f"🚨 發現 {summary['critical_cases']} 個嚴重異常案場！")
        # TODO: 發送 LINE/Email 通知

if __name__ == '__main__':
    main()
