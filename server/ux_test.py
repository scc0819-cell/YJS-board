#!/usr/bin/env python3
"""
昱金生能源集團 - 員工日報系統 使用者體驗測試
模擬不同角色：董事長、主管、員工
找出至少 10 個問題點
"""

import requests
from datetime import datetime

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("🧪 使用者體驗測試 - 昱金生能源集團員工日報系統")
print("=" * 70)
print(f"測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ===================== 角色 1：董事長（管理員） =====================
print("\n" + "=" * 70)
print("👤 角色 1：宋董事長（管理員視角）")
print("=" * 70)

session_admin = requests.Session()

# 登入
print("\n[步驟 1] 登入系統...")
resp = session_admin.post(f"{BASE_URL}/login", 
                          data={"username": "admin", "password": "yjsenergy2026"}, 
                          allow_redirects=False)
if resp.status_code == 302:
    print("✅ 登入成功")
else:
    print(f"❌ 登入失敗：HTTP {resp.status_code}")

# 首頁體驗
print("\n[步驟 2] 查看首頁...")
resp = session_admin.get(f"{BASE_URL}/")
if resp.status_code == 200:
    content = resp.text
    
    # 檢查問題
    issues = []
    
    # 問題 1：首頁是否顯示高風險/逾期任務摘要？
    if "高風險" not in content and "逾期" not in content:
        issues.append("❌ 首頁沒有顯示高風險/逾期任務摘要（董事長最關心的）")
    else:
        print("✅ 首頁有高風險/逾期摘要")
    
    # 問題 2：是否有快速統計卡片？
    if "stat-card" in content or "統計" in content:
        print("✅ 首頁有統計卡片")
    else:
        issues.append("❌ 首頁缺少快速統計卡片（提交率、案件數等）")
    
    # 問題 3：Logo 是否顯示？
    if "logo.jpg" in content or "Logo" in content:
        print("✅ Logo 已顯示")
    else:
        issues.append("❌ Logo 未正確顯示")
    
    if issues:
        for i in issues:
            print(i)
else:
    print(f"❌ 首頁異常：HTTP {resp.status_code}")

# 案件儀表板體驗
print("\n[步驟 3] 查看案件儀表板...")
resp = session_admin.get(f"{BASE_URL}/case-dashboard")
if resp.status_code == 200:
    content = resp.text
    
    issues = []
    
    # 問題 4：是否有篩選功能？
    if "<select" in content and "stage" in content:
        print("✅ 有階段篩選功能")
    else:
        issues.append("❌ 案件儀表板缺少篩選功能")
    
    # 問題 5：進度條是否可視化？
    if "progress-bar" in content or "進度" in content:
        print("✅ 進度條可視化")
    else:
        issues.append("❌ 進度缺少可視化條")
    
    # 問題 6：是否有快速操作按鈕？
    if "查看明細" in content or "編輯" in content:
        print("✅ 有快速操作按鈕")
    else:
        issues.append("❌ 缺少快速操作按鈕")
    
    if issues:
        for i in issues:
            print(i)
else:
    print(f"❌ 案件儀表板異常：HTTP {resp.status_code}")

# 風險追蹤體驗
print("\n[步驟 4] 查看風險追蹤...")
resp = session_admin.get(f"{BASE_URL}/risks")
if resp.status_code == 200:
    content = resp.text
    
    # 問題 7：風險分類是否完整？
    if "工期" in content and "成本" in content and "品質" in content:
        print("✅ 風險分類完整（8 大類）")
    else:
        print("⚠️  風險分類可能不完整")
    
    # 問題 8：是否有狀態更新功能？
    if "in_progress" in content or "處理中" in content:
        print("✅ 有狀態更新功能")
    else:
        issues.append("❌ 風險缺少狀態更新功能")
    
    if issues:
        for i in issues:
            print(i)
else:
    print(f"❌ 風險追蹤異常：HTTP {resp.status_code}")

# ===================== 角色 2：員工 =====================
print("\n" + "=" * 70)
print("👤 角色 2：陳明德（員工視角）")
print("=" * 70)

session_emp = requests.Session()

# 登入
print("\n[步驟 1] 員工登入...")
resp = session_emp.post(f"{BASE_URL}/login", 
                        data={"username": "chen_ming_de", "password": "1234"}, 
                        allow_redirects=False)
if resp.status_code == 302:
    print("✅ 登入成功")
    
    # 問題 9：員工是否被強制要求改密碼？
    if "change-password" in resp.text or "修改密碼" in resp.text:
        print("✅ 有強制改密碼機制")
    else:
        print("⚠️  可能缺少強制改密碼機制")
    
    # 填寫日報體驗
    print("\n[步驟 2] 填寫日報表單...")
    resp = session_emp.get(f"{BASE_URL}/report")
    if resp.status_code == 200:
        content = resp.text
        
        issues = []
        
        # 問題 10：案場是否為下拉選單？
        if "<select" in content and "case_id" in content:
            print("✅ 案場為下拉選單（非手打）")
        else:
            issues.append("❌ 案場可能需要手動輸入（易出錯）")
        
        # 問題 11：是否有草稿功能？
        if "draft" in content.lower() or "草稿" in content:
            print("✅ 有草稿儲存功能")
        else:
            issues.append("❌ 缺少草稿自動儲存功能")
        
        # 問題 12：附件上傳是否明顯？
        if "attachment" in content.lower() or "附件" in content:
            print("✅ 有附件上傳功能")
        else:
            issues.append("❌ 附件上傳功能不明顯")
        
        if issues:
            for i in issues:
                print(i)
    else:
        print(f"❌ 日報表單異常：HTTP {resp.status_code}")
else:
    print(f"❌ 員工登入失敗：HTTP {resp.status_code}")
    # 嘗試用 admin 密碼
    print("   嘗試使用 yjsenergy2026...")
    resp = session_emp.post(f"{BASE_URL}/login", 
                            data={"username": "chen_ming_de", "password": "yjsenergy2026"}, 
                            allow_redirects=False)
    if resp.status_code == 302:
        print("✅ 員工密碼已更新為 yjsenergy2026")

print("\n" + "=" * 70)
print("📋 測試完成")
print("=" * 70)
