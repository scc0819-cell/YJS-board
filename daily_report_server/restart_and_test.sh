#!/bin/bash
# 完全重啟日報系統並測試登入

echo "============================================================"
echo "🔄 重啟昱金生能源日報系統"
echo "============================================================"

# 1. 殺掉現有進程
echo "1️⃣  停止現有服務..."
pkill -9 -f "python3 app.py" 2>/dev/null || true
sleep 2

# 2. 確認已停止
echo "2️⃣  確認服務已停止..."
if pgrep -f "python3 app.py" > /dev/null; then
    echo "❌ 服務仍在運行，強制終止..."
    killall -9 python3 2>/dev/null || true
    sleep 2
fi

# 3. 設定密碼
echo "3️⃣  設定 admin 密碼..."
cd /home/yjsclaw/.openclaw/workspace/daily_report_server

python3 << 'PYTHON_EOF'
from werkzeug.security import generate_password_hash
import json
from pathlib import Path

USERS_FILE = Path('data/users.json')

with open(USERS_FILE, 'r', encoding='utf-8') as f:
    users = json.load(f)

# 生成新密碼 hash
password = 'Welcome2026!'
password_hash = generate_password_hash(password, method='scrypt', salt_length=16)

# 更新 admin
users['admin']['password_hash'] = password_hash
users['admin']['password_temp'] = False
users['admin']['name'] = '宋啓綸'
users['admin']['department'] = '管理部'
users['admin']['enabled'] = True

# 儲存
tmp = USERS_FILE.with_suffix('.json.tmp')
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(users, f, ensure_ascii=False, indent=2)
tmp.replace(USERS_FILE)

print(f"✅ admin 密碼已設定為：{password}")
PYTHON_EOF

# 4. 刪除 auth_state
echo "4️⃣  清除登入鎖定狀態..."
rm -f data/auth_state.json

# 5. 啟動服務
echo "5️⃣  啟動服務..."
nohup python3 app.py > /tmp/server.log 2>&1 &
sleep 5

# 6. 確認服務運行
echo "6️⃣  確認服務運行..."
if pgrep -f "python3 app.py" > /dev/null; then
    echo "✅ 服務已啟動"
    ps aux | grep "python3 app.py" | grep -v grep
else
    echo "❌ 服務啟動失敗"
    tail -50 /tmp/server.log
    exit 1
fi

# 7. 測試登入
echo ""
echo "7️⃣  測試登入..."
RESULT=$(curl -s -X POST http://localhost:5000/login \
    -d "username=admin&password=Welcome2026!" \
    -c /tmp/test_cookies.txt \
    -w "%{http_code}" \
    -o /tmp/login_response.html)

if [ "$RESULT" = "302" ]; then
    echo "✅ 登入成功！HTTP 302 重定向"
    echo ""
    echo "============================================================"
    echo "🎉 登入測試成功！"
    echo "============================================================"
    echo ""
    echo "🔐 登入資訊:"
    echo "   帳號：admin"
    echo "   密碼：Welcome2026!"
    echo ""
    echo "🌐 登入網址：http://localhost:5000"
    echo ""
    echo "📊 Dashboard:"
    echo "   file:///mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/full_email_analysis/dashboard.html"
    echo ""
else
    echo "❌ 登入失敗！HTTP $RESULT"
    echo ""
    echo "回應內容:"
    grep -i "錯誤\|error\|失敗" /tmp/login_response.html | head -5
    echo ""
    echo "Server log:"
    tail -20 /tmp/server.log
fi

echo "============================================================"
