#!/usr/bin/env python3
"""
昱金生能源集團 - 員工日報系統 v3.0
改進：
1. 登入驗證（帳號密碼保護）
2. 案場下拉選單（不需手打）
3. AI 自動分析（提交即觸發）
4. 歷史查詢功能
5. 草稿自動儲存
6. 自動提醒（超時未交）
7. 員工管理後台
"""

from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
import os
import json
import hashlib
from pathlib import Path
import threading
import subprocess

app = Flask(__name__)
app.secret_key = 'yjsenergy_v3_2026_ultra_secret'
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '請先登入'

# ===================== 路徑設定 =====================
BASE_DIR = Path('/home/yjsclaw/.openclaw/workspace')
REPORTS_DIR = BASE_DIR / 'daily_reports'
SCRIPTS_DIR = BASE_DIR / 'scripts'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ===================== 帳號資料 =====================
# 密碼使用 SHA256 雜湊，格式：sha256(帳號+密碼)
def hash_pw(username, password):
    return hashlib.sha256(f"{username}{password}".encode()).hexdigest()

USERS = {
    "admin": {
        "id": "admin",
        "name": "宋董事長",
        "role": "admin",
        "password_hash": hash_pw("admin", "yjsenergy2026")
    },
    "chen_ming_de": {
        "id": "chen_ming_de",
        "name": "陳明德",
        "role": "employee",
        "password_hash": hash_pw("chen_ming_de", "1234")
    },
    "yang_zong_wei": {
        "id": "yang_zong_wei",
        "name": "楊宗衛",
        "role": "employee",
        "password_hash": hash_pw("yang_zong_wei", "1234")
    },
    "li_ya_ting": {
        "id": "li_ya_ting",
        "name": "李雅婷",
        "role": "employee",
        "password_hash": hash_pw("li_ya_ting", "1234")
    },
    "hong_shu_rong": {
        "id": "hong_shu_rong",
        "name": "洪淑嫆",
        "role": "employee",
        "password_hash": hash_pw("hong_shu_rong", "1234")
    },
    "chen_gu_bin": {
        "id": "chen_gu_bin",
        "name": "陳谷濱",
        "role": "employee",
        "password_hash": hash_pw("chen_gu_bin", "1234")
    },
    "zhang_yi_chuan": {
        "id": "zhang_yi_chuan",
        "name": "張億峖",
        "role": "employee",
        "password_hash": hash_pw("zhang_yi_chuan", "1234")
    },
    "lin_kun_yi": {
        "id": "lin_kun_yi",
        "name": "林坤誼",
        "role": "employee",
        "password_hash": hash_pw("lin_kun_yi", "1234")
    },
    "huang_zhen_hao": {
        "id": "huang_zhen_hao",
        "name": "黃振豪",
        "role": "employee",
        "password_hash": hash_pw("huang_zhen_hao", "1234")
    },
    "xu_hui_ling": {
        "id": "xu_hui_ling",
        "name": "許惠玲",
        "role": "employee",
        "password_hash": hash_pw("xu_hui_ling", "1234")
    },
}

EMPLOYEES = [v for v in USERS.values() if v["role"] == "employee"]

# ===================== 案場清單 =====================
CASES = [
    {"id": "馬偕護專", "name": "馬偕護專停車場", "type": "停車場"},
    {"id": "彰化聯合標租", "name": "彰化學校聯合標租", "type": "屋頂型"},
    {"id": "陸豐國小", "name": "陸豐國小", "type": "屋頂型"},
    {"id": "媽厝國小", "name": "媽厝國小", "type": "屋頂型"},
    {"id": "仁豐國小", "name": "仁豐國小", "type": "屋頂型"},
    {"id": "萬合國小", "name": "萬合國小", "type": "屋頂型"},
    {"id": "長安國小", "name": "長安國小", "type": "屋頂型"},
    {"id": "線西國小", "name": "線西國小H區", "type": "風雨球場"},
    {"id": "伸東國小", "name": "伸東國小", "type": "屋頂型"},
    {"id": "鹿東國小", "name": "鹿東國小二校區", "type": "屋頂型"},
    {"id": "台積電PPA", "name": "台積電 PPA 綠電轉供", "type": "PPA"},
    {"id": "永豐融資", "name": "永豐銀行融資展延", "type": "行政"},
    {"id": "其他", "name": "其他/行政事務", "type": "行政"},
]

# ===================== 登入系統 =====================
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data["id"]
        self.name = user_data["name"]
        self.role = user_data["role"]

@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        return User(USERS[user_id])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user_data = USERS.get(username)
        if user_data and user_data['password_hash'] == hash_pw(username, password):
            user = User(user_data)
            login_user(user)
            flash(f'歡迎回來，{user.name}！', 'success')
            return redirect(url_for('index'))
        flash('帳號或密碼錯誤', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已登出', 'info')
    return redirect(url_for('login'))

# ===================== 首頁 =====================
@app.route('/')
@login_required
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    today_dir = REPORTS_DIR / today

    submitted_ids = set()
    if today_dir.exists():
        for f in today_dir.glob('*_report.json'):
            submitted_ids.add(f.stem.replace('_report', ''))

    submitted = [e for e in EMPLOYEES if e['id'] in submitted_ids]
    not_submitted = [e for e in EMPLOYEES if e['id'] not in submitted_ids]
    total = len(EMPLOYEES)
    submitted_count = len(submitted)
    rate = round(submitted_count / total * 100, 1) if total else 0

    # 員工只能看到自己的按鈕
    is_admin = current_user.role == 'admin'

    return render_template('index_v3.html',
        employees=EMPLOYEES,
        submitted=submitted,
        not_submitted=not_submitted,
        total=total,
        submitted_count=submitted_count,
        submission_rate=rate,
        today=today,
        is_admin=is_admin,
        current_user_id=current_user.id
    )

# ===================== 填寫表單 =====================
@app.route('/report', methods=['GET', 'POST'])
@app.route('/report/<employee_id>', methods=['GET', 'POST'])
@login_required
def report_form(employee_id=None):
    # 員工只能填自己的日報
    if current_user.role == 'employee':
        employee_id = current_user.id

    user_data = USERS.get(employee_id)
    if not user_data:
        flash('員工不存在', 'error')
        return redirect(url_for('index'))

    today = datetime.now().strftime('%Y-%m-%d')

    # 檢查是否已提交（允許覆蓋）
    today_dir = REPORTS_DIR / today
    existing = None
    report_file = today_dir / f"{employee_id}_report.json"
    if report_file.exists():
        with open(report_file, encoding='utf-8') as f:
            existing = json.load(f)

    if request.method == 'POST':
        data = request.json if request.is_json else request.form

        work_items = json.loads(request.form.get('work_items_json', '[]'))
        plan_items = json.loads(request.form.get('plan_items_json', '[]'))
        risk_items = json.loads(request.form.get('risk_items_json', '[]'))

        report = {
            "employee_id": employee_id,
            "employee_name": user_data['name'],
            "department": "未分類",
            "report_date": today,
            "submit_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "work_items": work_items,
            "plan_items": plan_items,
            "risk_items": risk_items,
            "summary": {
                "today_gain": request.form.get('today_gain', ''),
                "improvement": request.form.get('improvement', ''),
                "remarks": request.form.get('remarks', '')
            },
            "attachments": {
                "photo": 'photo' in request.form,
                "meeting": 'meeting' in request.form,
                "document": 'document' in request.form,
                "other": 'other_attachment' in request.form,
                "note": request.form.get('attachment_note', '')
            }
        }

        today_dir.mkdir(parents=True, exist_ok=True)
        is_edit = report_file.exists()
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # 編輯留痕
        action = '覆蓋修改' if is_edit else '初次提交'
        append_edit_log(report_file, current_user.name, action)

        # 自動觸發 AI 分析（背景執行）
        def run_analysis():
            try:
                subprocess.run(
                    ['python3', str(SCRIPTS_DIR / 'analyze_daily_reports.py'), today],
                    capture_output=True, timeout=60
                )
            except Exception:
                pass
        threading.Thread(target=run_analysis, daemon=True).start()

        flash('✅ 日報提交成功！AI 分析已自動觸發。', 'success')
        return redirect(url_for('index'))

    return render_template('report_form_v3.html',
        employee=user_data,
        today=today,
        cases=CASES,
        existing=existing
    )

# ===================== 草稿 API =====================
@app.route('/api/draft/save', methods=['POST'])
@login_required
def save_draft():
    today = datetime.now().strftime('%Y-%m-%d')
    draft_dir = REPORTS_DIR / today
    draft_dir.mkdir(parents=True, exist_ok=True)
    draft_file = draft_dir / f"{current_user.id}_draft.json"
    with open(draft_file, 'w', encoding='utf-8') as f:
        json.dump(request.json, f, ensure_ascii=False, indent=2)
    return jsonify({"status": "saved"})

@app.route('/api/draft/load')
@login_required
def load_draft():
    today = datetime.now().strftime('%Y-%m-%d')
    draft_file = REPORTS_DIR / today / f"{current_user.id}_draft.json"
    if draft_file.exists():
        with open(draft_file, encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({})

# ===================== 管理後台 =====================
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('無權限訪問', 'error')
        return redirect(url_for('index'))

    today = datetime.now().strftime('%Y-%m-%d')
    date_param = request.args.get('date', today)
    date_dir = REPORTS_DIR / date_param

    reports = []
    if date_dir.exists():
        for f in sorted(date_dir.glob('*_report.json')):
            with open(f, encoding='utf-8') as fp:
                reports.append(json.load(fp))

    analysis = None
    analysis_file = date_dir / 'analysis_result.json'
    if analysis_file.exists():
        with open(analysis_file, encoding='utf-8') as f:
            analysis = json.load(f)

    # 取得歷史日期清單
    history_dates = sorted(
        [d.name for d in REPORTS_DIR.iterdir() if d.is_dir()],
        reverse=True
    )[:30]

    submitted_ids = {r['employee_id'] for r in reports}
    not_submitted = [e for e in EMPLOYEES if e['id'] not in submitted_ids]

    return render_template('admin_v3.html',
        reports=reports,
        analysis=analysis,
        date=date_param,
        today=today,
        history_dates=history_dates,
        employees=EMPLOYEES,
        not_submitted=not_submitted,
        submitted_count=len(reports),
        total=len(EMPLOYEES)
    )

# ===================== 歷史查詢 =====================
@app.route('/history')
@login_required
def history():
    emp_id = current_user.id if current_user.role == 'employee' else request.args.get('emp_id', '')
    records = []
    if REPORTS_DIR.exists():
        for date_dir in sorted(REPORTS_DIR.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue
            report_file = date_dir / f"{emp_id}_report.json"
            if report_file.exists():
                with open(report_file, encoding='utf-8') as f:
                    records.append(json.load(f))
    return render_template('history.html',
        records=records,
        emp_id=emp_id,
        employees=EMPLOYEES,
        is_admin=current_user.role == 'admin'
    )

# ===================== API =====================
@app.route('/api/status')
@login_required
def api_status():
    today = datetime.now().strftime('%Y-%m-%d')
    today_dir = REPORTS_DIR / today
    submitted = len(list(today_dir.glob('*_report.json'))) if today_dir.exists() else 0
    return jsonify({
        'status': 'ok',
        'date': today,
        'total_employees': len(EMPLOYEES),
        'submitted': submitted,
        'rate': round(submitted / len(EMPLOYEES) * 100, 1)
    })

@app.route('/api/cases')
@login_required
def api_cases():
    return jsonify(CASES)

# ===================== 逾時未交提醒 =====================
@app.route('/api/reminder/check')
@login_required
def reminder_check():
    """檢查今天哪些員工還未提交，回傳名單（admin only）"""
    if current_user.role != 'admin':
        return jsonify({'error': '無權限'}), 403
    today = datetime.now().strftime('%Y-%m-%d')
    today_dir = REPORTS_DIR / today
    submitted_ids = set()
    if today_dir.exists():
        for f in today_dir.glob('*_report.json'):
            submitted_ids.add(f.stem.replace('_report', ''))
    missing = [{'id': e['id'], 'name': e['name']} for e in EMPLOYEES if e['id'] not in submitted_ids]
    hour = datetime.now().hour
    overdue = hour >= 18  # 18:00 後算逾時
    return jsonify({
        'date': today,
        'total': len(EMPLOYEES),
        'submitted': len(submitted_ids),
        'missing': missing,
        'overdue': overdue,
        'current_hour': hour
    })

# ===================== 編輯留痕 =====================
def append_edit_log(report_file: Path, operator: str, action: str):
    """在日報 JSON 中追加編輯記錄"""
    if not report_file.exists():
        return
    with open(report_file, encoding='utf-8') as f:
        data = json.load(f)
    if 'edit_log' not in data:
        data['edit_log'] = []
    data['edit_log'].append({
        'operator': operator,
        'action': action,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===================== 圖表資料 API =====================
@app.route('/api/chart/weekly')
@login_required
def chart_weekly():
    """最近 7 天各日提交率（供圖表使用）"""
    if current_user.role != 'admin':
        return jsonify({'error': '無權限'}), 403
    from datetime import timedelta
    result = []
    total = len(EMPLOYEES)
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        ddir = REPORTS_DIR / d
        count = len(list(ddir.glob('*_report.json'))) if ddir.exists() else 0
        result.append({'date': d, 'submitted': count, 'total': total,
                        'rate': round(count / total * 100, 1) if total else 0})
    return jsonify(result)

@app.route('/api/chart/risk_summary')
@login_required
def chart_risk_summary():
    """今日風險分佈統計"""
    if current_user.role != 'admin':
        return jsonify({'error': '無權限'}), 403
    today = datetime.now().strftime('%Y-%m-%d')
    today_dir = REPORTS_DIR / today
    high = medium = low = 0
    if today_dir.exists():
        for f in today_dir.glob('*_report.json'):
            with open(f, encoding='utf-8') as fp:
                r = json.load(fp)
            for risk in r.get('risk_items', []):
                lv = risk.get('risk_level', 'low')
                if lv == 'high': high += 1
                elif lv == 'medium': medium += 1
                else: low += 1
    return jsonify({'high': high, 'medium': medium, 'low': low})

# ===================== 啟動 =====================
if __name__ == '__main__':
    print("=" * 60)
    print("🏢 昱金生能源集團 - 員工日報系統 v3.0")
    print("=" * 60)
    print(f"🌐 http://127.0.0.1:5000")
    print(f"🔐 管理員帳號：admin / yjsenergy2026")
    print(f"👷 員工預設密碼：1234")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
