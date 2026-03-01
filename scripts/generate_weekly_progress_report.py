#!/usr/bin/env python3
"""
昱金生能源 - 每週進度報告
每週一 09:30 執行，彙整 B+C 任務執行結果
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 路徑設定
WORKSPACE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
ATTACHMENTS_DIR = WORKSPACE_DIR / 'daily_report_attachments'

def get_last_week_dates():
    """取得上週的日期範圍"""
    today = datetime.now()
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    return last_monday, last_sunday

def scan_plant_monitoring_reports(start_date, end_date):
    """掃描電廠監控報告"""
    reports = []
    monitoring_dir = ATTACHMENTS_DIR / 'plant_monitoring'
    
    if monitoring_dir.exists():
        for file in monitoring_dir.glob('plant_monitoring_*.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    summary = data.get('summary', {})
                    reports.append({
                        'date': summary.get('date', file.stem),
                        'total_cases': summary.get('total_cases', 0),
                        'normal_cases': summary.get('normal_cases', 0),
                        'warning_cases': summary.get('warning_cases', 0),
                        'critical_cases': summary.get('critical_cases', 0),
                        'alerts_count': len(summary.get('alerts', []))
                    })
            except Exception as e:
                logger.warning(f"讀取報告失敗 {file}: {e}")
    
    logger.info(f"🏭 掃描到 {len(reports)} 筆電廠監控報告")
    return reports

def scan_case_optimization_reports(start_date, end_date):
    """掃描案場名稱優化報告"""
    reports = []
    optimization_dir = ATTACHMENTS_DIR / 'case_name_optimization'
    
    if optimization_dir.exists():
        latest_report = optimization_dir / 'case_optimization_latest.md'
        if latest_report.exists():
            content = latest_report.read_text(encoding='utf-8')
            
            # 提取統計數據
            import re
            total_match = re.search(r'總案場數 \| (\d+)', content)
            with_names_match = re.search(r'有完整名稱 \| (\d+)', content)
            
            reports.append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_cases': int(total_match.group(1)) if total_match else 0,
                'with_names': int(with_names_match.group(1)) if with_names_match else 0,
                'coverage': 0
            })
            
            if reports[0]['total_cases'] > 0:
                reports[0]['coverage'] = reports[0]['with_names'] / reports[0]['total_cases'] * 100
    
    logger.info(f"🏭 掃描到 {len(reports)} 筆案場優化報告")
    return reports

def generate_progress_report(plant_reports, case_reports):
    """生成進度報告"""
    report_md = f"""# 📈 每週進度報告

**報告期間**: {datetime.now().strftime('%Y-%m-%d')}
**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🎯 任務 B：電廠監控系統

### 本週執行統計

| 指標 | 數值 | 狀態 |
|------|------|------|
| 執行次數 | {len(plant_reports)} | {'✅ 每日執行' if len(plant_reports) >= 5 else '⚠️ 執行不足'} |
| 監控案場數 | {plant_reports[0]['total_cases'] if plant_reports else 0} | {'✅ 正常' if plant_reports else '⚠️ 無數據'} |
| 平均異常數 | {sum(r['alerts_count'] for r in plant_reports) / len(plant_reports) if plant_reports else 0:.1f} | - |

### 異常趨勢

"""
    
    if plant_reports:
        total_critical = sum(r['critical_cases'] for r in plant_reports)
        total_warning = sum(r['warning_cases'] for r in plant_reports)
        
        report_md += f"""| 異常類型 | 本週總數 | 平均每日 |
|----------|----------|----------|
| 🚨 嚴重異常 | {total_critical} | {total_critical/len(plant_reports):.1f} |
| ⚠️ 警告 | {total_warning} | {total_warning/len(plant_reports):.1f} |

"""
    
    report_md += """### 建議行動

- [ ] 串接 AUO 真實數據源（目前為模擬數據）
- [ ] 建立告警通知機制（LINE/Email）
- [ ] 優化去抖動機制
- [ ] 增加歷史數據對比

---

## 🏭 任務 C：案場名稱提取優化

### 本週優化統計

| 指標 | 數值 | 目標 | 達成率 |
|------|------|------|--------|
| 總案場數 | {total} | - | - |
| 有完整名稱 | {with_names} | - | - |
| 名稱覆蓋率 | {coverage:.1f}% | 70% | {rate:.1f}% |

""".format(
        total=case_reports[0]['total_cases'] if case_reports else 0,
        with_names=case_reports[0]['with_names'] if case_reports else 0,
        coverage=case_reports[0]['coverage'] if case_reports else 0,
        rate=(case_reports[0]['coverage'] / 70 * 100) if case_reports else 0
    )
    
    report_md += """### 優化建議

- [ ] 擴大郵件掃描範圍至 180 天（目前 90 天）
- [ ] 手動補充主要案場名稱
- [ ] 建立案場名稱驗證機制
- [ ] 定期清理重複名稱

---

## 📊 整體進度

| 任務 | 狀態 | 自動化 | 下次回報 |
|------|------|--------|----------|
| B: 電廠監控 | 🟡 進行中 | ✅ 每日 08:00 | 下週一 09:30 |
| C: 案場名稱優化 | 🟡 進行中 | ✅ 每日 04:30 | 下週一 09:30 |

### 本週亮點

"""
    
    # 根據數據生成亮點
    if plant_reports and sum(r['critical_cases'] for r in plant_reports) == 0:
        report_md += "- ✅ 本週無嚴重異常案場\n"
    
    if case_reports and case_reports[0]['coverage'] > 60:
        report_md += f"- ✅ 案場名稱覆蓋率提升至 {case_reports[0]['coverage']:.1f}%\n"
    
    if not plant_reports and not case_reports:
        report_md += "- ⚠️ 本週無執行記錄，請檢查排程\n"
    
    report_md += f"""
---

## 📋 下週目標

1. **電廠監控**
   - [ ] 串接 AUO 真實數據源
   - [ ] 建立告警通知機制
   - [ ] 監控覆蓋率達 100%

2. **案場名稱優化**
   - [ ] 名稱覆蓋率提升至 70%
   - [ ] 擴大郵件掃描至 180 天
   - [ ] 建立名稱驗證機制

---

**報告自動生成**: 每週一 09:30
**下次報告**: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}
"""
    
    return report_md

def save_report(report_md):
    """儲存報告"""
    output_dir = WORKSPACE_DIR / 'weekly_progress_reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"weekly_progress_{datetime.now().strftime('%Y%m%d')}.md"
    output_file = output_dir / filename
    
    output_file.write_text(report_md, encoding='utf-8')
    logger.info(f"📄 已儲存報告：{output_file}")
    
    # 更新最新報告
    latest = output_dir / 'weekly_progress_latest.md'
    latest.write_text(report_md, encoding='utf-8')
    logger.info("📄 已更新最新報告")

def main():
    logger.info("=" * 70)
    logger.info("📈 昱金生能源 - 每週進度報告")
    logger.info(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # 取得日期範圍
    start_date, end_date = get_last_week_dates()
    logger.info(f"📅 報告期間：{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    
    # 掃描報告
    plant_reports = scan_plant_monitoring_reports(start_date, end_date)
    case_reports = scan_case_optimization_reports(start_date, end_date)
    
    # 生成報告
    report_md = generate_progress_report(plant_reports, case_reports)
    
    # 儲存報告
    save_report(report_md)
    
    # 輸出總結
    logger.info("\n" + "=" * 70)
    logger.info("✅ 每週進度報告完成！")
    logger.info("=" * 70)
    logger.info(f"電廠監控：{len(plant_reports)} 筆 | 案場優化：{len(case_reports)} 筆")

if __name__ == '__main__':
    main()
