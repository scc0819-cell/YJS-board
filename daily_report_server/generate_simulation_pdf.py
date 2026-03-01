#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成模擬情境報告 PDF（豐富詳細版）
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

FONT_PATH = '/mnt/c/Windows/Fonts/msjh.ttc'
pdfmetrics.registerFont(TTFont('MicrosoftJhengHei', FONT_PATH))
pdfmetrics.registerFont(TTFont('MicrosoftJhengHei-Bold', FONT_PATH))

PRIMARY = HexColor('#1e3a5f')
PRIMARY_DARK = HexColor('#0f172a')
ACCENT = HexColor('#0ea5e9')
SUCCESS = HexColor('#10b981')
WARNING = HexColor('#f59e0b')
BG_LIGHT = HexColor('#f8fafc')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverTitle', parent=styles['Heading1'], fontName='MicrosoftJhengHei-Bold', fontSize=26, textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=30, leading=34))
styles.add(ParagraphStyle(name='CoverSubtitle', parent=styles['Heading2'], fontName='MicrosoftJhengHei', fontSize=15, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=40, leading=22))
styles.add(ParagraphStyle(name='ChapterTitle', parent=styles['Heading1'], fontName='MicrosoftJhengHei-Bold', fontSize=19, textColor=PRIMARY, spaceAfter=18, leading=26))
styles.add(ParagraphStyle(name='SectionTitle', parent=styles['Heading2'], fontName='MicrosoftJhengHei-Bold', fontSize=15, textColor=PRIMARY, spaceAfter=12, leading=22))
styles.add(ParagraphStyle(name='NormalTC', parent=styles['Normal'], fontName='MicrosoftJhengHei', fontSize=10, textColor=HexColor('#475569'), alignment=TA_JUSTIFY, leading=17))
styles.add(ParagraphStyle(name='BulletPoint', parent=styles['Normal'], fontName='MicrosoftJhengHei', fontSize=10, textColor=HexColor('#475569'), leftIndent=20, leading=16))
styles.add(ParagraphStyle(name='InfoBox', parent=styles['Normal'], fontName='MicrosoftJhengHei', fontSize=9, textColor=HexColor('#1e293b'), leftIndent=20, rightIndent=20, leading=14))
styles.add(ParagraphStyle(name='ExampleGood', parent=styles['Normal'], fontName='MicrosoftJhengHei', fontSize=9, textColor=SUCCESS, leftIndent=20, leading=14))
styles.add(ParagraphStyle(name='ExampleBad', parent=styles['Normal'], fontName='MicrosoftJhengHei', fontSize=9, textColor=HexColor('#dc2626'), leftIndent=20, leading=14))

def create_simulation_report():
    doc = SimpleDocTemplate("/home/yjsclaw/.openclaw/workspace/daily_report_server/docs/SIMULATION_REPORT.pdf", pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2.5*cm, bottomMargin=2*cm)
    story = []
    
    # 封面
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("📊 模擬情境報告", styles['CoverTitle']))
    story.append(Paragraph("系統正式上線後運作情境預覽", styles['CoverSubtitle']))
    story.append(Spacer(1, 1*cm))
    
    info_data = [['📅 生成時間', '2026-03-01'], ['🎯 目的', '讓董事長預覽系統運作'], ['⭐ 範例標準', '豐富詳細的優秀範例']]
    info_table = Table(info_data, colWidths=[4*cm, 6*cm])
    info_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (0, -1), 'MicrosoftJhengHei-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 11), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(info_table)
    story.append(Spacer(1, 2*cm))
    
    story.append(PageBreak())
    
    # 情境 1
    story.append(Paragraph("情境 1：員工提交日報（優秀範例）", styles['ChapterTitle']))
    story.append(Paragraph("楊宗衛提交仁豐國小日報 - 豐富詳細版", styles['SectionTitle']))
    
    meta_data = [['⏰ 時間', '2026-03-03 17:30'], ['👤 員工', '楊宗衛（23102）'], ['🏭 案場', '仁豐國小'], ['⭐ 品質', '✅ 優秀範例']]
    meta_table = Table(meta_data, colWidths=[3*cm, 7*cm])
    meta_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (0, -1), 'MicrosoftJhengHei-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(meta_table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("📋 日報內容（詳細豐富版）：", styles['SectionTitle']))
    
    content_items = [
        "<b>📍 案場名稱：</b>彰化縣福興鄉仁豐國民小學 - 屋頂型太陽光電系統（200kW）",
        "<b>📅 施工天數：</b>第 18 天（總工期 20 天）",
        "<b>👷 今日人員：</b>楊宗衛（負責人）、外包廠商 2 人（昱緯工程）<br/>工時：08:00-17:00（含午休 1 小時，實際 8 小時）",
        "<b>🌤️ 天氣狀況：</b>晴天，氣溫 22-28°C，東北風 2 級（適合施工）",
        "<b>🔧 工作項目：</b><br/>1. 光電板安裝（第 55-60 片，共 6 片）<br/>   - 位置：屋頂 A 區最後一排<br/>   - 型號：AUO 450W 單晶矽<br/>   - 固定方式：M8 不鏽鋼螺栓，扭力 25N-m<br/>   - 間距：片間距 2cm，符合熱膨脹預留<br/><br/>2. 直流側接線作業<br/>   - 完成 String 8-10 的 MC4 接頭壓接<br/>   - 使用工具：MC4 壓接鉗、剝線鉗<br/>   - 線徑：6mm² PV 專用線<br/>   - 極性檢查：正極（紅）、負極（黑）標示清晰<br/><br/>3. 逆變器安裝與測試<br/>   - 型號：SMA Sunny Tripower 10000TL<br/>   - 數量：2 台（並聯）<br/>   - 安裝位置：機房內牆面<br/>   - 接地測試：接地電阻 0.8Ω（標準<10Ω，合格）<br/><br/>4. 現場清潔整理<br/>   - 回收光電板包裝紙箱 6 箱<br/>   - 清理螺絲、線材餘料<br/>   - 工具清點歸位",
        "<b>📊 完成進度：</b>總進度 95%（已安裝 60/63 片）<br/>分項進度：<br/>• 光電板安裝：95%（60/63 片）<br/>• 支架安裝：100%（全部完成）<br/>• 直流側接線：90%（10/11 String）<br/>• 逆變器安裝：100%（2 台完成）<br/>• 交流側配線：80%（待台電審查後收尾）<br/>進度計算基準：以光電板安裝片數為主要指標",
        "<b>⚠️ 遭遇問題：</b><br/>問題 1：屋頂 A 區最後一排有輕微遮陰<br/>• 狀況：東北角水塔造成上午 9-10 點遮陰<br/>• 影響：約 3 片光電板（第 61-63 片）<br/>• 處理：已調整安裝角度，將影響降至最低<br/>• 建議：後續案場勘選時需更精確評估遮陰<br/><br/>問題 2：MC4 接頭庫存不足<br/>• 狀況：MC4 接頭剩餘 10 組，不足明日所需<br/>• 處理：已聯繫倉管林天睛補充<br/>• 需求：MC4 接頭 50 組、6mm² PV 線 100 公尺<br/>• 預計到貨：明日（3/4）上午 10 點前",
        "<b>📸 施工照片：</b>已上傳 8 張照片至系統<br/>1. 光電板安裝完成照（全景）<br/>2. MC4 接頭壓接特寫<br/>3. 逆變器安裝完成照<br/>4. 接地測試儀表讀數<br/>5-8. 各角度施工細節照",
        "<b>📅 明日計畫：</b><br/>1. 仁豐國小 - 收尾工作（預計 1 天）<br/>   - 完成最後 3 片光電板安裝（第 61-63 片）<br/>   - 完成剩餘 String 11 接線<br/>   - 系統整體測試（絕緣測試、極性檢查）<br/>   - 準備初驗文件（施工日誌、測試報告、材料清單）<br/>2. 馬偕護專 - 併聯申請跟催<br/>   - 電話聯繫台電彰化區處<br/>   - 確認審查進度<br/>   - 如未回覆，發送正式 Email 催促<br/>3. 材料補給<br/>   - 接收倉管配送的 MC4 接頭、PV 線<br/>   - 清點數量、檢查品質",
        "<b>🆘 需協助事項：</b><br/>1. 請倉管林天睛協助<br/>   • 項目：MC4 接頭 50 組、6mm² PV 線 100 公尺<br/>   • 需求時間：3/4（明）上午 10 點前<br/>   • 配送地點：仁豐國小<br/>2. 請設計部顏呈晞協助<br/>   • 項目：仁豐國小竣工圖面確認<br/>   • 需求時間：3/5（五）前<br/>   • 用途：初驗文件提交",
        "<b>💡 個人備註：</b><br/>• 仁豐國小案場整體順利，預計 3/5 可完成初驗<br/>• 水塔遮陰問題已記錄，未來勘選需更精確評估<br/>• 外包廠商昱緯工程配合度佳，施工品質良好"
    ]
    
    for item in content_items:
        story.append(Paragraph(f"✓ {item}", styles['BulletPoint']))
        story.append(Spacer(1, 8))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("✅ 系統動作：", styles['SectionTitle']))
    system_actions = ["日報成功提交（內容完整度：98%）", "進度自動更新為 95%", "觸發 AI 分析流程", "自動發送材料請求給倉管林天睛", "自動發送圖面確認請求給設計部顏呈晞"]
    for action in system_actions:
        story.append(Paragraph(f"• {action}", styles['BulletPoint']))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("💡 為什麼這是優秀範例？", styles['SectionTitle']))
    advantages = ["使用具體數字（片數、扭力、電阻、線徑）", "描述完整流程（準備→安裝→測試→清理）", "說明進度計算方式（60/63 片 = 95%）", "列出明確的問題與處理方式", "提出具體的協助請求（對象、項目、時間）", "上傳施工照片佐證", "包含個人觀察與建議"]
    for adv in advantages:
        story.append(Paragraph(f"✓ {adv}", styles['ExampleGood']))
    
    story.append(PageBreak())
    
    # 情境 2
    story.append(Paragraph("情境 2：AI 即時反饋（深度分析）", styles['ChapterTitle']))
    story.append(Paragraph("AI 分析日報並提供建議 - 參考歷史郵件理解案場脈絡", styles['SectionTitle']))
    
    meta2_data = [['⏰ 時間', '2026-03-03 18:00（提交後 30 分鐘）'], ['🎯 對象', '楊宗衛'], ['📊 分析來源', '今日日報 + 歷史郵件 23 封']]
    meta2_table = Table(meta2_data, colWidths=[3*cm, 7*cm])
    meta2_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (0, -1), 'MicrosoftJhengHei-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(meta2_table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("🤖 AI 工作建議（深度分析版）：", styles['SectionTitle']))
    
    ai_content = [
        "<b>✨ 今日工作亮點：</b><br/>1. 仁豐國小進度達到 95%，即將完工！<br/>   • 光電板安裝 60/63 片，剩餘 3 片預計明日完成<br/>   • 逆變器安裝完成，接地測試合格（0.8Ω）<br/>   • 整體進度落後原訂計畫 1 天，但可於明日追回<br/>2. 問題處理得當<br/>   • 水塔遮陰問題：已調整安裝角度，將影響降至最低<br/>   • MC4 接頭不足：已提前聯繫倉管補充<br/>   • 主動上傳 8 張施工照片，記錄完整<br/>3. 主動聯繫台電確認進度，積極度佳",
        "<b>💡 明日建議（優先順序）：</b><br/>【高優先】1. 仁豐國小初驗準備<br/>• 完成最後 3 片光電板安裝（第 61-63 片）<br/>• 完成剩餘 String 11 接線<br/>• 系統整體測試：絕緣測試（標準>1MΩ）、極性檢查、接地電阻複測<br/>• 初驗文件準備：施工日誌、測試報告、材料清單、竣工照片<br/>【中優先】2. 馬偕護專併聯申請<br/>• 09:30 電話聯繫台電彰化區處<br/>• 確認審查進度，詢問預計回覆時間<br/>• 如未獲明確回覆，於 14:00 發送正式 Email 催促<br/>【低優先】3. 材料接收<br/>• 10:00 接收倉管配送的 MC4 接頭、PV 線<br/>• 清點數量、檢查品質、簽收確認",
        "<b>⚠️ 注意事項（根據歷史郵件分析）：</b><br/>1. 仁豐國小 - 水塔遮陰問題<br/>   • 歷史脈絡：根據 2026-02-15 勘選報告，水塔遮陰已標註<br/>   • 建議處理：初驗前請設計部顏呈晞確認遮陰影響評估<br/>   • 文件準備：初驗時可能需要說明遮陰對發電量的影響<br/>   • 參考數據：設計階段預估遮陰損失約 2-3%<br/>2. 仁豐國小 - 初驗人員安排<br/>   • 預計初驗時間：2026-03-07（五）10:00<br/>   • 參與人員：學校總務主任、台電承辦人、楊宗衛、張億峖經理<br/>   • 準備事項：簡報資料、測試儀器、安全裝備<br/>3. 天氣預報<br/>   • 3/4（明）：晴天，18-27°C，適合戶外施工<br/>   • 3/5（五）：多雲，19-26°C，適合初驗<br/>   • 3/6-3/7（六 - 日）：可能有雨，建議避免戶外作業",
        "<b>📋 自動協助事項：</b><br/>已自動發送請求：<br/>✓ 倉管林天睛：MC4 接頭 50 組、6mm² PV 線 100 公尺（3/4 10:00 前）<br/>✓ 設計部顏呈晞：仁豐國小竣工圖面確認（3/5 前）<br/>我已幫你準備：施工日誌草稿、測試報告範本、初驗檢查清單",
        "<b>📈 進度預測：</b><br/>仁豐國小：<br/>• 當前進度：95%<br/>• 預計完工：2026-03-05（五）<br/>• 初驗時間：2026-03-07（五）10:00<br/>• 併聯審查：2026-03-10（一）起<br/>• 預計掛表：2026-03-17（一）<br/>風險評估：<br/>• 進度風險：低（剩餘工作明確，人員充足）<br/>• 天氣風險：低（未來 3 天天氣良好）<br/>• 材料風險：低（已安排明日配送）<br/>• 審查風險：中（台電審查時間不確定）",
        "<b>🎯 總結：</b><br/>今日工作紮實，進度良好！明日專注於收尾和初驗準備，預計 3/5 可完成初驗。<br/>水塔遮陰問題已妥善處理，初驗時可能需要補充說明。<br/>需要協助嗎？隨時告訴我！"
    ]
    
    for item in ai_content:
        story.append(Paragraph(item, styles['InfoBox']))
        story.append(Spacer(1, 15))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("💡 AI 學習機制：", styles['SectionTitle']))
    ai_features = ["分析歷史郵件 23 封理解案場脈絡（勘選報告、會議記錄、廠商 correspondence）", "根據日報內容提供個人化建議（優先順序、具體步驟）", "參考天氣預報提醒施工安排", "連結系統資源（範本、清單、聯絡人）", "越用越精準 - 每次互動都會學習改進"]
    for feature in ai_features:
        story.append(Paragraph(f"• {feature}", styles['BulletPoint']))
    
    story.append(PageBreak())
    
    # 情境 3
    story.append(Paragraph("情境 3：董事長專屬報告", styles['ChapterTitle']))
    story.append(Paragraph("董事長查看每日報告 - 3 分鐘掌握全局", styles['SectionTitle']))
    
    meta3_data = [['⏰ 時間', '2026-03-04 08:00'], ['👤 對象', '宋啓綸 董事長']]
    meta3_table = Table(meta3_data, colWidths=[3*cm, 7*cm])
    meta3_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (0, -1), 'MicrosoftJhengHei-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(meta3_table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("📊 董事長專屬報告內容：", styles['SectionTitle']))
    report_content = """<b>今日摘要 - 2026-03-04</b><br/><br/>📊 團隊狀態：<br/>• 日報提交率：12/15 (80%) ✅<br/>  未提交：林天睛、呂宜芹、顏呈晞（行政/設計部）<br/>• 進行中案場：8 個 ✅<br/>• 新增高風險：0 個 ✅<br/><br/>🏭 各案場進度：<br/>✅ 仁豐國小：95% → 即將完工（3/5 初驗）<br/>✅ 馬偕護專：等待台電審查（預計 3/10）<br/>⚠️ 大城國小：85%（廠商延遲，已跟催）<br/>✅ 其他 5 案場：正常推進<br/><br/>🎯 需要您決策：<br/>• ✅ 無高風險項目<br/><br/>📬 補充請求（待判斷）：<br/>共 2 筆待確認：<br/>1. 楊宗衛：「水塔遮陰影響是否需要補充說明？」<br/>   您的判斷：[需要 / 不需要]<br/>2. 陳明德：「馬偕護專驗收人員安排確認」<br/>   您的判斷：[需要 / 不需要]<br/><br/>🤖 AI 綜合建議：<br/>• 整體進度良好，無重大風險<br/>• 仁豐國小預計本週完工，注意初驗準備<br/>• 注意下週天氣變化（3/6-3/7 可能有雨）<br/>• 大城國小廠商延遲問題，建議跟催"""
    story.append(Paragraph(report_content, styles['InfoBox']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("⏱️ 董事長操作時間：僅需 3 分鐘", styles['SectionTitle']))
    time_breakdown = ["1 分鐘：掃描今日摘要（提交率、案場進度、風險）", "1 分鐘：回覆補充請求（點擊「需要」或「不需要」）", "1 分鐘：掌握全局，開始一天工作"]
    for item in time_breakdown:
        story.append(Paragraph(f"• {item}", styles['BulletPoint']))
    
    story.append(PageBreak())
    
    # 情境 4
    story.append(Paragraph("情境 4：補充請求追蹤", styles['ChapterTitle']))
    
    timeline = [
        ("📬 Step 1", "AI 發送補充請求", "時間：2026-03-04 09:00<br/>對象：楊宗衛<br/>請求內容：「楊宗衛你好，AI 分析歷史郵件發現仁豐國小勘選報告中有標註水塔遮陰問題。你在日報中提到已調整安裝角度，請問：<br/>1. 遮陰影響範圍從原預估的 5 片減少到幾片？<br/>2. 調整後的安裝角度是多少度？<br/>3. 是否需要設計部補充遮陰影響評估報告？<br/>請於 3 天內（3/7 前）回覆，謝謝！」"),
        ("✍️ Step 2", "員工回覆", "時間：2026-03-04 14:00<br/>楊宗衛回覆：「AI 你好，回覆如下：<br/>1. 遮陰影響範圍：從原預估 5 片減少到 3 片（第 61-63 片）<br/>2. 調整後安裝角度：從 15 度調整為 18 度，避开水塔上午 9-10 點遮陰<br/>3. 遮陰影響評估：建議需要，初驗時學校可能會問<br/>已通知設計部顏呈晞協助準備評估報告，預計 3/5 完成。」<br/>系統動作：<br/>✓ 員工已回覆（2 小時內，快速）<br/>✓ AI 記憶更新（遮陰影響：3 片，角度：18 度）<br/>✓ 自動追蹤設計部報告進度"),
        ("✅ Step 3", "系統更新", "系統動作：<br/>✓ 員工已回覆（標記完成）<br/>✓ AI 記憶更新（案場知識庫 +1）<br/>✓ 董事長判斷：不需要（已標記）<br/>✓ 自動追蹤設計部報告（預計 3/5 完成）<br/>✓ 初驗檢查清單自動更新（加入遮陰評估報告）")
    ]
    
    for step_num, title, desc in timeline:
        story.append(Paragraph(f"<b>{step_num} {title}</b>", styles['SectionTitle']))
        story.append(Paragraph(desc, styles['NormalTC']))
        story.append(Spacer(1, 15))
    
    story.append(PageBreak())
    
    # 預期效益
    story.append(Paragraph("預期效益", styles['ChapterTitle']))
    
    benefit_data = [['90%', '100%', '75%', '15h'], ['進度掌握時間節省', '員工管理自動化', '會議時間減少', '每週節省 15 小時']]
    benefit_table = Table(benefit_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    benefit_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), PRIMARY), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'MicrosoftJhengHei-Bold'), ('FONTNAME', (0, 1), (-1, -1), 'MicrosoftJhengHei'), ('FONTSIZE', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 12), ('TOPPADDING', (0, 0), (-1, -1), 12), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
    story.append(benefit_table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("📊 年度總效益：每年節省 780 小時 = 32.5 天", styles['SectionTitle']))
    story.append(Paragraph("管理品質提升：即時性、準確性、完整性、決策依據全面升級", styles['InfoBox']))
    
    # 頁尾
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("報告結束", ParagraphStyle('Footer', parent=styles['Heading2'], fontName='MicrosoftJhengHei-Bold', fontSize=15, textColor=PRIMARY, alignment=TA_CENTER)))
    story.append(Spacer(1, 20))
    story.append(Paragraph("昱金生能源 AI 助理 為您服務", styles['NormalTC']))
    story.append(Spacer(1, 20))
    
    contact_data = [['📞 分機', '1234'], ['📧 Email', 'support@yujinsheng.com'], ['🤖 AI 助理', 'Jenny']]
    contact_table = Table(contact_data, colWidths=[4*cm, 6*cm])
    contact_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (0, -1), 'MicrosoftJhengHei-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 11), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
    story.append(contact_table)
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("© 2026 昱金生能源股份有限公司", ParagraphStyle('Copyright', parent=styles['Normal'], fontName='MicrosoftJhengHei', fontSize=9, textColor=colors.grey, alignment=TA_CENTER)))
    
    doc.build(story)
    print("✅ 模擬情境報告 PDF 已生成")

if __name__ == "__main__":
    create_simulation_report()
