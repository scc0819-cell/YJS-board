#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
昱金生能源 - AI 記憶注入系統
將郵件解析結果注入 AI 記憶系統
"""

import json
from pathlib import Path
from datetime import datetime

# 輸入檔案
INPUT_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/full_email_analysis')
MEMORY_FILE = Path('/home/yjsclaw/.openclaw/workspace/memory/2026-03-01.md')
MEMORY_LONG_TERM = Path('/home/yjsclaw/.openclaw/workspace/MEMORY.md')

def load_case_database():
    """載入案場資料庫"""
    case_db_file = INPUT_DIR / 'case_database.json'
    with open(case_db_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_employee_database():
    """載入員工資料庫"""
    emp_db_file = INPUT_DIR / 'employee_database.json'
    with open(emp_db_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_full_report():
    """載入完整報告"""
    report_file = INPUT_DIR / 'full_analysis_report_20260301_051808.json'
    with open(report_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_ai_memory_summary(case_db, emp_db, report):
    """生成 AI 記憶摘要"""
    
    summary = []
    summary.append("="*70)
    summary.append("🧠 AI 記憶注入 - 郵件解析系統知識庫")
    summary.append("="*70)
    summary.append(f"注入時間：{datetime.now().isoformat()}")
    summary.append(f"資料來源：2,783 封郵件完整解析\n")
    
    # 案場知識
    summary.append("## 🏭 案場知識庫（401 個案場）")
    summary.append("-"*50)
    summary.append("\n### 前 20 大活躍案場（重點記憶）\n")
    
    sorted_cases = sorted(case_db.items(), key=lambda x: x[1].get('timeline_count', 0), reverse=True)[:20]
    
    for i, (case_name, case_info) in enumerate(sorted_cases, 1):
        summary.append(f"{i}. **{case_name}**")
        summary.append(f"   - 郵件數：{case_info.get('timeline_count', 0)} 封")
        summary.append(f"   - 問題記錄：{case_info.get('issue_count', 0)} 件")
        summary.append(f"   - 負責員工：{', '.join(case_info.get('employees', []))}")
        if case_info.get('issues_sample'):
            summary.append(f"   - 常見問題：{case_info['issues_sample'][0].get('description', 'N/A')[:100]}")
        summary.append("")
    
    # 員工知識
    summary.append("\n## 👥 員工知識庫（10 位活躍員工）")
    summary.append("-"*50)
    summary.append("\n### 員工專長與工作模式\n")
    
    sorted_emps = sorted(emp_db.items(), key=lambda x: x[1].get('total_emails', 0), reverse=True)
    
    for emp_key, emp_info in sorted_emps:
        summary.append(f"### {emp_info.get('name', emp_key)} ({emp_info.get('dept', '未知')})")
        summary.append(f"- 系統 ID：`{emp_key}`")
        summary.append(f"- 總郵件：{emp_info.get('total_emails', 0)} 封")
        summary.append(f"- 日報數：{emp_info.get('daily_reports', 0)} 封")
        summary.append(f"- 負責案場：{len(emp_info.get('cases', []))} 個")
        summary.append(f"- 附件數：{emp_info.get('attachments', 0)} 個")
        
        if emp_info.get('cases'):
            summary.append(f"- 主要案場：{', '.join(emp_info['cases'][:5])}")
        
        # 工作模式分析
        if emp_info.get('daily_reports', 0) > 100:
            summary.append("- 📝 **工作模式**：勤奮提交日報，習慣詳細記錄")
        if emp_info.get('attachments', 0) > 100:
            summary.append("- 📎 **工作模式**：大量附件，可能是檢測報告或施工照片")
        if len(emp_info.get('cases', [])) > 30:
            summary.append("- 🏭 **工作模式**：跨多個案場，可能是管理職或設計支援")
        if emp_info.get('daily_reports', 0) == 0:
            summary.append("- 📋 **工作模式**：較少提交日報，可能是行政支援或其他工作類型")
        
        summary.append("")
    
    # 常見問題模式
    summary.append("\n## ⚠️ 常見問題模式")
    summary.append("-"*50)
    summary.append("\n從郵件中提取的常見問題類型：\n")
    
    summary.append("1. **電氣問題**")
    summary.append("   - 無電壓、無電流")
    summary.append("   - DC 箱異常")
    summary.append("   - 逆變器故障")
    summary.append("")
    summary.append("2. **施工問題**")
    summary.append("   - 物料延遲")
    summary.append("   - 天候影響")
    summary.append("   - 人力調度")
    summary.append("")
    summary.append("3. **行政問題**")
    summary.append("   - 請款作業")
    summary.append("   - 文件審查")
    summary.append("   - 協調會議")
    summary.append("")
    
    # 解決方案建議
    summary.append("\n## 💡 解決方案建議")
    summary.append("-"*50)
    summary.append("\n基於歷史郵件的解決方案模式：\n")
    
    summary.append("1. **無電壓/無電流問題**")
    summary.append("   - 檢查 DC 箱開關")
    summary.append("   - 測量電壓電流")
    summary.append("   - 檢查接線是否鬆脫")
    summary.append("   - 必要時更換設備")
    summary.append("")
    summary.append("2. **施工延遲**")
    summary.append("   - 確認物料到貨時間")
    summary.append("   - 調整施工順序")
    summary.append("   - 增加人力支援")
    summary.append("   - 與業主協調")
    summary.append("")
    
    # 數據洞察
    summary.append("\n## 📊 數據洞察")
    summary.append("-"*50)
    summary.append("\n### 整體統計")
    summary.append(f"- 總郵件數：2,783 封")
    summary.append(f"- 日報郵件：1,553 封（55.8%）")
    summary.append(f"- 活躍員工：10 位")
    summary.append(f"- 運轉案場：401 個")
    summary.append(f"- 解析時間：7 分鐘")
    summary.append("")
    
    summary.append("### 關鍵發現")
    summary.append("- 陳明德負責最多案場（60 個），是工程部主力")
    summary.append("- 張億峖日報提交率 99.6%，工作習慣極佳")
    summary.append("- 陳靜儒負責維運案場，附件量大但日報少")
    summary.append("- 林天睛行政支援，日報提交率 99.5%")
    summary.append("- 高竹妤設計支援 43 個案場，跨案場最多")
    summary.append("")
    
    summary.append("### 案場分佈")
    summary.append("- 前 20 大案場佔總郵件 60%+")
    summary.append("- 04-720 是最活躍案場（149 封郵件）")
    summary.append("- 多數案場有 2-4 位負責人，顯示團隊協作")
    summary.append("")
    
    return '\n'.join(summary)


def inject_to_daily_memory(summary_text):
    """注入到每日記憶"""
    
    # 讀取現有記憶
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = f"# 📝 2026-03-01 記憶記錄\n\n**日期**: 2026-03-01\n\n"
    
    # 檢查是否已注入
    if "🧠 AI 記憶注入 - 郵件解析系統知識庫" in content:
        print("⚠️  AI 記憶已注入，跳過...")
        return
    
    # 添加到記憶末尾
    content += "\n\n"
    content += summary_text
    content += "\n\n---\n\n**AI 記憶注入完成**: " + datetime.now().isoformat()
    
    # 寫回檔案
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已注入到每日記憶：{MEMORY_FILE}")


def inject_to_long_term_memory(case_db, emp_db):
    """注入到長期記憶 (MEMORY.md)"""
    
    if MEMORY_LONG_TERM.exists():
        with open(MEMORY_LONG_TERM, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# 🧠 MEMORY.md — Jenny 的長期記憶\n\n"
    
    # 檢查是否已注入
    if "📧 郵件完整解析（2026-03-01）" in content:
        print("⚠️  長期記憶已更新，跳過...")
        return
    
    # 建立更新內容
    update_section = f"""

---

## 📧 郵件完整解析（2026-03-01）

**解析成果**:
- 總郵件：2,783 封
- 日報：1,553 封（55.8%）
- 員工：10 位活躍用戶
- 案場：401 個

**員工績效 TOP 3**:
1. 陳明德（工程部）- 294 封，負責 60 個案場
2. 張億峖（工程部）- 281 封，日報率 99.6%
3. 陳靜儒（維運部）- 249 封，維運報告為主

**前 5 大活躍案場**:
1. 04-720（149 封）- 陳谷濱負責
2. 02-2999（127 封）- 陳靜儒負責
3. 25-1（46 封）
4. 18-1（46 封）
5. 30-1（44 封）

**關鍵洞察**:
- 陳明德：案場冠軍，負責 60 個案場
- 張億峖：日報模範，提交率 99.6%
- 高竹妤：設計支援 43 個案場
- 陳靜儒：維運報告，附件量大

**輸出檔案**:
- `/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/full_email_analysis/`
- case_database.json（401 個案場）
- employee_database.json（10 位員工）
- full_analysis_report.json（完整報告）

"""
    
    # 添加到內容末尾
    content += update_section
    
    # 寫回檔案
    with open(MEMORY_LONG_TERM, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已注入到長期記憶：{MEMORY_LONG_TERM}")


def main():
    """主函數"""
    print("="*70)
    print("🧠 AI 記憶注入系統")
    print("="*70)
    print(f"\n開始時間：{datetime.now().isoformat()}\n")
    
    try:
        # 1. 載入資料
        print("📂 載入案場資料庫...")
        case_db = load_case_database()
        print(f"✅ 載入 {len(case_db)} 個案場")
        
        print("📂 載入員工資料庫...")
        emp_db = load_employee_database()
        print(f"✅ 載入 {len(emp_db)} 位員工")
        
        print("📂 載入完整報告...")
        report = load_full_report()
        print("✅ 載入完成\n")
        
        # 2. 生成 AI 記憶摘要
        print("🤖 生成 AI 記憶摘要...")
        summary = generate_ai_memory_summary(case_db, emp_db, report)
        print("✅ 摘要生成完成\n")
        
        # 3. 注入到每日記憶
        print("💾 注入到每日記憶...")
        inject_to_daily_memory(summary)
        
        # 4. 注入到長期記憶
        print("💾 注入到長期記憶...")
        inject_to_long_term_memory(case_db, emp_db)
        
        # 完成
        print("\n" + "="*70)
        print("✅✅✅ AI 記憶注入完成！")
        print("="*70)
        print(f"\n📁 更新檔案:")
        print(f"   - {MEMORY_FILE}")
        print(f"   - {MEMORY_LONG_TERM}")
        
        print(f"\n📊 注入內容:")
        print(f"   - 401 個案場知識")
        print(f"   - 10 位員工檔案")
        print(f"   - 常見問題模式")
        print(f"   - 解決方案建議")
        print(f"   - 數據洞察")
        
        print(f"\n結束時間：{datetime.now().isoformat()}")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ 錯誤：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
