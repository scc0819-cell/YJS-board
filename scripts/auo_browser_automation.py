#!/usr/bin/env python3
"""
昱金生能源 - AUO 電廠監控自動化腳本（使用 browser 工具）

執行流程：
1. 登入 AUO SunVeillance 系統
2. 掃描所有案場（共 9 頁）
3. 提取每個案場的詳細數據
4. 生成深度分析報告 + 建議
5. 每日 08:00 自動執行

登入資訊：
- 網址：https://gms.auo.com/MvcWebPortal
- 帳號：johnnys@yjsenergy.com
- 密碼：5295Song!
"""

# 這是 browser 自動化腳本的參考實現
# 實際執行需要使用 OpenClaw browser 工具

# 步驟 1: 登入系統
browser.navigate("https://gms.auo.com/MvcWebPortal")
browser.type(ref="e10", text="johnnys@yjsenergy.com")  # Email Account
browser.type(ref="e14", text="5295Song!")  # Password
browser.click(ref="e25")  # Log in button

# 步驟 2: 掃描所有案場（共 9 頁）
all_cases = []
for page in range(1, 10):
    # 如果是第 2 頁以後，點擊下一頁
    if page > 1:
        browser.click(ref="e467")  # 頁面 2
        # 或使用下一頁按鈕：browser.click(ref="e478")
    
    # 等待頁面載入
    browser.wait(timeMs=2000)
    
    # 提取當前頁面的案場數據
    cases = browser.evaluate("""
        Array.from(document.querySelectorAll('[ref^="e"][role="row"]')).slice(1).map(row => {
            const cells = row.querySelectorAll('[role="gridcell"]');
            return {
                name: cells[0]?.textContent?.trim() || '',
                alerts: cells[1]?.textContent?.trim() || '0',
                dr_no: cells[2]?.textContent?.trim() || '',
                site_id: cells[3]?.textContent?.trim() || '',
                capacity: parseFloat(cells[4]?.textContent?.trim()) || 0,
                version: cells[5]?.textContent?.trim() || '',
                installer: cells[6]?.textContent?.trim() || '',
                on_grid_date: cells[7]?.textContent?.trim() || '',
                last_report: cells[8]?.textContent?.trim() || '',
                city: cells[9]?.textContent?.trim() || '',
                county: cells[10]?.textContent?.trim() || ''
            };
        }).filter(c => c.name && !c.name.startsWith('View'));
    """)
    
    all_cases.extend(cases)
    print(f"第{page}頁：提取 {len(cases)} 個案場")

# 步驟 3: 分析數據
analysis = {
    'total_cases': len(all_cases),
    'total_capacity': sum(c['capacity'] for c in all_cases),
    'cases_with_alerts': [c for c in all_cases if c['alerts'] != '0' and c['alerts']],
    'by_county': {},
    'top_capacity': sorted(all_cases, key=lambda x: x['capacity'], reverse=True)[:10],
    'recent_reports': [c for c in all_cases if '2026/03/01' in c['last_report']]
}

# 統計各縣市案場數
for case in all_cases:
    county = case['county']
    if county:
        analysis['by_county'][county] = analysis['by_county'].get(county, 0) + 1

# 步驟 4: 生成報告
report = f"""# 🏭 AUO 友達電廠監控深度分析報告

**執行時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**數據來源**: AUO SunVeillance 監控系統
**登入帳號**: johnnys@yjsenergy.com

---

## 📊 系統總覽

| 指標 | 數值 |
|------|------|
| 監控案場總數 | {analysis['total_cases']} |
| 總裝置容量 | {analysis['total_capacity']:.2f} kW |
| 有異常案場 | {len(analysis['cases_with_alerts'])} |
| 今日有回報 | {len(analysis['recent_reports'])} |

---

## 🚨 異常案場清單

"""

if analysis['cases_with_alerts']:
    report += "| 案場名稱 | 異常數 | DR 編號 | 容量 (kW) | 最後回報 | 建議行動 |\n"
    report += "|----------|--------|---------|-----------|----------|----------|\n"
    for case in analysis['cases_with_alerts'][:20]:
        report += f"| {case['name']} | {case['alerts']} | {case['dr_no']} | {case['capacity']} | {case['last_report']} | 立即檢查 |\n"
else:
    report += "✅ 目前無異常案場\n"

report += f"""
---

## 📍 縣市分佈

| 縣市 | 案場數 | 佔比 |
|------|--------|------|
"""

for county, count in sorted(analysis['by_county'].items(), key=lambda x: -x[1]):
    percentage = count / analysis['total_cases'] * 100
    report += f"| {county} | {count} | {percentage:.1f}% |\n"

report += f"""
---

## 🔝 TOP 10 大容量案場

| 排名 | 案場名稱 | 容量 (kW) | DR 編號 | 縣市 |
|------|----------|-----------|---------|------|
"""

for i, case in enumerate(analysis['top_capacity'], 1):
    report += f"| {i} | {case['name']} | {case['capacity']} | {case['dr_no']} | {case['county']} |\n"

report += f"""
---

## 💡 建議行動

### 立即處理（24 小時內）

"""

if analysis['cases_with_alerts']:
    for i, case in enumerate(analysis['cases_with_alerts'][:5], 1):
        report += f"{i}. **{case['name']}** - {case['alerts']} 個異常，最後回報：{case['last_report']}\n"
else:
    report += "✅ 無需立即處理的異常\n"

report += """
### 本週跟進

1. 檢查所有今日無回報的案場
2. 檢視低效率案場（PR < 60%）
3. 更新案場聯絡人資訊

### 長期優化

1. 建立案場績效評比機制
2. 定期清理灰塵（尤其是畜牧場案場）
3. 優化逆變器設定

---

## 📋 監測頻率

- **每日監測**: 08:00 自動執行
- **異常告警**: 發現異常時立即通知
- **週報彙整**: 每週一 09:30

---

**下次更新**: 明日 08:00
"""

# 步驟 5: 儲存報告
with open(f'auo_analysis_{datetime.now().strftime("%Y%m%d")}.md', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✅ 報告已儲存：auo_analysis_{datetime.now().strftime('%Y%m%d')}.md")
