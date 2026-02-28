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

from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session, send_file
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import hashlib
from pathlib import Path
import threading
import subprocess
import io
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    EXCEL_OK = True
except ImportError:
    EXCEL_OK = False

app = Flask(__name__)
# NOTE: 正式環境請改用環境變數或外部設定檔提供 secret key
app.secret_key = os.environ.get('YJS_DAILY_REPORT_SECRET_KEY', 'yjsenergy_v3_2026_ultra_secret')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
)
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
# ✅ 改善重點：
# - 不再把預設密碼顯示在畫面上
# - 支援登入後自行修改密碼
# - 使用者資料改為落地到 JSON（重啟不會消失）
# - 密碼雜湊改用 werkzeug（含 salt），避免自製 SHA256

DATA_DIR = BASE_DIR / 'server' / 'data'
USERS_FILE = DATA_DIR / 'users.json'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 初始帳號（首次建立 users.json 時才會使用）
# 注意：員工初始密碼不在畫面顯示；首次登入會被要求修改密碼。
SEED_USERS = {
    "admin": {
        "id": "admin",
        "name": "宋董事長",
        "role": "admin",
        "password_hash": generate_password_hash("yjsenergy2026"),
        "password_temp": False,
    },
    "chen_ming_de": {"id": "chen_ming_de", "name": "陳明德", "role": "employee", "password_hash": generate_password_hash("1234"), "password_temp": True},
    "yang_zong_wei": {"id": "yang_zong_wei", "name": "楊宗衛", "role": "employee", "password_hash": generate_password_hash("1234"), "password_temp": True},
    "li_ya_ting": {"id": "li_ya_ting", "name": "李雅婷", "role": "employee", "password_hash": generate_password_hash("1234"), "password_temp": True},
    "hong_shu_rong": {"id": "hong_shu_rong", "name": "洪淑嫆", "role": "employee", "password_hash": generate_password_hash("1234"), "password_temp": True},
    "chen_gu_bin": {"id": "chen_gu_bin", "name": "陳谷濱", "role": "employee", "password_hash": generate_password_hash("1234"), "password_temp": True},
    "zhang_yi_chuan": {"id": "zhang_yi_chuan", "name": "張億峖", "role": "employee", "password_hash": generate_password_hash("1234"), "password_temp": True},
    "lin_kun_yi": {"id": "lin_kun_yi", "name": "林坤誼", "role": "employee", "password_hash": generate_password_hash("1234"), "password_temp": True},
    "huang_zhen_hao": {"id": "huang_zhen_hao", "name": "黃振豪", "role": "employee", "password_hash": generate_password_hash("1234"), "password_temp": True},
    "xu_hui_ling": {"id": "xu_hui_ling", "name": "許惠玲", "role": "employee", "password_hash": generate_password_hash("1234"), "password_temp": True},
}


def load_users():
    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text(encoding='utf-8'))
        except Exception:
            # 檔案損壞時回退到 seed（避免整個系統起不來）
            return dict(SEED_USERS)
    # 首次建立
    USERS_FILE.write_text(json.dumps(SEED_USERS, ensure_ascii=False, indent=2), encoding='utf-8')
    return dict(SEED_USERS)


def save_users(users: dict):
    tmp = USERS_FILE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(USERS_FILE)


def public_user(u: dict) -> dict:
    return {
        'id': u.get('id'),
        'name': u.get('name'),
        'role': u.get('role'),
    }


USERS = load_users()


def refresh_employee_cache():
    global EMPLOYEES
    EMPLOYEES = [public_user(v) for v in USERS.values() if v.get('role') == 'employee']
    EMPLOYEES.sort(key=lambda x: x.get('name') or '')


refresh_employee_cache()


# ===================== 安全與稽核 =====================
AUTH_STATE_FILE = DATA_DIR / 'auth_state.json'
AUDIT_LOG_FILE = DATA_DIR / 'audit.jsonl'


def _now_ts():
    return int(datetime.now().timestamp())


def load_auth_state():
    if AUTH_STATE_FILE.exists():
        try:
            return json.loads(AUTH_STATE_FILE.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def save_auth_state(state: dict):
    tmp = AUTH_STATE_FILE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(AUTH_STATE_FILE)


def client_ip():
    xf = request.headers.get('X-Forwarded-For', '')
    if xf:
        return xf.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def audit(event: str, actor_id: str = '', target_id: str = '', detail: dict | None = None):
    """寫入稽核紀錄（JSONL）。避免寫入密碼等敏感資訊。"""
    rec = {
        'ts': _now_ts(),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'event': event,
        'actor_id': actor_id,
        'target_id': target_id,
        'ip': client_ip(),
        'path': request.path,
        'detail': detail or {},
    }
    try:
        with open(AUDIT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


def tail_jsonl(p: Path, max_lines: int = 400):
    if not p.exists():
        return []
    try:
        lines = p.read_text(encoding='utf-8', errors='ignore').splitlines()[-max_lines:]
        out = []
        for ln in lines:
            try:
                out.append(json.loads(ln))
            except Exception:
                continue
        return out
    except Exception:
        return []


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

    # 登入失敗鎖定（避免暴力破解）
    MAX_FAILS = 5
    WINDOW_SEC = 15 * 60
    LOCK_SEC = 15 * 60

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        ip = client_ip()

        key = f"{username}|{ip}"
        st = load_auth_state()
        entry = st.get(key, {'fails': [], 'locked_until': 0})
        now = _now_ts()

        if entry.get('locked_until', 0) > now:
            remain = int(entry['locked_until'] - now)
            mins = max(1, (remain + 59) // 60)
            audit('login_locked', actor_id=username, detail={'mins': mins})
            flash(f'此帳號嘗試次數過多，已暫時鎖定 {mins} 分鐘，請稍後再試或聯繫管理員。', 'error')
            return render_template('login.html')

        user_data = USERS.get(username)
        ok = bool(user_data and check_password_hash(user_data.get('password_hash', ''), password))

        if ok:
            st[key] = {'fails': [], 'locked_until': 0}
            save_auth_state(st)

            user = User(user_data)
            login_user(user)
            session.permanent = True
            audit('login_success', actor_id=user.id)
            flash(f'歡迎回來，{user.name}！', 'success')
            return redirect(url_for('index'))

        fails = [t for t in entry.get('fails', []) if isinstance(t, int) and now - t <= WINDOW_SEC]
        fails.append(now)
        locked_until = 0
        if len(fails) >= MAX_FAILS:
            locked_until = now + LOCK_SEC
        st[key] = {'fails': fails, 'locked_until': locked_until}
        save_auth_state(st)
        audit('login_fail', actor_id=username, detail={'fail_count': len(fails), 'locked': bool(locked_until)})
        flash('帳號或密碼錯誤', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    audit('logout', actor_id=current_user.id if current_user.is_authenticated else '')
    logout_user()
    flash('已登出', 'info')
    return redirect(url_for('login'))


@app.before_request
def force_password_change():
    """若帳號仍為臨時密碼，強制導向修改密碼頁。"""
    try:
        if current_user.is_authenticated:
            u = USERS.get(current_user.id)
            if u and u.get('password_temp'):
                # 允許的 endpoint
                allow = {'change_password', 'logout', 'static', 'login'}
                if request.endpoint not in allow and not (request.path or '').startswith('/static'):
                    return redirect(url_for('change_password'))
    except Exception:
        pass


def _validate_new_password(pw: str):
    """基本密碼規則：至少 8 碼，且同時包含英文字母與數字。"""
    if not pw or len(pw) < 8:
        return False, '密碼長度需至少 8 碼'
    has_alpha = any(c.isalpha() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    if not (has_alpha and has_digit):
        return False, '密碼需同時包含英文字母與數字'
    if ' ' in pw:
        return False, '密碼不可包含空白'
    return True, ''


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    u = USERS.get(current_user.id)
    if not u:
        flash('使用者不存在', 'error')
        return redirect(url_for('logout'))

    forced = bool(u.get('password_temp'))

    if request.method == 'POST':
        old_pw = request.form.get('old_password', '')
        new_pw = request.form.get('new_password', '')
        confirm_pw = request.form.get('confirm_password', '')

        if not check_password_hash(u.get('password_hash', ''), old_pw):
            flash('舊密碼不正確', 'error')
            return redirect(url_for('change_password'))
        if new_pw != confirm_pw:
            flash('新密碼與確認密碼不一致', 'error')
            return redirect(url_for('change_password'))
        ok, msg = _validate_new_password(new_pw)
        if not ok:
            flash(msg, 'error')
            return redirect(url_for('change_password'))

        u['password_hash'] = generate_password_hash(new_pw)
        u['password_temp'] = False
        USERS[current_user.id] = u
        save_users(USERS)
        refresh_employee_cache()
        audit('password_change', actor_id=current_user.id)
        flash('✅ 密碼已更新', 'success')
        return redirect(url_for('index'))

    return render_template('change_password.html', forced=forced)

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

        audit('report_submit', actor_id=current_user.id, target_id=employee_id, detail={'date': today, 'edit': bool(is_edit)})

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

# ===================== 稽核紀錄（管理員） =====================
@app.route('/admin/audit')
@login_required
def admin_audit():
    if current_user.role != 'admin':
        flash('無權限訪問', 'error')
        return redirect(url_for('index'))

    q_event = request.args.get('event', '').strip()
    q_actor = request.args.get('actor', '').strip()

    rows = tail_jsonl(AUDIT_LOG_FILE, max_lines=500)
    rows.sort(key=lambda r: r.get('ts', 0), reverse=True)

    def ok(r):
        if q_event and r.get('event') != q_event:
            return False
        if q_actor and r.get('actor_id') != q_actor:
            return False
        return True

    filtered = [r for r in rows if ok(r)][:300]

    events = sorted({r.get('event') for r in rows if r.get('event')})
    actors = sorted({r.get('actor_id') for r in rows if r.get('actor_id')})

    return render_template('admin_audit.html', rows=filtered, events=events, actors=actors, q_event=q_event, q_actor=q_actor)


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

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})


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

# ===================== Excel 匯出 =====================
@app.route('/export/excel')
@login_required
def export_excel():
    if current_user.role != 'admin':
        flash('無權限', 'error'); return redirect(url_for('index'))
    if not EXCEL_OK:
        flash('伺服器未安裝 openpyxl，無法匯出', 'error')
        return redirect(url_for('admin_dashboard'))

    date_param = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    date_dir = REPORTS_DIR / date_param
    reports = []
    if date_dir.exists():
        for f in sorted(date_dir.glob('*_report.json')):
            reports.append(json.loads(f.read_text(encoding='utf-8')))

    wb = openpyxl.Workbook()

    # ── 工作表一：摘要 ──
    ws_sum = wb.active
    ws_sum.title = '日報摘要'
    header_fill = PatternFill(fill_type='solid', fgColor='4F46E5')
    header_font = Font(bold=True, color='FFFFFF', size=11)
    thin = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    def hcell(ws, row, col, val, width=None):
        c = ws.cell(row=row, column=col, value=val)
        c.fill = header_fill; c.font = header_font
        c.alignment = Alignment(horizontal='center', vertical='center')
        c.border = thin
        if width: ws.column_dimensions[c.column_letter].width = width
        return c
    def dcell(ws, row, col, val):
        c = ws.cell(row=row, column=col, value=val)
        c.alignment = Alignment(vertical='center', wrap_text=True)
        c.border = thin; return c

    ws_sum.row_dimensions[1].height = 30
    hcell(ws_sum,1,1,'員工姓名',15); hcell(ws_sum,1,2,'部門',12)
    hcell(ws_sum,1,3,'提交時間',18); hcell(ws_sum,1,4,'工作項數',10)
    hcell(ws_sum,1,5,'計畫項數',10); hcell(ws_sum,1,6,'風險項數',10)
    hcell(ws_sum,1,7,'高風險數',10); hcell(ws_sum,1,8,'今日收穫',30)

    # 未提交員工
    submitted_ids = {r['employee_id'] for r in reports}
    for emp in EMPLOYEES:
        if emp['id'] not in submitted_ids:
            row = ws_sum.max_row + 1
            dcell(ws_sum, row, 1, emp['name'])
            dcell(ws_sum, row, 2, '未提交')
            for col in range(3, 9): dcell(ws_sum, row, col, '-')
            ws_sum.cell(row=row, column=2).font = Font(color='FF0000')

    for r in reports:
        high_count = sum(1 for ri in r.get('risk_items',[]) if ri.get('risk_level')=='high')
        row = ws_sum.max_row + 1
        dcell(ws_sum, row, 1, r['employee_name'])
        dcell(ws_sum, row, 2, r.get('department',''))
        dcell(ws_sum, row, 3, r['submit_time'])
        dcell(ws_sum, row, 4, len(r.get('work_items',[])))
        dcell(ws_sum, row, 5, len(r.get('plan_items',[])))
        dcell(ws_sum, row, 6, len(r.get('risk_items',[])))
        dcell(ws_sum, row, 7, high_count)
        dcell(ws_sum, row, 8, r.get('summary',{}).get('today_gain',''))
        if high_count > 0:
            ws_sum.cell(row=row, column=7).fill = PatternFill(fill_type='solid', fgColor='FEE2E2')
            ws_sum.cell(row=row, column=7).font = Font(color='991B1B', bold=True)

    # ── 工作表二：工作明細 ──
    ws_work = wb.create_sheet('工作明細')
    headers = ['員工','案場','工作類型','工作內容','進度%','工時','產出物','狀態']
    for i, h in enumerate(headers, 1):
        hcell(ws_work, 1, i, h, [12,15,10,40,8,8,20,10][i-1])
    ws_work.row_dimensions[1].height = 25
    for r in reports:
        for w in r.get('work_items', []):
            row = ws_work.max_row + 1
            dcell(ws_work, row, 1, r['employee_name'])
            dcell(ws_work, row, 2, w.get('case_id',''))
            dcell(ws_work, row, 3, w.get('work_type',''))
            dcell(ws_work, row, 4, w.get('work_content',''))
            dcell(ws_work, row, 5, w.get('progress',''))
            dcell(ws_work, row, 6, w.get('hours',''))
            dcell(ws_work, row, 7, w.get('output',''))
            dcell(ws_work, row, 8, w.get('status',''))

    # ── 工作表三：風險清單 ──
    ws_risk = wb.create_sheet('風險清單')
    rh = ['員工','案場','風險等級','風險說明','影響層面','需要協助']
    for i, h in enumerate(rh, 1):
        hcell(ws_risk, 1, i, h, [12,15,10,35,25,25][i-1])
    ws_risk.row_dimensions[1].height = 25
    risk_colors = {'high':'FEE2E2', 'medium':'FEF3C7', 'low':'DCFCE7'}
    for r in reports:
        for ri in r.get('risk_items', []):
            row = ws_risk.max_row + 1
            dcell(ws_risk, row, 1, r['employee_name'])
            dcell(ws_risk, row, 2, ri.get('case_id',''))
            lv = ri.get('risk_level','low')
            lv_text = {'high':'🔴 高風險','medium':'🟠 中風險','low':'🟢 低風險'}.get(lv, lv)
            c = dcell(ws_risk, row, 3, lv_text)
            c.fill = PatternFill(fill_type='solid', fgColor=risk_colors.get(lv,'FFFFFF'))
            dcell(ws_risk, row, 4, ri.get('risk_desc',''))
            dcell(ws_risk, row, 5, ri.get('risk_impact',''))
            dcell(ws_risk, row, 6, ri.get('need_help',''))

    buf = io.BytesIO()
    wb.save(buf); buf.seek(0)
    audit('export_excel', actor_id=current_user.id, detail={'date': date_param})
    filename = f"日報_{date_param}.xlsx"
    return send_file(buf, as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# ===================== 員工管理頁 =====================
@app.route('/admin/reset-password/<user_id>', methods=['POST'])
@login_required
def admin_reset_password(user_id):
    if current_user.role != 'admin':
        flash('無權限', 'error')
        return redirect(url_for('index'))

    if user_id not in USERS:
        flash('員工不存在', 'error')
        return redirect(url_for('admin_employees'))

    # 產生一次性臨時密碼（不在登入頁顯示；只回給管理員）
    import secrets
    temp_pw = secrets.token_urlsafe(9)  # 約 12~13 字元

    u = USERS[user_id]
    u['password_hash'] = generate_password_hash(temp_pw)
    u['password_temp'] = True
    USERS[user_id] = u
    save_users(USERS)
    refresh_employee_cache()

    audit('admin_reset_password', actor_id=current_user.id, target_id=user_id)
    flash(f'已重設 {u.get("name")} 的密碼。臨時密碼：{temp_pw}（請轉交本人並提醒登入後立即修改）', 'success')
    return redirect(url_for('admin_employees'))


@app.route('/admin/employees')
@login_required
def admin_employees():
    if current_user.role != 'admin':
        flash('無權限', 'error'); return redirect(url_for('index'))

    # 近 30 天提交統計
    today = datetime.now()
    stats = {}
    for emp in EMPLOYEES:
        stats[emp['id']] = {'name': emp['name'], 'total_days': 0, 'submit_days': 0, 'avg_work': 0}

    total_work_by_emp = {e['id']: [] for e in EMPLOYEES}
    for i in range(30):
        d = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        dd = REPORTS_DIR / d
        if not dd.exists(): continue
        for emp in EMPLOYEES:
            f = dd / f"{emp['id']}_report.json"
            stats[emp['id']]['total_days'] += 1
            if f.exists():
                stats[emp['id']]['submit_days'] += 1
                r = json.loads(f.read_text(encoding='utf-8'))
                total_work_by_emp[emp['id']].append(len(r.get('work_items', [])))

    for eid, wlist in total_work_by_emp.items():
        stats[eid]['avg_work'] = round(sum(wlist)/len(wlist), 1) if wlist else 0
        sd = stats[eid]['submit_days']
        td = stats[eid]['total_days']
        stats[eid]['rate'] = round(sd/td*100, 1) if td else 0

    return render_template('admin_employees.html',
        employees=EMPLOYEES, stats=stats)

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
    print("🔐 管理員帳號：admin（密碼請由管理員另行提供/保存）")
    print("👷 員工初始密碼：首次登入需修改（密碼不在此顯示）")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
