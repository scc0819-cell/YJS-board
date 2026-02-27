#!/usr/bin/env python3
"""
昱金生能源集團 - 員工日報 AI 分析腳本
功能：
1. 讀取當日所有日報
2. AI 自動評分（A/B/C/D）
3. 風險評估與預警
4. 生成行動建議
5. 任務自動指派
"""

import json
import os
from pathlib import Path
from datetime import datetime
import sys

# 設定路徑
BASE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
REPORTS_DIR = BASE_DIR / 'daily_reports'
SCRIPTS_DIR = BASE_DIR / 'scripts'

def load_daily_reports(date):
    """讀取當日所有日報"""
    date_dir = REPORTS_DIR / date
    if not date_dir.exists():
        print(f"❌ 日期 {date} 的資料夾不存在")
        return []
    
    reports = []
    for report_file in date_dir.glob('*_report.json'):
        with open(report_file, 'r', encoding='utf-8') as f:
            reports.append(json.load(f))
    
    print(f"✅ 讀取 {len(reports)} 份日報")
    return reports

def score_daily_report(report):
    """評分單份日報"""
    score = 0
    details = {}
    
    # 1. 工作內容完整性（30 分）
    work_items = report.get('work_items', [])
    work_score = min(len(work_items) * 5, 30)
    score += work_score
    details['work_completeness'] = work_score
    
    # 2. 進度標記準確性（25 分）
    progress_items = [w for w in work_items if w.get('progress')]
    if progress_items:
        has_progress = len(progress_items) / len(work_items) if work_items else 0
        progress_score = int(has_progress * 25)
        score += progress_score
    details['progress_accuracy'] = progress_score if progress_items else 0
    
    # 3. 明日計畫具體度（15 分）
    plan_items = report.get('plan_items', [])
    if plan_items:
        plan_score = min(len(plan_items) * 5, 15)
        score += plan_score
    details['plan_specificity'] = plan_score if plan_items else 0
    
    # 4. 風險通報主動性（15 分）
    risk_items = report.get('risk_items', [])
    if risk_items:
        risk_score = 10
        # 有風險且有建議方案，加分
        if any(r.get('need_help') for r in risk_items):
            risk_score += 5
        score += risk_score
    details['risk_reporting'] = risk_score if risk_items else 0
    
    # 5. 附件佐證（10 分）
    attachments = report.get('attachments', {})
    attach_count = sum([
        attachments.get('photo', False),
        attachments.get('meeting', False),
        attachments.get('document', False),
        attachments.get('other', False)
    ])
    attach_score = min(attach_count * 3, 10)
    score += attach_score
    details['attachments'] = attach_score
    
    # 6. 及時提交（5 分）
    submit_time = report.get('submit_time', '')
    if submit_time:
        try:
            hour = int(submit_time.split(' ')[1].split(':')[0])
            if hour <= 18:
                score += 5
                details['on_time'] = 5
            else:
                details['on_time'] = 0
        except:
            details['on_time'] = 0
    
    # 判定等級
    if score >= 70:
        grade = 'A'
    elif score >= 50:
        grade = 'B'
    elif score >= 30:
        grade = 'C'
    else:
        grade = 'D'
    
    return {
        'total_score': score,
        'grade': grade,
        'details': details,
        'work_count': len(work_items),
        'plan_count': len(plan_items),
        'risk_count': len(risk_items)
    }

def analyze_risks(reports):
    """風險評估與預警"""
    all_risks = []
    
    for report in reports:
        for risk in report.get('risk_items', []):
            all_risks.append({
                'employee': report['employee_name'],
                'case_id': risk.get('case_id', ''),
                'level': risk.get('risk_level', ''),
                'description': risk.get('risk_desc', ''),
                'impact': risk.get('risk_impact', ''),
                'need_help': risk.get('need_help', ''),
                'date': report['report_date']
            })
    
    # 分類風險
    high_risks = [r for r in all_risks if r['level'] == 'high']
    medium_risks = [r for r in all_risks if r['level'] == 'medium']
    low_risks = [r for r in all_risks if r['level'] == 'low']
    
    return {
        'total': len(all_risks),
        'high': high_risks,
        'medium': medium_risks,
        'low': low_risks,
        'requires_immediate_action': len(high_risks) > 0
    }

def generate_action_items(reports, risk_analysis):
    """生成行動建議與任務指派"""
    actions = []
    
    # 1. 高風險事項優先處理
    for risk in risk_analysis['high']:
        actions.append({
            'priority': '🔥 高',
            'type': '風險處理',
            'case': risk['case_id'],
            'description': f"{risk['description']} - {risk['impact']}",
            'assignee': risk['employee'],
            'action': risk['need_help'],
            'deadline': '24 小時內',
            'status': '待處理'
        })
    
    # 2. D 級日報員工輔導
    for report in reports:
        score_result = score_daily_report(report)
        if score_result['grade'] == 'D':
            actions.append({
                'priority': '⚠️ 中',
                'type': '員工輔導',
                'case': '-',
                'description': f"{report['employee_name']} 日報品質待改進（{score_result['total_score']}分）",
                'assignee': '部門主管',
                'action': '约谈並提供教育訓練',
                'deadline': '3 日內',
                'status': '待處理'
            })
    
    # 3. 明日重點工作追蹤
    for report in reports:
        for plan in report.get('plan_items', []):
            if plan.get('need_support'):
                actions.append({
                    'priority': '🟢 低',
                    'type': '工作支援',
                    'case': plan.get('case_id', ''),
                    'description': f"{report['employee_name']} 需要支援：{plan['plan_content']}",
                    'assignee': '部門主管',
                    'action': plan['need_support'],
                    'deadline': '明日',
                    'status': '待確認'
                })
    
    return actions

def generate_analysis_report(date, reports):
    """生成完整分析報告"""
    # 評分所有日報
    scored_reports = []
    for report in reports:
        score_result = score_daily_report(report)
        scored_reports.append({
            **report,
            'score_result': score_result
        })
    
    # 風險分析
    risk_analysis = analyze_risks(reports)
    
    # 行動建議
    action_items = generate_action_items(reports, risk_analysis)
    
    # 統計數據
    total_employees = len(reports)
    grade_distribution = {
        'A': len([r for r in scored_reports if r['score_result']['grade'] == 'A']),
        'B': len([r for r in scored_reports if r['score_result']['grade'] == 'B']),
        'C': len([r for r in scored_reports if r['score_result']['grade'] == 'C']),
        'D': len([r for r in scored_reports if r['score_result']['grade'] == 'D'])
    }
    avg_score = sum(r['score_result']['total_score'] for r in scored_reports) / total_employees if total_employees > 0 else 0
    
    # 組裝報告
    analysis_report = {
        'date': date,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'total_employees': total_employees,
            'submitted': total_employees,
            'submission_rate': '100%',
            'average_score': round(avg_score, 1),
            'grade_distribution': grade_distribution
        },
        'risk_analysis': risk_analysis,
        'action_items': action_items,
        'employee_scores': [
            {
                'name': r['employee_name'],
                'score': r['score_result']['total_score'],
                'grade': r['score_result']['grade'],
                'work_count': r['score_result']['work_count'],
                'risk_count': r['score_result']['risk_count']
            }
            for r in scored_reports
        ],
        'recommendations': [
            '立即處理高風險事項：' + ', '.join([r['case_id'] for r in risk_analysis['high']]) if risk_analysis['high'] else '無高風險事項',
            '加強 D 級員工輔導：' + ', '.join([r['employee_name'] for r in scored_reports if r['score_result']['grade'] == 'D']) if any(r['score_result']['grade'] == 'D' for r in scored_reports) else '無需輔導',
            '明日重點追蹤：' + ', '.join([a['case'] for a in action_items if a['priority'] == '🟢 低']) if any(a['priority'] == '🟢 低' for a in action_items) else '無特殊事項'
        ]
    }
    
    return analysis_report

def save_analysis_report(date, analysis_report):
    """儲存分析報告"""
    date_dir = REPORTS_DIR / date
    date_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = date_dir / 'analysis_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 分析報告已儲存：{output_file}")

def main():
    if len(sys.argv) < 2:
        print("用法：python3 analyze_daily_reports.py <date>")
        print("範例：python3 analyze_daily_reports.py 2026-02-28")
        sys.exit(1)
    
    date = sys.argv[1]
    
    print("="*60)
    print(f"🤖 AI 日報分析 - {date}")
    print("="*60)
    
    # 讀取日報
    reports = load_daily_reports(date)
    if not reports:
        sys.exit(1)
    
    # 生成分析報告
    analysis_report = generate_analysis_report(date, reports)
    
    # 儲存報告
    save_analysis_report(date, analysis_report)
    
    # 列印摘要
    print("\n" + "="*60)
    print("📊 分析摘要")
    print("="*60)
    print(f"總員工數：{analysis_report['summary']['total_employees']}")
    print(f"平均評分：{analysis_report['summary']['average_score']}")
    print(f"評分分佈：A:{analysis_report['summary']['grade_distribution']['A']} "
          f"B:{analysis_report['summary']['grade_distribution']['B']} "
          f"C:{analysis_report['summary']['grade_distribution']['C']} "
          f"D:{analysis_report['summary']['grade_distribution']['D']}")
    print(f"高風險事項：{len(analysis_report['risk_analysis']['high'])}")
    print(f"行動建議：{len(analysis_report['action_items'])} 項")
    print("="*60)

if __name__ == '__main__':
    main()
