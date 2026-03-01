#!/usr/bin/env python3
"""
昱金生能源集團 - 員工日報系統 自動化測試腳本
測試項目：
1. 管理員登入
2. 案場總覽訪問
3. 案場明細更新
4. 風險追蹤
5. 案件儀表板
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
ADMIN_ID = "admin"
ADMIN_PW = "yjsenergy2026"

session = requests.Session()

print("=" * 60)
print("🧪 昱金生能源集團 - 員工日報系統 自動化測試")
print("=" * 60)

# 1. 測試管理員登入
print("\n[1/6] 測試管理員登入...")
resp = session.post(f"{BASE_URL}/login", data={"username": ADMIN_ID, "password": ADMIN_PW}, allow_redirects=False)
if resp.status_code == 302:
    print("✅ 登入成功")
else:
    print(f"❌ 登入失敗：HTTP {resp.status_code}")
    exit(1)

# 2. 測試首頁訪問
print("\n[2/6] 測試首頁訪問...")
resp = session.get(f"{BASE_URL}/")
if resp.status_code == 200 and "昱金生" in resp.text:
    print("✅ 首頁正常")
else:
    print(f"❌ 首頁異常：HTTP {resp.status_code}")

# 3. 測試案場總覽
print("\n[3/6] 測試案場總覽 (/cases)...")
resp = session.get(f"{BASE_URL}/cases")
if resp.status_code == 200:
    if "案場" in resp.text or "仁豐" in resp.text:
        print("✅ 案場總覽正常（找到案場資料）")
    else:
        print("⚠️  案場總覽載入但無資料")
else:
    print(f"❌ 案場總覽異常：HTTP {resp.status_code}")

# 4. 測試風險追蹤
print("\n[4/6] 測試風險追蹤 (/risks)...")
resp = session.get(f"{BASE_URL}/risks")
if resp.status_code == 200:
    print("✅ 風險追蹤頁面正常")
else:
    print(f"❌ 風險追蹤異常：HTTP {resp.status_code}")

# 5. 測試案件儀表板
print("\n[5/6] 測試案件儀表板 (/case-dashboard)...")
resp = session.get(f"{BASE_URL}/case-dashboard")
if resp.status_code == 200:
    if "案件進度儀表板" in resp.text or "里程碑" in resp.text:
        print("✅ 案件儀表板正常")
    else:
        print("⚠️  案件儀表板載入但內容異常")
else:
    print(f"❌ 案件儀表板異常：HTTP {resp.status_code}")

# 6. 測試 AI API
print("\n[6/6] 測試 AI API (/api/ai/overview)...")
resp = session.get(f"{BASE_URL}/api/ai/overview")
if resp.status_code == 200:
    try:
        data = resp.json()
        if "cases" in data:
            print(f"✅ AI API 正常（返回 {len(data['cases'])} 個案件）")
        else:
            print("⚠️  AI API 返回格式異常")
    except:
        print("⚠️  AI API 返回非 JSON")
else:
    print(f"❌ AI API 異常：HTTP {resp.status_code}")

# 資料庫檢查
print("\n" + "=" * 60)
print("📊 資料庫狀態檢查")
print("=" * 60)

import sqlite3
db_path = "/home/yjsclaw/.openclaw/workspace/server/data/app.db"
try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # 案件數量
    cur.execute("SELECT COUNT(*) as cnt FROM case_status")
    case_count = cur.fetchone()['cnt']
    print(f"✅ 案件總數：{case_count}")
    
    # 風險數量
    cur.execute("SELECT COUNT(*) as cnt FROM risk_items WHERE status != 'closed'")
    risk_count = cur.fetchone()['cnt']
    print(f"✅ 未結案風險：{risk_count}")
    
    # 任務數量
    cur.execute("SELECT COUNT(*) as cnt FROM tasks WHERE status != 'closed'")
    task_count = cur.fetchone()['cnt']
    print(f"✅ 未結案任務：{task_count}")
    
    # 最近日報
    cur.execute("SELECT MAX(report_date) as last_date FROM reports")
    last_report = cur.fetchone()['last_date']
    print(f"✅ 最近日報日期：{last_report or '無資料'}")
    
    # 里程碑分佈
    cur.execute("SELECT stage, COUNT(*) as cnt FROM case_status GROUP BY stage")
    stages = cur.fetchall()
    print("\n📋 里程碑分佈:")
    for s in stages:
        print(f"   - {s['stage'] or '未設定'}: {s['cnt']} 件")
    
    conn.close()
except Exception as e:
    print(f"❌ 資料庫檢查失敗：{e}")

print("\n" + "=" * 60)
print("✅ 測試完成！")
print("=" * 60)
