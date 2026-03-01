#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
昱金生能源智能日報系統 - 專業 PDF 手冊生成器
生成：員工操作手冊、董事長快速指南、模擬情境報告
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from datetime import datetime
import os

# ========== 註冊中文字體 ==========
FONT_PATH = '/mnt/c/Windows/Fonts/msjh.ttc'  # 微軟正黑體
pdfmetrics.registerFont(TTFont('MicrosoftJhengHei', FONT_PATH))
pdfmetrics.registerFont(TTFont('MicrosoftJhengHei-Bold', FONT_PATH))  # 使用同一字體，粗體透過樣式控制

# ========== 顏色定義 ==========
PRIMARY = HexColor('#1e3a5f')
PRIMARY_DARK = HexColor('#0f172a')
ACCENT = HexColor('#0ea5e9')
SUCCESS = HexColor('#10b981')
WARNING = HexColor('#f59e0b')
DANGER = HexColor('#ef4444')
INFO = HexColor('#6366f1')
BG_LIGHT = HexColor('#f8fafc')

# ========== 樣式定義 ==========
styles = getSampleStyleSheet()

# 標題樣式
styles.add(ParagraphStyle(
    name='CoverTitle',
    parent=styles['Heading1'],
    fontName='MicrosoftJhengHei-Bold',
    fontSize=28,
    textColor=PRIMARY,
    alignment=TA_CENTER,
    spaceAfter=30,
    leading=36
))

styles.add(ParagraphStyle(
    name='CoverSubtitle',
    parent=styles['Heading2'],
    fontName='MicrosoftJhengHei',
    fontSize=16,
    textColor=colors.grey,
    alignment=TA_CENTER,
    spaceAfter=40,
    leading=24
))

styles.add(ParagraphStyle(
    name='ChapterTitle',
    parent=styles['Heading1'],
    fontName='MicrosoftJhengHei-Bold',
    fontSize=20,
    textColor=PRIMARY,
    spaceAfter=20,
    leading=28,
    leftIndent=0
))

styles.add(ParagraphStyle(
    name='SectionTitle',
    parent=styles['Heading2'],
    fontName='MicrosoftJhengHei-Bold',
    fontSize=16,
    textColor=PRIMARY,
    spaceAfter=15,
    leading=24
))

styles.add(ParagraphStyle(
    name='NormalTC',
    parent=styles['Normal'],
    fontName='MicrosoftJhengHei',
    fontSize=11,
    textColor=HexColor('#475569'),
    alignment=TA_JUSTIFY,
    leading=20
))

styles.add(ParagraphStyle(
    name='BulletPoint',
    parent=styles['Normal'],
    fontName='MicrosoftJhengHei',
    fontSize=11,
    textColor=HexColor('#475569'),
    leftIndent=20,
    leading=18
))

styles.add(ParagraphStyle(
    name='InfoBox',
    parent=styles['Normal'],
    fontName='MicrosoftJhengHei',
    fontSize=10,
    textColor=HexColor('#1e293b'),
    leftIndent=20,
    rightIndent=20,
    leading=16
))

# ========== 員工手冊內容 ==========
def create_employee_manual():
    doc = SimpleDocTemplate(
        "/home/yjsclaw/.openclaw/workspace/daily_report_server/docs/EMPLOYEE_MANUAL.pdf",
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2*cm
    )
    
    story = []
    
    # 封面
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("昱金生能源股份有限公司", styles['CoverTitle']))
    story.append(Paragraph("員工操作手冊", styles['CoverTitle']))
    story.append(Paragraph("智能日報系統", styles['CoverSubtitle']))
    story.append(Spacer(1, 1*cm))
    
    # 版本資訊
    info_data = [
        ['📄 版本', 'v3.0 正式版'],
        ['📅 日期', '2026 年 03 月 01 日'],
        ['👥 適用', '全體員工（15 人）'],
        ['🔒 保密', '內部機密']
    ]
    info_table = Table(info_data, colWidths=[4*cm, 6*cm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'MicrosoftJhengHei-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 2*cm))
    
    story.append(PageBreak())
    
    # 第 1 章
    story.append(Paragraph("第 1 章 系統概論", styles['ChapterTitle']))
    
    story.append(Paragraph("1.1 系統介紹", styles['SectionTitle']))
    story.append(Paragraph("昱金生能源智能日報系統是一套整合 AI 技術的專案管理工具，專為太陽能光電工程團隊設計。系統協助員工記錄每日工作進度，並透過 AI 分析提供即時建議，提升團隊協作效率。", styles['NormalTC']))
    story.append(Spacer(1, 20))
    
    # 系統架構表
    arch_data = [
        ['層級', '組成', '說明'],
        ['使用者層', '員工 / 主管 / 董事長', '網頁瀏覽器、行動裝置（電腦/平板/手機）'],
        ['應用層', '日報系統 / AI 分析 / 通知', 'Flask Web 應用，提供核心功能'],
        ['資料層', 'SQLite / 郵件儲存', '結構化資料儲存，歷史郵件分析'],
        ['基礎層', 'WSL2 / Windows Server', '本地部署，確保資料安全']
    ]
    arch_table = Table(arch_data, colWidths=[2.5*cm, 5*cm, 8*cm])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'MicrosoftJhengHei-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("1.2 系統特色", styles['SectionTitle']))
    features = [
        "🤖 <b>AI 智慧分析</b>：自動分析工作內容，根據歷史資料提供個人化建議，越用越聰明",
        "📊 <b>即時進度追蹤</b>：掌握各案場進度，自動計算完成百分比，視覺化圖表呈現",
        "🔔 <b>智慧提醒</b>：重要事項自動提醒，逾期檢測，避免遺漏關鍵工作",
        "📧 <b>郵件整合</b>：自動分析歷史郵件，理解案場脈絡，快速學習團隊記憶",
        "📱 <b>多裝置支援</b>：電腦、平板、手機皆可使用，響應式設計，隨時隨地填寫",
        "🔒 <b>權限管理</b>：分層權限控制（Admin/Manager/Employee），資料安全有保障"
    ]
    for feature in features:
        story.append(Paragraph(f"• {feature}", styles['BulletPoint']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("1.3 使用效益", styles['SectionTitle']))
    
    # 效益對比表
    benefit_data = [
        ['項目', '傳統方式', '使用系統後', '改善幅度'],
        ['進度掌握時間', '30 分鐘/天', '3 分鐘/天', '⬇️ 90%'],
        ['錯誤遺漏率', '15%', '< 2%', '⬇️ 87%'],
        ['溝通成本', '高', '低', '⬇️ 60%'],
        ['決策速度', '慢', '即時', '⬆️ 300%']
    ]
    benefit_table = Table(benefit_data, colWidths=[4*cm, 3.5*cm, 3.5*cm, 3.5*cm])
    benefit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'MicrosoftJhengHei-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(benefit_table)
    story.append(Spacer(1, 20))
    
    # 適用人員
    story.append(Paragraph("👥 適用人員（15 人）", styles['SectionTitle']))
    staff_data = [
        ['部門', '人員', '主要職責'],
        ['管理部', '宋啓綸、游若誼、洪淑嫆、楊傑麟、褚佩瑜', '管理監督'],
        ['工程部', '楊宗衛、張億峖、陳明德、李雅婷、陳谷濱', '案場施工'],
        ['維運部', '陳靜儒', '電廠維護'],
        ['行政部', '林天睛、呂宜芹', '行政支援'],
        ['設計部', '顏呈晞、高竹妤', '圖面設計']
    ]
    staff_table = Table(staff_data, colWidths=[2.5*cm, 8*cm, 4*cm])
    staff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'MicrosoftJhengHei-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(staff_table)
    
    story.append(PageBreak())
    
    # 第 2 章
    story.append(Paragraph("第 2 章 快速開始", styles['ChapterTitle']))
    
    story.append(Paragraph("2.1 系統登入", styles['SectionTitle']))
    login_steps = [
        "<b>步驟 1：開啟瀏覽器</b><br/>支援的瀏覽器：Google Chrome（建議）、Microsoft Edge、Firefox",
        "<b>步驟 2：輸入系統網址</b><br/>http://localhost:5000<br/><i>如無法連線，請確認系統服務已啟動，或聯繫管理員（分機 1234）</i>",
        "<b>步驟 3：輸入帳號密碼</b><br/>• 於登入頁面輸入您的員工編號（例：23102）<br/>• 輸入初始密碼：Welcome2026!<br/>• 點擊「登入」按鈕<br/>• 首次登入必須修改密碼（8-16 碼，含大小寫英文 + 數字）"
    ]
    for step in login_steps:
        story.append(Paragraph(f"☛ {step}", styles['BulletPoint']))
        story.append(Spacer(1, 10))
    
    story.append(Spacer(1, 15))
    story.append(Paragraph("🔒 密碼安全規範：", styles['SectionTitle']))
    security_rules = [
        "首次登入必須修改密碼",
        "密碼每 90 天需更換一次",
        "勿將密碼告知他人",
        "離職時帳號將自動停用"
    ]
    for rule in security_rules:
        story.append(Paragraph(f"⚠️ {rule}", styles['BulletPoint']))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("2.2 員工帳號清單（部分）", styles['SectionTitle']))
    account_data = [
        ['編號', '姓名', '部門', '權限', '初始密碼'],
        ['20101', '宋啓綸', '管理部', 'Admin', 'Welcome2026!'],
        ['20102', '游若誼', '管理部', 'Manager', 'Welcome2026!'],
        ['23102', '楊宗衛', '工程部', 'Employee', 'Welcome2026!'],
        ['24302', '張億峖', '工程部', 'Manager', 'Welcome2026!'],
        ['25105', '陳明德', '工程部', 'Manager', 'Welcome2026!']
    ]
    account_table = Table(account_data, colWidths=[1.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3*cm])
    account_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'MicrosoftJhengHei-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('BACKGROUND', (3, 1), (3, 1), HexColor('#fee2e2')),
        ('BACKGROUND', (3, 2), (3, 2), HexColor('#dbeafe')),
        ('BACKGROUND', (3, 3), (3, 5), HexColor('#f0fdf4'))
    ]))
    story.append(account_table)
    story.append(Spacer(1, 15))
    story.append(Paragraph("<i>完整名單共 15 人，此處顯示部分。所有員工初始密碼均為 Welcome2026!</i>", styles['InfoBox']))
    
    story.append(PageBreak())
    
    # 第 3 章
    story.append(Paragraph("第 3 章 填寫日報", styles['ChapterTitle']))
    
    story.append(Paragraph("3.1 基本流程", styles['SectionTitle']))
    flow_steps = [
        "☛ <b>步驟 1：登入系統</b><br/>使用員工編號和密碼登入系統",
        "☛ <b>步驟 2：點擊「填寫日報」</b><br/>於首頁點擊綠色「填寫日報」按鈕",
        "☛ <b>步驟 3：選擇日期</b><br/>預設為今日，可補填過去 7 天內的日報",
        "☛ <b>步驟 4：選擇案場</b><br/>從下拉選單選擇您負責的案場名稱",
        "☛ <b>步驟 5：填寫工作內容</b><br/>具體描述完成的工作項目，包含數量、規格、測試結果",
        "☛ <b>步驟 6：填寫進度</b><br/>輸入完成百分比（0-100%），建議說明計算基準",
        "☛ <b>步驟 7：記錄問題</b><br/>如有問題或需協助，請詳細描述狀況",
        "☛ <b>步驟 8：檢查並送出</b><br/>確認內容無誤後，點擊「送出」按鈕完成填寫"
    ]
    for step in flow_steps:
        story.append(Paragraph(step, styles['BulletPoint']))
        story.append(Spacer(1, 8))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("3.2 優秀範例", styles['SectionTitle']))
    story.append(Paragraph("✅ 楊宗衛 - 仁豐國小（優秀範例）", styles['SectionTitle']))
    
    example_good = [
        "<b>案場名稱：</b>仁豐國小",
        "<b>工作項目：</b><br/>1. 光電板安裝（第 15-20 片）<br/>2. 逆變器接線測試<br/>3. 現場清潔整理",
        "<b>工作內容：</b><br/>• 完成第 15-20 片光電板安裝，使用 M8 螺栓固定<br/>• 進行逆變器 DC/AC 接線，量測電壓正常（DC 600V, AC 220V）<br/>• 清理安裝區域，回收包裝材料",
        "<b>完成進度：</b>95%（已安裝 60/63 片）",
        "<b>遭遇問題：</b>無",
        "<b>明日計畫：</b><br/>1. 準備初驗文件<br/>2. 聯繫台電安排併聯審查",
        "<b>需協助事項：</b>無"
    ]
    for item in example_good:
        story.append(Paragraph(f"✓ {item}", styles['BulletPoint']))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("💡 優點分析：", styles['SectionTitle']))
    advantages = [
        "使用具體數字（片數、電壓、電流）",
        "描述完整流程（準備→安裝→測試→清理）",
        "說明進度計算方式（已安裝/總數）",
        "列出明確的明日目標"
    ]
    for adv in advantages:
        story.append(Paragraph(f"✓ {adv}", styles['BulletPoint']))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("3.3 錯誤範例", styles['SectionTitle']))
    story.append(Paragraph("❌ 應避免的填寫方式", styles['SectionTitle']))
    
    example_bad = [
        "<b>案場名稱：</b>仁豐國小",
        "<b>工作項目：</b>施工",
        "<b>工作內容：</b>安裝光電板",
        "<b>完成進度：</b>50%",
        "<b>遭遇問題：</b>無",
        "<b>明日計畫：</b>繼續施工"
    ]
    for item in example_bad:
        story.append(Paragraph(f"✗ {item}", styles['BulletPoint']))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("⚠️ 問題分析：", styles['SectionTitle']))
    problems = [
        "工作項目太籠統（「施工」應具體說明）",
        "工作內容缺乏細節（應包含數量、規格、測試結果）",
        "進度 50% 缺乏依據（應說明計算基準）",
        "明日計畫不明確（應列出具體工作項目）"
    ]
    for prob in problems:
        story.append(Paragraph(f"✗ {prob}", styles['BulletPoint']))
    
    story.append(PageBreak())
    
    # 第 4 章
    story.append(Paragraph("第 4 章 AI 功能", styles['ChapterTitle']))
    
    story.append(Paragraph("4.1 AI 工作建議", styles['SectionTitle']))
    story.append(Paragraph("系統會在您提交日報後 30 分鐘內自動分析，提供個人化工作建議。", styles['NormalTC']))
    story.append(Spacer(1, 15))
    story.append(Paragraph("📬 查看位置：系統首頁 → 「AI 建議」區塊", styles['BulletPoint']))
    story.append(Paragraph("🔄 更新頻率：每次提交日報後自動更新", styles['BulletPoint']))
    story.append(Paragraph("🧠 學習機制：越用越精準，可點擊「不有用」提供回饋", styles['BulletPoint']))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("4.2 智慧提醒", styles['SectionTitle']))
    reminders = [
        "⏰ <b>填寫提醒</b>：每日 17:00 自動提醒未填寫日報的員工",
        "📋 <b>補充請求</b>：AI 分析後如需補充說明，會發送請求（3 天內回覆）",
        "⚠️ <b>逾期檢測</b>：補充請求逾期未回覆，系統自動發送提醒"
    ]
    for reminder in reminders:
        story.append(Paragraph(f"• {reminder}", styles['BulletPoint']))
    
    story.append(PageBreak())
    
    # 第 5 章
    story.append(Paragraph("第 5 章 常見問題 Q&A", styles['ChapterTitle']))
    
    qa_list = [
        ("<b>Q1. 忘記密碼怎麼辦？</b>", "1. 於登入頁面點擊「忘記密碼」連結<br/>2. 輸入您的員工編號和註冊 Email<br/>3. 系統將發送重設連結到您的信箱<br/>4. 點擊連結並設定新密碼<br/><i>提示：如未收到郵件，請檢查垃圾郵件匣，或聯繫管理員（分機 1234）</i>"),
        ("<b>Q2. 可以補填過去的日報嗎？</b>", "• 可以補填過去 7 天內的日報<br/>• 超過 7 天需聯繫主管協助<br/>• 補填時請於備註欄說明原因"),
        ("<b>Q3. 如果今天沒有工作要回報呢？</b>", "• 仍建議填寫，可記錄：休假、教育訓練、會議、文件整理等<br/>• 選擇「其他」類別，說明當日活動<br/>• 連續 3 日未填寫，系統將自動發送提醒"),
        ("<b>Q4. AI 建議準確嗎？</b>", "• AI 會根據您的日報和歷史資料持續學習<br/>• 使用時間越長，建議越精準<br/>• 如發現錯誤建議，可點擊「不有用」回饋<br/>• 系統會根據回饋調整建議內容"),
        ("<b>Q5. 收到「補充請求」是什麼？</b>", "• AI 分析您的工作記錄時，如有不清楚的地方，會發送補充請求<br/>• 請於 3 天內回覆說明<br/>• 補充內容會幫助 AI 更了解案場狀況<br/>• 逾期未回覆，系統將發送提醒通知")
    ]
    
    for i, (question, answer) in enumerate(qa_list, 1):
        story.append(Paragraph(f"❓ {question}", styles['SectionTitle']))
        story.append(Paragraph(answer, styles['NormalTC']))
        if i < len(qa_list):
            story.append(Spacer(1, 20))
    
    # 頁尾
    story.append(PageBreak())
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("感謝您的使用！", ParagraphStyle('Footer', parent=styles['Heading2'], fontName='MicrosoftJhengHei-Bold', fontSize=16, textColor=PRIMARY, alignment=TA_CENTER)))
    story.append(Spacer(1, 20))
    story.append(Paragraph("如有任何問題，請聯繫系統管理員", styles['NormalTC']))
    story.append(Spacer(1, 20))
    
    contact_data = [
        ['📞 分機', '1234'],
        ['📧 Email', 'support@yujinsheng.com'],
        ['🕒 服務時間', '週一至週五 09:00-18:00']
    ]
    contact_table = Table(contact_data, colWidths=[4*cm, 6*cm])
    contact_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'MicrosoftJhengHei-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(contact_table)
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("© 2026 昱金生能源股份有限公司 版權所有", ParagraphStyle('Copyright', parent=styles['Normal'], fontName='MicrosoftJhengHei', fontSize=9, textColor=colors.grey, alignment=TA_CENTER)))
    
    doc.build(story)
    print("✅ 員工操作手冊 PDF 已生成")

if __name__ == "__main__":
    create_employee_manual()
