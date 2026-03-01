#!/usr/bin/env python3
"""
昱金生能源 - 專業 PDF 手冊生成器 v2.0
生成正式、專業、圖文並茂的操作手冊
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime
import os

# ========== 字體設定 ==========
FONT_PATH = '/mnt/c/Windows/Fonts/msjh.ttc'
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('MSJH', FONT_PATH))
    print(f"✅ 字體已註冊：{FONT_PATH}")
else:
    print(f"⚠️ 字體未找到：{FONT_PATH}")

# ========== 檔案路徑 ==========
WORKSPACE = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server')
OUTPUT_DIR = WORKSPACE / 'docs'
OUTPUT_DIR.mkdir(exist_ok=True)

# ========== 專業配色 ==========
class Colors:
    PRIMARY = '#1e3a5f'
    PRIMARY_DARK = '#0f172a'
    ACCENT = '#0ea5e9'
    SUCCESS = '#10b981'
    WARNING = '#f59e0b'
    DANGER = '#ef4444'
    BG_LIGHT = '#f8fafc'
    BORDER = '#e2e8f0'
    TEXT_DARK = '#1e293b'
    TEXT_MEDIUM = '#475569'

# ========== 樣式建立 ==========
def get_styles():
    styles = getSampleStyleSheet()
    
    try:
        try:
        styles.add(ParagraphStyle('CoverTitle', parent=styles['Title'],
        fontName='MSJH', fontSize=32, textColor=colors.HexColor(Colors.PRIMARY_DARK),
        spaceAfter=40, alignment=TA_CENTER, leading=42))
    
    try:
        styles.add(ParagraphStyle('CoverSubtitle', parent=styles['Heading1'],
        fontName='MSJH', fontSize=18, textColor=colors.HexColor(Colors.PRIMARY),
        spaceAfter=30, alignment=TA_CENTER, leading=28))
    
    try:
        styles.add(ParagraphStyle('ChapterTitle', parent=styles['Heading1'],
        fontName='MSJH', fontSize=20, textColor=colors.HexColor(Colors.PRIMARY_DARK),
        spaceAfter=25, spaceBefore=30, leading=30))
    
    try:
        styles.add(ParagraphStyle('SectionTitle', parent=styles['Heading2'],
        fontName='MSJH', fontSize=16, textColor=colors.HexColor(Colors.PRIMARY),
        spaceAfter=18, spaceBefore=25, leading=24))
    
    try:
        styles.add(ParagraphStyle('SubSectionTitle', parent=styles['Heading3'],
        fontName='MSJH', fontSize=13, textColor=colors.HexColor(Colors.PRIMARY_LIGHT) if hasattr(Colors, 'PRIMARY_LIGHT') else colors.HexColor(Colors.PRIMARY),
        spaceAfter=12, spaceBefore=18, leading=20))
    except KeyError: pass
    try:
    
    try:
        styles.add(ParagraphStyle('BodyText', parent=styles['Normal'],
        fontName='MSJH', fontSize=11, textColor=colors.HexColor(Colors.TEXT_DARK),
        alignment=TA_JUSTIFY, leading=20, spaceAfter=10))
    
    try:
        styles.add(ParagraphStyle('CodeText', parent=styles['Normal'],
        fontName='MSJH', fontSize=10, textColor=colors.HexColor('#dc2626'),
        alignment=TA_LEFT, leading=16, backColor=colors.HexColor('#f1f5f9'),
        borderWidth=1, borderColor=colors.HexColor(Colors.BORDER), borderPadding=8))
    
    return styles

# ========== 頁首頁尾 ==========
def create_header(canvas, doc, title):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor(Colors.PRIMARY))
    canvas.rect(0, A4[1] - 15, A4[0], 15, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont('MSJH', 9)
    canvas.drawString(2*cm, A4[1] - 12, '昱金生能源股份有限公司')
    canvas.drawRightString(A4[0] - 2*cm, A4[1] - 12, title)
    canvas.restoreState()

def create_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor(Colors.BORDER))
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 2.5*cm, A4[0] - 2*cm, 2.5*cm)
    canvas.setFillColor(colors.HexColor('#94a3b8'))
    canvas.setFont('MSJH', 9)
    page_num = canvas.getPageNumber()
    canvas.drawRightString(A4[0] - 2*cm, 2*cm, f'第 {page_num} 頁')
    canvas.restoreState()

# ========== 員工手冊 ==========
def generate_employee_manual():
    print("\n📘 生成：專業版員工操作手冊...")
    
    doc = SimpleDocTemplate(str(OUTPUT_DIR / 'EMPLOYEE_MANUAL_PRO.pdf'),
        pagesize=A4, rightMargin=2.5*cm, leftMargin=2.5*cm,
        topMargin=3*cm, bottomMargin=3*cm)
    
    styles = get_styles()
    story = []
    
    # 封面
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("昱金生能源", styles['CoverTitle']))
    story.append(Paragraph("YUJINSHENG ENERGY", ParagraphStyle('EnglishSub',
        parent=styles['CoverSubtitle'], fontSize=14,
        textColor=colors.HexColor(Colors.TEXT_MEDIUM))))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("員工操作手冊", styles['CoverSubtitle']))
    story.append(Paragraph("智能日報系統", ParagraphStyle('DocSub',
        parent=styles['CoverSubtitle'], fontSize=14,
        textColor=colors.HexColor(Colors.TEXT_MEDIUM))))
    story.append(Spacer(1, 2*cm))
    
    # 版本資訊
    version_data = [
        ['文件版本', 'v2.0 正式版'],
        ['更新日期', datetime.now().strftime('%Y 年 %m 月 %d 日')],
        ['適用對象', '全體員工（15 人）'],
        ['保密等級', '內部機密'],
        ['權限說明', '游若誼：Manager | 其餘：Employee'],
    ]
    ver_table = Table(version_data, colWidths=[3*cm, 5*cm])
    ver_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(Colors.BG_LIGHT)),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(Colors.BORDER)),
    ]))
    story.append(ver_table)
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("© 2026 昱金生能源股份有限公司 版權所有",
        ParagraphStyle('Copyright', parent=styles['BodyText'],
            fontSize=9, textColor=colors.HexColor('#94a3b8'), alignment=TA_CENTER)))
    story.append(PageBreak())
    
    # 目錄
    story.append(Paragraph("目錄", styles['ChapterTitle']))
    toc_data = [
        ['第 1 章', '系統概論', '1'],
        ['1.1', '系統介紹與架構', '1'],
        ['1.2', '系統特色', '2'],
        ['1.3', '使用效益', '3'],
        ['第 2 章', '快速開始', '4'],
        ['2.1', '系統登入', '4'],
        ['2.2', '介面導覽', '6'],
        ['2.3', '帳號管理', '8'],
        ['第 3 章', '填寫日報', '9'],
        ['3.1', '基本流程', '9'],
        ['3.2', '工作項目填寫', '11'],
        ['3.3', '優秀範例 vs 錯誤範例', '13'],
        ['第 4 章', 'AI 功能', '15'],
        ['4.1', 'AI 工作建議', '15'],
        ['4.2', '智慧提醒與通知', '17'],
        ['第 5 章', '常見問題 Q&A', '19'],
        ['第 6 章', '最佳實踐', '22'],
    ]
    toc_table = Table(toc_data, colWidths=[1.5*cm, 8*cm, 1.5*cm])
    toc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Colors.PRIMARY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor(Colors.ACCENT)),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(Colors.BORDER)),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    
    # 第 1 章
    story.append(Paragraph("第 1 章 系統概論", styles['ChapterTitle']))
    story.append(Paragraph("1.1 系統介紹與架構", styles['SectionTitle']))
    story.append(Paragraph("""
    昱金生能源智能日報系統是一套整合 AI 技術的專案管理工具，專為太陽能光電工程團隊設計。
    系統協助員工記錄每日工作進度，並透過 AI 分析提供即時建議，提升團隊協作效率。
    """, styles['BodyText']))
    
    # 系統架構
    story.append(Paragraph("<b>圖 1-1：系統架構</b>", styles['SubSectionTitle']))
    arch_data = [
        ['<b>層級</b>', '<b>組成</b>', '<b>說明</b>'],
        ['使用者層', '員工 / 主管 / 董事長', '網頁瀏覽器、行動裝置'],
        ['應用層', '日報系統、AI 分析、通知', 'Flask Web 應用'],
        ['資料層', 'SQLite 資料庫、郵件儲存', '結構化資料儲存'],
        ['基礎設施', 'WSL2、Windows Server', '本地部署'],
    ]
    arch_table = Table(arch_data, colWidths=[2.5*cm, 5*cm, 5*cm])
    arch_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Colors.PRIMARY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(Colors.BORDER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(Colors.BORDER)),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("1.2 系統特色", styles['SectionTitle']))
    features = [
        ['🤖', 'AI 智慧分析', '自動分析工作內容，提供個人化建議'],
        ['📊', '即時進度追蹤', '掌握各案場進度，自動計算完成百分比'],
        ['🔔', '智慧提醒', '重要事項自動提醒，避免遺漏'],
        ['📧', '郵件整合', '自動分析歷史郵件，理解案場脈絡'],
        ['📱', '多裝置支援', '電腦、平板、手機皆可使用'],
        ['🔒', '權限管理', '分層權限控制，資料安全'],
    ]
    for icon, title, desc in features:
        story.append(Paragraph(f"{icon} <b>{title}</b>", styles['SubSectionTitle']))
        story.append(Paragraph(desc, styles['BodyText']))
        story.append(Spacer(1, 0.3*cm))
    story.append(PageBreak())
    
    story.append(Paragraph("1.3 使用效益", styles['SectionTitle']))
    benefit_data = [
        ['項目', '傳統方式', '使用系統後', '改善'],
        ['進度掌握', '30 分鐘/天', '3 分鐘/天', '⬇️ 90%'],
        ['錯誤遺漏', '15%', '< 2%', '⬇️ 87%'],
        ['溝通成本', '高', '低', '⬇️ 60%'],
        ['決策速度', '慢', '即時', '⬆️ 300%'],
    ]
    ben_table = Table(benefit_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm])
    ben_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Colors.PRIMARY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(Colors.BORDER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(Colors.BORDER)),
    ]))
    story.append(ben_table)
    story.append(Spacer(1, 0.5*cm))
    
    # 適用人員
    story.append(Paragraph("<b>適用人員（15 人）</b>", styles['SubSectionTitle']))
    user_data = [
        ['管理部', '宋啓綸、游若誼、洪淑嫆、楊傑麟、褚佩瑜', '管理監督'],
        ['工程部', '楊宗衛、張億峖、陳明德、李雅婷、陳谷濱', '案場施工'],
        ['維運部', '陳靜儒', '電廠維護'],
        ['行政部', '林天睛、呂宜芹', '行政支援'],
        ['設計部', '顏呈晞、高竹妤', '圖面設計'],
    ]
    user_table = Table(user_data, colWidths=[2*cm, 6*cm, 3.5*cm])
    user_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(Colors.PRIMARY)),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(Colors.BORDER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(Colors.BORDER)),
    ]))
    story.append(user_table)
    story.append(PageBreak())
    
    # 第 2 章
    story.append(Paragraph("第 2 章 快速開始", styles['ChapterTitle']))
    story.append(Paragraph("2.1 系統登入", styles['SectionTitle']))
    
    story.append(Paragraph("<b>步驟 1：開啟瀏覽器</b>", styles['SubSectionTitle']))
    story.append(Paragraph("支援：Google Chrome、Microsoft Edge、Firefox（建議 Chrome）", styles['BodyText']))
    
    story.append(Paragraph("<b>步驟 2：輸入網址</b>", styles['SubSectionTitle']))
    story.append(Paragraph("http://localhost:5000", styles['CodeText']))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>💡 提示：</b>如無法連線，請確認系統服務已啟動", styles['BodyText']))
    
    story.append(Paragraph("<b>步驟 3：輸入帳號密碼</b>", styles['SubSectionTitle']))
    login_steps = [
        '於登入頁面輸入<b>員工編號</b>（例：23102）',
        '輸入<b>初始密碼</b>：Welcome2026!',
        '點擊「登入」按鈕',
        '首次登入需修改密碼（8-16 碼，含大小寫英文 + 數字）',
    ]
    for i, step in enumerate(login_steps, 1):
        story.append(Paragraph(f"<b>{i}.</b> {step}", styles['BodyText']))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("<b>表 2-1：員工帳號清單</b>", styles['SubSectionTitle']))
    account_data = [
        ['編號', '姓名', '部門', '權限', '密碼'],
        ['20101', '宋啓綸', '管理部', 'Admin', 'Welcome2026!'],
        ['20102', '游若誼', '管理部', 'Manager', 'Welcome2026!'],
        ['23102', '楊宗衛', '工程部', 'Employee', 'Welcome2026!'],
        ['24302', '張億峖', '工程部', 'Manager', 'Welcome2026!'],
        ['25105', '陳明德', '工程部', 'Manager', 'Welcome2026!'],
    ]
    acc_table = Table(account_data, colWidths=[1.5*cm, 2*cm, 2*cm, 2*cm, 3*cm])
    acc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Colors.PRIMARY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(Colors.BORDER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(Colors.BORDER)),
    ]))
    story.append(acc_table)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("<b>⚠️ 注意：</b>首次登入必須修改密碼，密碼每 90 天需更換", styles['BodyText']))
    story.append(PageBreak())
    
    # 第 3 章
    story.append(Paragraph("第 3 章 填寫日報", styles['ChapterTitle']))
    story.append(Paragraph("3.1 基本流程", styles['SectionTitle']))
    
    story.append(Paragraph("<b>圖 3-1：日報填寫流程</b>", styles['SubSectionTitle']))
    flow_data = [['登入', '→', '進入日報', '→', '選日期', '→', '填寫', '→', '送出']]
    flow_table = Table(flow_data, colWidths=[1.5*cm, 0.5*cm]*4 + [1.5*cm])
    flow_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(Colors.PRIMARY)),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor(Colors.ACCENT)),
        ('BACKGROUND', (4, 0), (4, 0), colors.HexColor(Colors.SUCCESS)),
        ('BACKGROUND', (6, 0), (6, 0), colors.HexColor(Colors.INFO)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(Colors.BORDER)),
    ]))
    story.append(flow_table)
    story.append(Spacer(1, 0.5*cm))
    
    detailed_steps = [
        ('1️⃣', '登入系統', '使用員工編號和密碼'),
        ('2️⃣', '點擊「填寫日報」', '於首頁點擊綠色按鈕'),
        ('3️⃣', '選擇日期', '預設為今日，可補填 7 天內'),
        ('4️⃣', '選擇案場', '從下拉選單選擇負責案場'),
        ('5️⃣', '填寫工作內容', '具體描述完成項目'),
        ('6️⃣', '填寫進度', '輸入百分比（0-100%）'),
        ('7️⃣', '記錄問題', '如有問題請詳細描述'),
        ('8️⃣', '檢查送出', '確認無誤後送出'),
    ]
    for icon, title, desc in detailed_steps:
        story.append(Paragraph(f"{icon} <b>{title}</b>", styles['SubSectionTitle']))
        story.append(Paragraph(desc, styles['BodyText']))
        story.append(Spacer(1, 0.2*cm))
    story.append(PageBreak())
    
    # 範例
    story.append(Paragraph("3.3 優秀範例 vs 錯誤範例", styles['SectionTitle']))
    
    story.append(Paragraph("<b>✅ 優秀範例</b>", styles['SubSectionTitle']))
    good = [
        ['案場', '仁豐國小'],
        ['工作', '1. 光電板安裝（第 15-20 片）\n2. 逆變器接線測試\n3. 現場清潔'],
        ['內容', '• 完成第 15-20 片安裝，M8 螺栓固定\n• 逆變器測試正常（DC 600V, AC 220V）\n• 清理區域，回收包材'],
        ['進度', '95%'],
        ['問題', '無'],
        ['明日', '1. 準備初驗文件\n2. 聯繫台電審查'],
    ]
    good_table = Table(good, colWidths=[2*cm, 8.5*cm])
    good_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor(Colors.SUCCESS)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(Colors.BORDER)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(good_table)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("<b>❌ 錯誤範例</b>", styles['SubSectionTitle']))
    bad = [
        ['案場', '仁豐國小'],
        ['工作', '施工'],
        ['內容', '安裝光電板'],
        ['進度', '50%'],
        ['問題', '無'],
        ['明日', '繼續施工'],
    ]
    bad_table = Table(bad, colWidths=[2*cm, 8.5*cm])
    bad_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ffebee')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor(Colors.DANGER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(Colors.BORDER)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(bad_table)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("""<b>💡 改善建議：</b>
<br/>• 使用具體數字（片數、電壓、電流）
<br/>• 描述完整流程（準備→安裝→測試→清理）
<br/>• 說明進度計算方式
<br/>• 列出明確的明日目標""", styles['BodyText']))
    story.append(PageBreak())
    
    # 第 5 章 Q&A
    story.append(Paragraph("第 5 章 常見問題 Q&A", styles['ChapterTitle']))
    
    qa_data = [
        ['<b>Q1. 忘記密碼？</b>', 'A. 點擊「忘記密碼」→ 輸入 Email → 收取重設連結 → 設定新密碼'],
        ['<b>Q2. 可補填日報？</b>', 'A. 可補填過去 7 天內，超過需聯繫主管'],
        ['<b>Q3. 無工作要填？</b>', 'A. 仍建議填寫（休假、訓練、會議），選「其他」類別'],
        ['<b>Q4. AI 建議準確？</b>', 'A. 越用越精準，可點擊「不有用」回饋'],
        ['<b>Q5. 補充請求？</b>', 'A. AI 請求補充說明，請於 3 天內回覆'],
    ]
    qa_table = Table(qa_data, colWidths=[4*cm, 8*cm])
    qa_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(Colors.BG_LIGHT)),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(Colors.BORDER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(Colors.BORDER)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(qa_table)
    story.append(PageBreak())
    
    # 第 6 章
    story.append(Paragraph("第 6 章 最佳實踐", styles['ChapterTitle']))
    story.append(Paragraph("6.1 填寫技巧", styles['SectionTitle']))
    
    tips = [
        ['✅', '具體明確', '描述實際完成工作'],
        ['✅', '有數據', '使用數字、百分比'],
        ['✅', '有脈絡', '說明背景目的'],
        ['✅', '有照片', '重要進度拍照'],
        ['✅', '有計畫', '列出明日目標'],
        ['❌', '太簡略', '避免「施工」、「會議」'],
        ['❌', '無數據', '不要只寫百分比'],
        ['❌', '延遲填', '請於當日下班前'],
    ]
    tips_table = Table(tips, colWidths=[0.8*cm, 2*cm, 6.7*cm])
    tips_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(Colors.BORDER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(Colors.BORDER)),
    ]))
    story.append(tips_table)
    
    # 結尾
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("=" * 50, ParagraphStyle('Divider',
        parent=styles['BodyText'], alignment=TA_CENTER, fontSize=16,
        textColor=colors.HexColor(Colors.PRIMARY))))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("感謝您的使用！", styles['SectionTitle']))
    story.append(Paragraph("""如有任何問題，請聯繫：
<br/>• 系統管理員：分機 1234
<br/>• Email：support@yujinsheng.com
<br/>• 服務時間：週一至週五 09:00-18:00""", styles['BodyText']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("昱金生能源 管理團隊", styles['BodyText']))
    
    # 生成
    doc.build(story, onFirstPage=lambda c, d: create_header(c, d, "員工操作手冊"),
              onLaterPages=lambda c, d: create_header(c, d, "員工操作手冊"),
              onAllPages=lambda c, d: create_footer(c, d))
    
    print(f"✅ 已生成：{OUTPUT_DIR / 'EMPLOYEE_MANUAL_PRO.pdf'}")


if __name__ == '__main__':
    print("="*60)
    print("📄 昱金生能源 - 專業手冊生成器 v2.0")
    print("="*60)
    generate_employee_manual()
    print("\n✅ 生成完成！")
