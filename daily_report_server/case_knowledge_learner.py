#!/usr/bin/env python3
"""
昱金生能源 - 案場知識深度學習系統
從郵件中提取案場經驗、流程、問題、解決方案
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

# 路徑設定
BASE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
OUTPUT_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/full_email_analysis')
MEMORY_DIR = BASE_DIR / 'memory'

def load_case_database():
    """載入案場資料庫"""
    case_db_file = OUTPUT_DIR / 'case_database.json'
    if case_db_file.exists():
        with open(case_db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_employee_database():
    """載入員工資料庫"""
    emp_db_file = OUTPUT_DIR / 'employee_database.json'
    if emp_db_file.exists():
        with open(emp_db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def extract_case_experience(case_data):
    """從案場數據中提取經驗"""
    experience = {
        'case_id': case_data.get('case_id', ''),
        'case_name': case_data.get('case_name', ''),
        'case_type': case_data.get('type', ''),
        'total_reports': 0,
        'timeline': [],
        'common_issues': [],
        'solutions': [],
        'key_personnel': set(),
        'lessons_learned': []
    }
    
    # 分析報告
    reports = case_data.get('reports', [])
    experience['total_reports'] = len(reports)
    
    # 提取時間軸
    dates = set()
    for report in reports:
        date = report.get('report_date', '')
        if date:
            dates.add(date)
        employee = report.get('employee_id', '')
        if employee:
            experience['key_personnel'].add(employee)
    
    experience['timeline'] = sorted(list(dates))
    experience['key_personnel'] = list(experience['key_personnel'])
    
    # 提取常見問題（從工作內容中）
    issue_keywords = ['問題', '異常', '困難', '障礙', '缺失', '改善', '待處理']
    for report in reports:
        work_content = report.get('work_content', '')
        if any(kw in work_content for kw in issue_keywords):
            experience['common_issues'].append({
                'date': report.get('report_date', ''),
                'employee': report.get('employee_id', ''),
                'description': work_content[:200]
            })
    
    # 提取解決方案
    solution_keywords = ['已完成', '解決', '修復', '改善', '完成', 'ok', 'okay']
    for report in reports:
        work_content = report.get('work_content', '')
        progress = report.get('progress', 0)
        if any(kw in work_content.lower() for kw in solution_keywords) or progress == 100:
            experience['solutions'].append({
                'date': report.get('report_date', ''),
                'employee': report.get('employee_id', ''),
                'solution': work_content[:200]
            })
    
    # 提取經驗教訓
    if len(reports) > 10:
        experience['lessons_learned'].append(f"長期案場，累積 {len(reports)} 次報告")
    if len(experience['key_personnel']) > 3:
        experience['lessons_learned'].append(f"多人協作案場，參與人員：{len(experience['key_personnel'])} 位")
    
    return experience

def generate_case_insights(cases_experiences):
    """生成案場洞察報告"""
    insights = {
        'timestamp': datetime.now().isoformat(),
        'total_cases': len(cases_experiences),
        'active_cases': 0,
        'high_frequency_cases': [],
        'multi_person_cases': [],
        'common_patterns': [],
        'recommendations': []
    }
    
    # 分析活躍案場
    for exp in cases_experiences:
        if exp['total_reports'] > 5:
            insights['active_cases'] += 1
            insights['high_frequency_cases'].append({
                'case_id': exp['case_id'],
                'reports': exp['total_reports'],
                'personnel': len(exp['key_personnel'])
            })
        
        if len(exp['key_personnel']) > 3:
            insights['multi_person_cases'].append({
                'case_id': exp['case_id'],
                'personnel_count': len(exp['key_personnel']),
                'personnel': exp['key_personnel']
            })
    
    # 排序
    insights['high_frequency_cases'].sort(key=lambda x: x['reports'], reverse=True)
    insights['multi_person_cases'].sort(key=lambda x: x['personnel_count'], reverse=True)
    
    # 提取共同模式
    if insights['high_frequency_cases']:
        insights['common_patterns'].append(
            f"高頻案場共 {len(insights['high_frequency_cases'])} 個，主要為長期維運或複雜工程"
        )
    
    if insights['multi_person_cases']:
        insights['common_patterns'].append(
            f"多人協作案場共 {len(insights['multi_person_cases'])} 個，需要良好的溝通協調"
        )
    
    # 建議
    if insights['active_cases'] > 10:
        insights['recommendations'].append("建議建立標準化作業流程 (SOP) 以降低對特定人員的依賴")
    
    if len([c for c in insights['high_frequency_cases'] if c['reports'] > 20]) > 0:
        insights['recommendations'].append("高頻案場應定期檢討，優化維護策略")
    
    return insights

def update_memory_with_insights(insights, cases_experiences):
    """更新記憶系統"""
    today = datetime.now().strftime('%Y-%m-%d')
    memory_file = MEMORY_DIR / f'{today}.md'
    
    with open(memory_file, 'a', encoding='utf-8') as f:
        f.write(f"\n\n## 🧠 案場知識深度學習報告\n")
        f.write(f"**更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"### 總覽\n")
        f.write(f"- 學習案場總數：{insights['total_cases']}\n")
        f.write(f"- 活躍案場：{insights['active_cases']}\n")
        f.write(f"- 高頻案場：{len(insights['high_frequency_cases'])}\n")
        f.write(f"- 多人協作案場：{len(insights['multi_person_cases'])}\n\n")
        
        if insights['high_frequency_cases'][:5]:
            f.write(f"### 🔥 TOP 5 高頻案場\n")
            for i, case in enumerate(insights['high_frequency_cases'][:5], 1):
                f.write(f"{i}. **{case['case_id']}** - {case['reports']} 次報告，{case['personnel']} 位參與\n")
            f.write("\n")
        
        if insights['common_patterns']:
            f.write(f"### 📊 共同模式\n")
            for pattern in insights['common_patterns']:
                f.write(f"- {pattern}\n")
            f.write("\n")
        
        if insights['recommendations']:
            f.write(f"### 💡 建議事項\n")
            for rec in insights['recommendations']:
                f.write(f"- {rec}\n")
            f.write("\n")
    
    print(f"✅ 已更新記憶：{memory_file}")

def save_case_experiences(cases_experiences):
    """儲存案場經驗"""
    output_file = OUTPUT_DIR / 'case_experiences.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cases_experiences, f, ensure_ascii=False, indent=2)
    print(f"✅ 已儲存案場經驗：{output_file}")

def save_insights(insights):
    """儲存洞察報告"""
    output_file = OUTPUT_DIR / f'case_insights_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(insights, f, ensure_ascii=False, indent=2)
    print(f"✅ 已儲存洞察報告：{output_file}")

def main():
    """主函數"""
    print("=" * 60)
    print("🧠 昱金生能源 - 案場知識深度學習系統")
    print(f"⏰ 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 載入資料庫
    print("\n📚 載入資料庫...")
    case_db = load_case_database()
    employee_db = load_employee_database()
    print(f"   案場數：{len(case_db)}")
    print(f"   員工數：{len(employee_db)}")
    
    # 2. 提取案場經驗
    print("\n🔍 提取案場經驗...")
    cases_experiences = []
    for case_id, case_data in case_db.items():
        exp = extract_case_experience(case_data)
        cases_experiences.append(exp)
    print(f"   已提取 {len(cases_experiences)} 個案場經驗")
    
    # 3. 生成洞察
    print("\n💡 生成洞察報告...")
    insights = generate_case_insights(cases_experiences)
    print(f"   活躍案場：{insights['active_cases']}")
    print(f"   高頻案場：{len(insights['high_frequency_cases'])}")
    
    # 4. 儲存結果
    print("\n💾 儲存結果...")
    save_case_experiences(cases_experiences)
    save_insights(insights)
    
    # 5. 更新記憶
    print("\n🧠 更新記憶系統...")
    update_memory_with_insights(insights, cases_experiences)
    
    print("\n" + "=" * 60)
    print("✅ 案場知識深度學習完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
