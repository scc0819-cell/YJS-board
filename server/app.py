#!/usr/bin/env python3
"""
昱金生能源集團 - 員工日報系統後端伺服器
功能：
1. 提供員工日報填寫網頁
2. 自動儲存日報資料（依日期分類）
3. 自動觸發 AI 分析
4. 生成管理報表
"""

from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import json
import pandas as pd
from pathlib import Path
import subprocess
import shutil

app = Flask(__name__)
app.secret_key = 'yjsenergy_daily_report_2026_secret_key'
CORS(app)

# 設定路徑
BASE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
REPORTS_DIR = BASE_DIR / 'daily_reports'
TEMPLATES_DIR = BASE_DIR / 'templates'
SCRIPTS_DIR = BASE_DIR / 'scripts'

# 確保目錄存在
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# 員工清單
EMPLOYEES = [
    {"id": "chen_ming_de", "name": "陳明德", "email": "alexchen@yjsenergy.com", "department": "工程部"},
    {"id": "chen_gu_bin", "name": "陳谷濱", "email": "eng@yjsenergy.com", "department": "工程部"},
    {"id": "zhang_yi_chuan", "name": "張億峖", "email": "eng@yjsenergy.com", "department": "工程部"},
    {"id": "yang_zong_wei", "name": "楊宗衛", "email": "eng@yjsenergy.com", "department": "工程部"},
    {"id": "li_ya_ting", "name": "李雅婷", "email": "colleenlee@yjsenergy.com", "department": "行政部"},
    {"id": "gao_zhu_yu", "name": "高竹妤", "email": "cukao@yjsenergy.com", "department": "設計部"},
    {"id": "chen_jing_ru", "name": "陳靜儒", "email": "mat@yjsenergy.com", "department": "行政部"},
    {"id": "hong_shu_rong", "name": "洪淑嫆", "email": "hr@yjsenergy.com", "department": "行政部"},
    {"id": "yang_jie_lin", "name": "楊傑麟", "email": "legal@yjsenergy.com", "department": "業務部"},
]

# ==================== 網頁路由 ====================

@app.route('/')
def index():
    """首頁 - 日報提交清單"""
    today = datetime.now().strftime('%Y-%m-%d')
    today_dir = REPORTS_DIR / today
    
    # 檢查今日提交狀況
    submissions = []
    if today_dir.exists():
        for emp in EMPLOYEES:
            report_file = today_dir / f"{emp['id']}_report.json"
            submitted = report_file.exists()
            submissions.append({
                **emp,
                'submitted': submitted,
                'submit_time': None
            })
            if submitted:
                with open(report_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    submissions[-1]['submit_time'] = data.get('submit_time', 'Unknown')
    else:
        submissions = [{**emp, 'submitted': False, 'submit_time': None} for emp in EMPLOYEES]
    
    return render_template('index.html', submissions=submissions, today=today)

@app.route('/submit', methods=['GET'])
def submit_form():
    """日報填寫表單"""
    employee_id = request.args.get('employee_id')
    employee = next((emp for emp in EMPLOYEES if emp['id'] == employee_id), None)
    if not employee:
        flash('請選擇員工', 'error')
        return redirect(url_for('index'))
    
    return render_template('daily_report_form_full.html', employee=employee)

@app.route('/submit', methods=['POST'])
def submit_report():
    """提交日報"""
    try:
        # 收集表單資料
        data = {
            'employee_id': request.form.get('employee_id'),
            'employee_name': request.form.get('employee_name'),
            'department': request.form.get('department'),
            'report_date': request.form.get('report_date'),
            'submit_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'work_items': [],
            'plan_items': [],
            'risk_items': [],
            'summary': {
                'today_gain': request.form.get('today_gain', ''),
                'improvement': request.form.get('improvement', ''),
                'remarks': request.form.get('remarks', '')
            },
            'attachments': {
                'photo': request.form.get('attach_photo') == 'on',
                'meeting': request.form.get('attach_meeting') == 'on',
                'document': request.form.get('attach_document') == 'on',
                'other': request.form.get('attach_other') == 'on',
                'note': request.form.get('attach_note', '')
            }
        }
        
        # 收集工作項目
        work_count = int(request.form.get('work_count', 0))
        for i in range(work_count):
            data['work_items'].append({
                'case_id': request.form.get(f'work_{i}_case_id', ''),
                'case_name': request.form.get(f'work_{i}_case_name', ''),
                'work_type': request.form.get(f'work_{i}_type', ''),
                'work_content': request.form.get(f'work_{i}_content', ''),
                'progress': request.form.get(f'work_{i}_progress', ''),
                'hours': request.form.get(f'work_{i}_hours', ''),
                'output': request.form.get(f'work_{i}_output', ''),
                'status': request.form.get(f'work_{i}_status', '')
            })
        
        # 收集明日計畫
        plan_count = int(request.form.get('plan_count', 0))
        for i in range(plan_count):
            data['plan_items'].append({
                'case_id': request.form.get(f'plan_{i}_case_id', ''),
                'case_name': request.form.get(f'plan_{i}_case_name', ''),
                'plan_content': request.form.get(f'plan_{i}_content', ''),
                'plan_hours': request.form.get(f'plan_{i}_hours', ''),
                'need_support': request.form.get(f'plan_{i}_support', '')
            })
        
        # 收集風險事項
        risk_count = int(request.form.get('risk_count', 0))
        for i in range(risk_count):
            data['risk_items'].append({
                'case_id': request.form.get(f'risk_{i}_case_id', ''),
                'risk_level': request.form.get(f'risk_{i}_level', ''),
                'risk_desc': request.form.get(f'risk_{i}_desc', ''),
                'risk_impact': request.form.get(f'risk_{i}_impact', ''),
                'need_help': request.form.get(f'risk_{i}_help', '')
            })
        
        # 建立日期資料夾
        report_date = data['report_date']
        date_dir = REPORTS_DIR / report_date
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # 儲存日報檔案
        employee_id = data['employee_id']
        report_file = date_dir / f"{employee_id}_report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 記錄提交時間
        log_file = date_dir / 'submission_log.json'
        log_data = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        log_data.append({
            'employee_id': employee_id,
            'employee_name': data['employee_name'],
            'submit_time': data['submit_time']
        })
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        flash(f"✅ {data['employee_name']} 的日報已提交成功！", 'success')
        
        # 檢查是否所有人都已提交，如果是則觸發分析
        all_submitted = check_all_submitted(report_date)
        if all_submitted:
            trigger_analysis(report_date)
        
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'❌ 提交失敗：{str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/reports/<date>')
def view_reports(date):
    """檢視指定日期的所有日報"""
    date_dir = REPORTS_DIR / date
    if not date_dir.exists():
        flash('該日期無日報資料', 'error')
        return redirect(url_for('index'))
    
    reports = []
    for emp in EMPLOYEES:
        report_file = date_dir / f"{emp['id']}_report.json"
        if report_file.exists():
            with open(report_file, 'r', encoding='utf-8') as f:
                reports.append(json.load(f))
    
    # 檢查是否有分析報告
    analysis_file = date_dir / 'analysis_result.json'
    analysis = None
    if analysis_file.exists():
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
    
    return render_template('view_reports.html', reports=reports, date=date, analysis=analysis)

@app.route('/api/submission-status/<date>')
def api_submission_status(date):
    """API - 查詢提交狀況"""
    date_dir = REPORTS_DIR / date
    status = {
        'date': date,
        'total': len(EMPLOYEES),
        'submitted': 0,
        'pending': 0,
        'employees': []
    }
    
    if date_dir.exists():
        for emp in EMPLOYEES:
            report_file = date_dir / f"{emp['id']}_report.json"
            submitted = report_file.exists()
            status['employees'].append({
                'id': emp['id'],
                'name': emp['name'],
                'submitted': submitted
            })
            if submitted:
                status['submitted'] += 1
            else:
                status['pending'] += 1
    
    return jsonify(status)

# ==================== 輔助函數 ====================

def check_all_submitted(date):
    """檢查是否所有人都已提交"""
    date_dir = REPORTS_DIR / date
    if not date_dir.exists():
        return False
    
    submitted_count = 0
    for emp in EMPLOYEES:
        report_file = date_dir / f"{emp['id']}_report.json"
        if report_file.exists():
            submitted_count += 1
    
    # 假設 80% 提交率就觸發分析
    return submitted_count >= len(EMPLOYEES) * 0.8

def trigger_analysis(date):
    """觸發 AI 分析"""
    try:
        # 呼叫分析腳本
        analysis_script = SCRIPTS_DIR / 'analyze_daily_reports.py'
        if analysis_script.exists():
            subprocess.run(['python3', str(analysis_script), date], timeout=300)
            print(f"✅ {date} 的分析已完成")
        else:
            print(f"⚠️ 分析腳本不存在：{analysis_script}")
    except Exception as e:
        print(f"❌ 分析失敗：{e}")

# ==================== 啟動伺服器 ====================

if __name__ == '__main__':
    print("="*60)
    print("🏢 昱金生能源集團 - 員工日報系統")
    print("="*60)
    print(f"📁 資料儲存路徑：{REPORTS_DIR}")
    print(f"🌐 伺服器網址：http://localhost:5000")
    print(f"👥 員工人數：{len(EMPLOYEES)}")
    print("="*60)
    
    # 啟動伺服器（開發環境）
    app.run(host='0.0.0.0', port=5000, debug=True)
