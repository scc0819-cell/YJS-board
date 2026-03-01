#!/usr/bin/env python3
"""
昱金生能源 - 專業 PDF 手冊生成器 v2.0
生成正式、專業、圖文並茂的操作手冊
風格：現代化、專業、視覺化（參考 Notion、Linear）
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, Flowable, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import pagesizes
from pathlib import Path
from datetime import datetime
import os

# ========== 字體設定 ==========
FONT_PATH = '/mnt/c/Windows/Fonts/msjh.ttc'  # 微軟正黑體
FONT_PATH_ALT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'  # 備用字體

def register_fonts():
    """註冊中文字體"""
    font_paths = [FONT_PATH, FONT_PATH_ALT]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('MicrosoftJhengHei', path))
                pdfmetrics.registerFont(TTFont('MSJH', path))  # 別名
                print(f"✅ 字體已註冊：{path}")
                return True
            except Exception as e:
                print(f"⚠️  字體註冊失敗 {path}: {e}")
    
    print("❌ 所有字體註冊失敗，使用預設字體")
    return False

register_fonts()

# ========== 檔案路徑 ==========
WORKSPACE = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server')
OUTPUT_DIR = WORKSPACE / 'docs'
IMAGES_DIR = WORKSPACE / 'static' / 'images'
OUTPUT_DIR.mkdir(exist_ok=True)

# ========== 專業配色方案 ==========
class BrandColors:
    """昱金生能源品牌色系"""
    PRIMARY_DARK = '#0f172a'      # 深藍黑（主色）
    PRIMARY = '#1e3a5f'           # 深藍（主要品牌色）
    PRIMARY_LIGHT = '#334155'     # 中藍（次要色）
    ACCENT = '#0ea5e9'            # 亮藍（強調色）
    SUCCESS = '#10b981'           # 綠色（成功）
    WARNING = '#f59e0b'           # 橘色（警告）
    DANGER = '#ef4444'            # 紅色（錯誤）
    INFO = '#6366f1'              # 紫色（資訊）
    BG_LIGHT = '#f8fafc'          # 淺灰背景
    BG_WHITE = '#ffffff'          # 白色背景
    TEXT_DARK = '#1e293b'         # 深灰文字
    TEXT_MEDIUM = '#475569'       # 中灰文字
    TEXT_LIGHT = '#94a3b8'        # 淺灰文字
    BORDER = '#e2e8f0'            # 邊框色

# ========== 專業樣式定義 ==========
def create_professional_styles():
    """建立專業文件樣式"""
    styles = getSampleStyleSheet()
    
    # 封面標題
    styles.add(ParagraphStyle(
        name='CoverTitle',
        parent=styles['Title'],
        textColor=colors.HexColor(BrandColors.PRIMARY_DARK),
        spaceAfter=40,
        alignment=TA_CENTER,
        leading=42
    ))
    
    # 封面副標題
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        parent=styles['Heading1'],
        textColor=colors.HexColor(BrandColors.PRIMARY),
        spaceAfter=30,
        alignment=TA_CENTER,
        leading=28,
    
    # 章節標題（大）
    styles.add(ParagraphStyle(
        name='ChapterTitle',
        parent=styles['Heading1'],
        textColor=colors.HexColor(BrandColors.PRIMARY_DARK),
        spaceAfter=25,
        spaceBefore=30,
        leading=30,
        borderWidth=0,
        borderColor=colors.HexColor(BrandColors.ACCENT),
        borderPadding=10,
    
    # 次級標題
    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading2'],
        textColor=colors.HexColor(BrandColors.PRIMARY),
        spaceAfter=18,
        spaceBefore=25,
        leading=24,
    
    # 小節標題
    styles.add(ParagraphStyle(
        name='SubSectionTitle',
        parent=styles['Heading3'],
        textColor=colors.HexColor(BrandColors.PRIMARY_LIGHT),
        spaceAfter=12,
        spaceBefore=18,
        leading=20,
    
    # 內文（寬鬆排版）
    styles.add(ParagraphStyle(
        name='BodyText',
        parent=styles['Normal'],
        textColor=colors.HexColor(BrandColors.TEXT_DARK),
        alignment=TA_JUSTIFY,
        leading=20,  # 行距 20pt（寬鬆）
        firstLineIndent=0,
        spaceAfter=10,
    
    # 重點提示框
    styles.add(ParagraphStyle(
        name='HighlightBox',
        parent=styles['Normal'],
        textColor=colors.HexColor(BrandColors.PRIMARY_DARK),
        alignment=TA_LEFT,
        leading=18,
        leftIndent=20,
        rightIndent=20,
        spaceAfter=15,
    
    # 步驟說明
    styles.add(ParagraphStyle(
        name='StepText',
        parent=styles['Normal'],
        textColor=colors.HexColor(BrandColors.TEXT_DARK),
        alignment=TA_LEFT,
        leading=18,
        leftIndent=30,
        spaceAfter=8,
    
    # 程式碼/路徑
    styles.add(ParagraphStyle(
        name='CodeText',
        parent=styles['Normal'],
        textColor=colors.HexColor('#dc2626'),
        alignment=TA_LEFT,
        leading=16,
        backColor=colors.HexColor('#f1f5f9'),
        borderWidth=1,
        borderColor=colors.HexColor(BrandColors.BORDER),
        borderPadding=8,
    
    # 表格標題
    styles.add(ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        textColor=colors.white,
        alignment=TA_CENTER,
        leading=16,
    
    # 表格內容
    styles.add(ParagraphStyle(
        name='TableCell',
        parent=styles['Normal'],
        textColor=colors.HexColor(BrandColors.TEXT_DARK),
        alignment=TA_LEFT,
        leading=16,
    
    return styles


# ========== 專業頁首頁尾 ==========
def create_professional_header(canvas, doc, title, chapter=''):
    """專業頁首"""
    canvas.saveState()
    
    # 頂部色帶
    canvas.setFillColor(colors.HexColor(BrandColors.PRIMARY))
    canvas.rect(0, A4[1] - 15, A4[0], 15, fill=1)
    
    # 公司名稱
    canvas.setFillColor(colors.white)
    canvas.setFont('MSJH', 9)
    canvas.drawString(2*cm, A4[1] - 12, '昱金生能源股份有限公司')
    
    # 文件標題
    canvas.setFillColor(colors.HexColor(BrandColors.TEXT_MEDIUM))
    canvas.setFont('MSJH', 9)
    canvas.drawRightString(A4[0] - 2*cm, A4[1] - 12, title)
    
    # 章節（如果有）
    if chapter:
        canvas.setFillColor(colors.HexColor(BrandColors.ACCENT))
        canvas.setFont('MSJH', 8)
        canvas.drawString(2*cm, A4[1] - 25, chapter)
    
    # 分隔線
    canvas.setStrokeColor(colors.HexColor(BrandColors.BORDER))
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, A4[1] - 30, A4[0] - 2*cm, A4[1] - 30)
    
    canvas.restoreState()


def create_professional_footer(canvas, doc):
    """專業頁尾"""
    canvas.saveState()
    
    # 分隔線
    canvas.setStrokeColor(colors.HexColor(BrandColors.BORDER))
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 2.5*cm, A4[0] - 2*cm, 2.5*cm)
    
    # 頁碼
    canvas.setFillColor(colors.HexColor(BrandColors.TEXT_LIGHT))
    canvas.setFont('MSJH', 9)
    page_num = canvas.getPageNumber()
    canvas.drawRightString(A4[0] - 2*cm, 2*cm, f'第 {page_num} 頁')
    
    # 版權資訊
    canvas.drawString(2*cm, 2*cm, f'© 2026 昱金生能源 | 機密文件')
    
    # 日期
    canvas.drawCentredString(A4[0]/2, 2*cm, datetime.now().strftime('%Y-%m-%d'))
    
    canvas.restoreState()


# ========== 視覺元素 ==========
def draw_status_indicator(canvas, x, y, status, size=10):
    """繪製狀態指示器"""
    colors_map = {
        'success': BrandColors.SUCCESS,
        'warning': BrandColors.WARNING,
        'danger': BrandColors.DANGER,
        'info': BrandColors.INFO
    }
    
    color = colors_map.get(status, BrandColors.TEXT_LIGHT)
    canvas.setFillColor(colors.HexColor(color))
    canvas.circle(x, y, size/2, fill=1)


def draw_section_header(canvas, doc, title, icon='📋'):
    """繪製章節標題（帶圖示）"""
    canvas.saveState()
    
    # 背景色塊
    canvas.setFillColor(colors.HexColor(BrandColors.BG_LIGHT))
    canvas.rect(2*cm, A4[1] - 4*cm, A4[0] - 4*cm, 3*cm, fill=1)
    
    # 標題
    canvas.setFillColor(colors.HexColor(BrandColors.PRIMARY_DARK))
    canvas.setFont('MSJH', 18)
    canvas.drawString(2.5*cm, A4[1] - 2.5*cm, f'{icon} {title}')
    
    canvas.restoreState()


# ========== 員工操作手冊 ==========
def generate_professional_employee_manual():
    """生成專業版員工操作手冊"""
    print("\n📘 生成：專業版員工操作手冊...")
    
    doc = SimpleDocTemplate(
        str(OUTPUT_DIR / 'EMPLOYEE_MANUAL_PRO.pdf'),
        pagesize=A4,
        rightMargin=2.5*cm,
        leftMargin=2.5*cm,
        topMargin=3*cm,
        bottomMargin=3*cm,
        title="昱金生能源 - 員工操作手冊"
    )
    
    styles = create_professional_styles()
    story = []
    
    # ==================== 封面 ====================
    story.append(Spacer(1, 3*cm))
    
    # 公司 Logo（文字版）
    story.append(Paragraph("昱金生能源", styles['CoverTitle']))
    story.append(Paragraph("YUJINSHENG ENERGY", ParagraphStyle(
        'EnglishSubtitle',
        parent=styles['CoverSubtitle'],
        fontSize=14,
        textColor=colors.HexColor(BrandColors.PRIMARY_LIGHT)
    )))
    
    story.append(Spacer(1, 1.5*cm))
    
    # 文件標題
    story.append(Paragraph("員工操作手冊", styles['CoverSubtitle']))
    story.append(Paragraph("智能日報系統", ParagraphStyle(
        'DocSubtitle',
        parent=styles['CoverSubtitle'],
        fontSize=14,
        textColor=colors.HexColor(BrandColors.TEXT_MEDIUM)
    )))
    
    story.append(Spacer(1, 2*cm))
    
    # 版本資訊
    version_info = [
        ['文件版本', 'v2.0'],
        ['更新日期', datetime.now().strftime('%Y 年 %m 月 %d 日')],
        ['適用對象', '全體員工'],
        ['保密等級', '內部機密'],
    ]
    version_table = Table(version_info, colWidths=[3*cm, 5*cm])
    version_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(BrandColors.BG_LIGHT)),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(BrandColors.BORDER)),
    ]))
    story.append(version_table)
    
    story.append(Spacer(1, 3*cm))
    
    # 版權聲明
    story.append(Paragraph("© 2026 昱金生能源股份有限公司 版權所有", ParagraphStyle(
        'Copyright',
        parent=styles['BodyText'],
        fontSize=9,
        textColor=colors.HexColor(BrandColors.TEXT_LIGHT),
        alignment=TA_CENTER
    )))
    
    story.append(PageBreak())
    
    # ==================== 目錄 ====================
    story.append(Paragraph("目錄", styles['ChapterTitle']))
    
    toc_data = [
        ['第 1 章', '系統概論', '1'],
        ['1.1', '系統介紹', '1'],
        ['1.2', '系統特色', '2'],
        ['1.3', '使用效益', '3'],
        ['', '', ''],
        ['第 2 章', '快速開始', '4'],
        ['2.1', '系統登入', '4'],
        ['2.2', '介面導覽', '6'],
        ['2.3', '帳號管理', '8'],
        ['', '', ''],
        ['第 3 章', '填寫日報', '9'],
        ['3.1', '基本流程', '9'],
        ['3.2', '工作項目填寫', '11'],
        ['3.3', '進度回報', '13'],
        ['3.4', '問題記錄', '14'],
        ['', '', ''],
        ['第 4 章', 'AI 功能', '15'],
        ['4.1', 'AI 工作建議', '15'],
        ['4.2', '智慧提醒', '17'],
        ['4.3', '補充請求', '18'],
        ['', '', ''],
        ['第 5 章', '常見問題', '19'],
        ['5.1', '登入問題', '19'],
        ['5.2', '填寫問題', '20'],
        ['5.3', '系統異常', '21'],
        ['', '', ''],
        ['第 6 章', '最佳實踐', '22'],
        ['6.1', '填寫技巧', '22'],
        ['6.2', '溝通建議', '23'],
        ['6.3', '效率提升', '24'],
    ]
    
    toc_table = Table(toc_data, colWidths=[1.5*cm, 8*cm, 1.5*cm])
    toc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(BrandColors.PRIMARY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor(BrandColors.ACCENT)),
        ('LINEBELOW', (0, 4), (-1, 4), 1, colors.HexColor(BrandColors.BORDER)),
        ('LINEBELOW', (0, 10), (-1, 10), 1, colors.HexColor(BrandColors.BORDER)),
        ('LINEBELOW', (0, 16), (-1, 16), 1, colors.HexColor(BrandColors.BORDER)),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(BrandColors.BORDER)),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    
    # ==================== 第 1 章：系統概論 ====================
    story.append(Paragraph("第 1 章 系統概論", styles['ChapterTitle']))
    
    story.append(Paragraph("1.1 系統介紹", styles['SectionTitle']))
    story.append(Paragraph("""
    昱金生能源智能日報系統是一套整合 AI 技術的專案管理工具，專為太陽能光電工程團隊設計。
    系統協助員工記錄每日工作進度，並透過 AI 分析提供即時建議，提升團隊協作效率。
    """, styles['BodyText']))
    
    # 系統架構圖（文字描述）
    story.append(Paragraph("<b>圖 1-1：系統架構圖</b>", styles['SubSectionTitle']))
    
    arch_data = [
        ['<b>使用者層</b>', '員工 / 主管 / 董事長', '網頁瀏覽器、行動裝置'],
        ['<b>應用層</b>', '日報系統、AI 分析、通知服務', 'Flask Web 應用'],
        ['<b>資料層</b>', 'SQLite 資料庫、郵件儲存', '結構化資料儲存'],
        ['<b>基礎設施</b>', 'WSL2、Windows Server', '本地部署'],
    ]
    arch_table = Table(arch_data, colWidths=[2.5*cm, 5*cm, 5*cm])
    arch_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(BrandColors.PRIMARY)),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, 0), (2, 0), colors.HexColor(BrandColors.BG_LIGHT)),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(BrandColors.BORDER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BrandColors.BORDER)),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("1.2 系統特色", styles['SectionTitle']))
    
    features = [
        ['🤖', '<b>AI 智慧分析</b>', '自動分析工作內容，提供個人化建議'],
        ['📊', '<b>即時進度追蹤</b>', '掌握各案場進度，自動計算完成百分比'],
        ['🔔', '<b>智慧提醒</b>', '重要事項自動提醒，避免遺漏'],
        ['📧', '<b>郵件整合</b>', '自動分析歷史郵件，理解案場脈絡'],
        ['📱', '<b>多裝置支援</b>', '電腦、平板、手機皆可使用'],
        ['🔒', '<b>權限管理</b>', '分層權限控制，資料安全'],
    ]
    
    for i, (icon, title, desc) in enumerate(features):
        story.append(Paragraph(f"{icon} {title}", styles['SubSectionTitle']))
        story.append(Paragraph(desc, styles['BodyText']))
        if i < len(features) - 1:
            story.append(Spacer(1, 0.3*cm))
    
    story.append(PageBreak())
    
    story.append(Paragraph("1.3 使用效益", styles['SectionTitle']))
    
    # 效益對比表
    benefit_data = [
        ['項目', '傳統方式', '使用系統後', '改善幅度'],
        ['進度掌握時間', '30 分鐘/天', '3 分鐘/天', '⬇️ 90%'],
        ['錯誤遺漏率', '15%', '< 2%', '⬇️ 87%'],
        ['溝通成本', '高', '低', '⬇️ 60%'],
        ['決策速度', '慢', '即時', '⬆️ 300%'],
    ]
    benefit_table = Table(benefit_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm])
    benefit_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(BrandColors.PRIMARY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(BrandColors.BORDER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BrandColors.BORDER)),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(BrandColors.BG_LIGHT)]),
    ]))
    story.append(benefit_table)
    story.append(Spacer(1, 0.5*cm))
    
    # 適用人員
    story.append(Paragraph("<b>適用人員</b>", styles['SubSectionTitle']))
    user_roles = [
        ['工程部', '楊宗衛、張億峖、陳明德、李雅婷、陳谷濱', '案場施工、進度回報'],
        ['維運部', '陳靜儒', '電廠維護、異常處理'],
        ['設計部', '顏呈晞、高竹妤', '圖面設計、規劃'],
        ['行政部', '林天睛、呂宜芹', '行政支援、文件處理'],
        ['管理部', '宋啓綸、游若誼、洪淑嫆、楊傑麟、褚佩瑜', '管理監督、決策'],
    ]
    user_table = Table(user_roles, colWidths=[2*cm, 6*cm, 4.5*cm])
    user_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(BrandColors.PRIMARY_LIGHT)),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(BrandColors.BORDER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BrandColors.BORDER)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(user_table)
    story.append(PageBreak())
    
    # ==================== 第 2 章：快速開始 ====================
    story.append(Paragraph("第 2 章 快速開始", styles['ChapterTitle']))
    
    story.append(Paragraph("2.1 系統登入", styles['SectionTitle']))
    
    # 步驟 1
    story.append(Paragraph("<b>步驟 1：開啟瀏覽器</b>", styles['SubSectionTitle']))
    story.append(Paragraph("""
    支援的瀏覽器：Google Chrome、Microsoft Edge、Firefox（建議使用 Chrome）
    """, styles['BodyText']))
    
    # 步驟 2
    story.append(Paragraph("<b>步驟 2：輸入系統網址</b>", styles['SubSectionTitle']))
    story.append(Paragraph("""
    於瀏覽器網址列輸入以下網址：
    """, styles['BodyText']))
    
    story.append(Paragraph("http://localhost:5000", styles['CodeText']))
    story.append(Spacer(1, 0.3*cm))
    
    story.append(Paragraph("""
    <b>💡 提示：</b>如無法連線，請確認系統服務已啟動，或聯繫管理員。
    """, styles['HighlightBox']))
    
    # 步驟 3
    story.append(Paragraph("<b>步驟 3：輸入帳號密碼</b>", styles['SubSectionTitle']))
    
    login_steps = [
        ['1', '在登入頁面輸入您的<b>員工編號</b>（例：23102）'],
        ['2', '輸入<b>初始密碼</b>：Welcome2026!'],
        ['3', '點擊「登入」按鈕'],
        ['4', '首次登入需修改密碼（8-16 碼，含大小寫英文 + 數字）'],
    ]
    
    for step_num, step_desc in login_steps:
        story.append(Paragraph(f"<b>{step_num}.</b> {step_desc}", styles['StepText']))
    
    story.append(Spacer(1, 0.5*cm))
    
    # 帳號清單
    story.append(Paragraph("<b>表 2-1：員工帳號清單（部分）</b>", styles['SubSectionTitle']))
    
    account_data = [
        ['編號', '姓名', '部門', '預設密碼', '權限'],
        ['20101', '宋啓綸', '管理部', 'Welcome2026!', 'Admin'],
        ['20102', '游若誼', '管理部', 'Welcome2026!', 'Manager'],
        ['23102', '楊宗衛', '工程部', 'Welcome2026!', 'Employee'],
        ['24302', '張億峖', '工程部', 'Welcome2026!', 'Manager'],
        ['25105', '陳明德', '工程部', 'Welcome2026!', 'Manager'],
    ]
    
    account_table = Table(account_data, colWidths=[1.5*cm, 2*cm, 2*cm, 3*cm, 2*cm])
    account_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(BrandColors.PRIMARY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(BrandColors.BORDER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BrandColors.BORDER)),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(BrandColors.BG_LIGHT)]),
    ]))
    story.append(account_table)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("""
    <b>⚠️ 注意事項：</b>
    <br/>• 首次登入必須修改密碼
    <br/>• 密碼每 90 天需更換一次
    <br/>• 勿將密碼告知他人
    <br/>• 離職時帳號將自動停用
    """, styles['HighlightBox']))
    
    story.append(PageBreak())
    
    # ==================== 第 3 章：填寫日報 ====================
    story.append(Paragraph("第 3 章 填寫日報", styles['ChapterTitle']))
    
    story.append(Paragraph("3.1 基本流程", styles['SectionTitle']))
    
    # 流程圖
    story.append(Paragraph("<b>圖 3-1：日報填寫流程圖</b>", styles['SubSectionTitle']))
    
    flow_data = [
        ['登入系統', '→', '進入日報頁面', '→', '選擇日期', '→', '填寫內容', '→', '檢查送出'],
    ]
    flow_table = Table(flow_data, colWidths=[2*cm, 0.5*cm, 2*cm, 0.5*cm, 2*cm, 0.5*cm, 2*cm, 0.5*cm, 2*cm])
    flow_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(BrandColors.PRIMARY)),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor(BrandColors.PRIMARY_LIGHT)),
        ('BACKGROUND', (4, 0), (4, 0), colors.HexColor(BrandColors.ACCENT)),
        ('BACKGROUND', (6, 0), (6, 0), colors.HexColor(BrandColors.SUCCESS)),
        ('BACKGROUND', (8, 0), (8, 0), colors.HexColor(BrandColors.INFO)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(BrandColors.BORDER)),
    ]))
    story.append(flow_table)
    story.append(Spacer(1, 0.5*cm))
    
    # 詳細步驟
    story.append(Paragraph("<b>詳細步驟說明</b>", styles['SubSectionTitle']))
    
    detailed_steps = [
        ['1️⃣', '登入系統', '使用員工編號和密碼登入'],
        ['2️⃣', '點擊「填寫日報」', '於首頁點擊綠色按鈕'],
        ['3️⃣', '選擇日期', '預設為今日，可補填過去 7 天'],
        ['4️⃣', '選擇案場', '從下拉選單選擇您負責的案場'],
        ['5️⃣', '填寫工作內容', '具體描述完成的工作項目'],
        ['6️⃣', '填寫進度', '輸入完成百分比（0-100%）'],
        ['7️⃣', '記錄問題', '如有問題或需協助，請詳細描述'],
        ['8️⃣', '檢查並送出', '確認無誤後點擊「送出」按鈕'],
    ]
    
    for icon, title, desc in detailed_steps:
        story.append(Paragraph(f"{icon} <b>{title}</b>", styles['SubSectionTitle']))
        story.append(Paragraph(desc, styles['BodyText']))
        story.append(Spacer(1, 0.2*cm))
    
    story.append(PageBreak())
    
    # ==================== 範例展示 ====================
    story.append(Paragraph("3.2 填寫範例", styles['SectionTitle']))
    
    # 好的範例
    story.append(Paragraph("<b>✅ 優秀範例</b>", styles['SubSectionTitle']))
    
    good_example = [
        ['<b>案場名稱</b>', '仁豐國小'],
        ['<b>工作項目</b>', '1. 光電板安裝（第 15-20 片）\n2. 逆變器接線測試\n3. 現場清潔整理'],
        ['<b>工作內容</b>', '• 完成第 15-20 片光電板安裝，使用 M8 螺栓固定\n• 進行逆變器 DC/AC 接線，量測電壓正常（DC 600V, AC 220V）\n• 清理安裝區域，回收包裝材料'],
        ['<b>完成進度</b>', '95%'],
        ['<b>遭遇問題</b>', '無'],
        ['<b>明日計畫</b>', '1. 準備初驗文件\n2. 聯繫台電安排併聯審查'],
        ['<b>需協助事項</b>', '無'],
    ]
    
    good_table = Table(good_example, colWidths=[2.5*cm, 8*cm])
    good_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor(BrandColors.SUCCESS)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BrandColors.BORDER)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(good_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # 不好的範例
    story.append(Paragraph("<b>❌ 錯誤範例</b>", styles['SubSectionTitle']))
    
    bad_example = [
        ['<b>案場名稱</b>', '仁豐國小'],
        ['<b>工作項目</b>', '施工'],
        ['<b>工作內容</b>', '安裝光電板'],
        ['<b>完成進度</b>', '50%'],
        ['<b>遭遇問題</b>', '無'],
        ['<b>明日計畫</b>', '繼續施工'],
        ['<b>需協助事項</b>', '無'],
    ]
    
    bad_table = Table(bad_example, colWidths=[2.5*cm, 8*cm])
    bad_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ffebee')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor(BrandColors.DANGER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BrandColors.BORDER)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(bad_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # 改善建議
    story.append(Paragraph("<b>💡 改善建議</b>", styles['SubSectionTitle']))
    story.append(Paragraph("""
    <b>錯誤範例的問題：</b>
    <br/>• 工作項目太籠統（「施工」應具體說明）
    <br/>• 工作內容缺乏細節（應包含數量、規格、測試結果）
    <br/>• 進度 50% 缺乏依據（應說明計算基準）
    <br/>• 明日計畫不明確（應列出具體工作項目）
    <br/><br/>
    <b>建議改善：</b>
    <br/>• 使用具體數字（片數、電壓、電流）
    <br/>• 描述完整流程（準備→安裝→測試→清理）
    <br/>• 說明進度計算方式（已安裝/總數）
    <br/>• 列出明確的明日目標
    """, styles['HighlightBox']))
    
    story.append(PageBreak())
    
    # ==================== 常見問題 ====================
    story.append(Paragraph("第 5 章 常見問題", styles['ChapterTitle']))
    
    # Q1
    story.append(Paragraph("<b>Q1. 忘記密碼怎麼辦？</b>", styles['SubSectionTitle']))
    story.append(Paragraph("""
    <b>解答：</b>
    <br/>1. 於登入頁面點擊「忘記密碼」連結
    <br/>2. 輸入您的員工編號和註冊 Email
    <br/>3. 系統將發送重設連結到您的信箱
    <br/>4. 點擊連結並設定新密碼
    <br/><br/>
    <b>💡 提示：</b>如未收到郵件，請檢查垃圾郵件匣，或聯繫管理員（分機 1234）
    """, styles['BodyText']))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Q2
    story.append(Paragraph("<b>Q2. 可以補填過去的日報嗎？</b>", styles['SubSectionTitle']))
    story.append(Paragraph("""
    <b>解答：</b>
    <br/>• 可以補填<b>過去 7 天內</b>的日報
    <br/>• 超過 7 天需聯繫主管協助
    <br/>• 補填時請於備註欄說明原因
    """, styles['BodyText']))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Q3
    story.append(Paragraph("<b>Q3. 如果今天沒有工作要回報呢？</b>", styles['SubSectionTitle']))
    story.append(Paragraph("""
    <b>解答：</b>
    <br/>• 仍建議填寫，可記錄：休假、教育訓練、會議、文件整理等
    <br/>• 選擇「其他」類別，說明當日活動
    <br/>• 連續 3 日未填寫，系統將自動發送提醒
    """, styles['BodyText']))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Q4
    story.append(Paragraph("<b>Q4. AI 建議準確嗎？</b>", styles['SubSectionTitle']))
    story.append(Paragraph("""
    <b>解答：</b>
    <br/>• AI 會根據您的日報和歷史資料持續學習
    <br/>• 使用時間越長，建議越精準
    <br/>• 如發現錯誤建議，可點擊「不有用」回饋
    <br/>• 系統會根據回饋調整建議內容
    """, styles['BodyText']))
    
    story.append(Spacer(1, 0.5*cm))
    
    # Q5
    story.append(Paragraph("<b>Q5. 收到「補充請求」是什麼？</b>", styles['SubSectionTitle']))
    story.append(Paragraph("""
    <b>解答：</b>
    <br/>• AI 分析您的工作記錄時，如有不清楚的地方，會發送補充請求
    <br/>• 請於<b>3 天內</b>回覆說明
    <br/>• 補充內容會幫助 AI 更了解案場狀況
    <br/>• 逾期未回覆，系統將發送提醒通知
    """, styles['BodyText']))
    
    story.append(PageBreak())
    
    # ==================== 最佳實踐 ====================
    story.append(Paragraph("第 6 章 最佳實踐", styles['ChapterTitle']))
    
    story.append(Paragraph("6.1 填寫技巧", styles['SectionTitle']))
    
    tips_data = [
        ['✅', '具體明確', '描述實際完成的工作，避免籠統字眼'],
        ['✅', '有數據', '使用數字、百分比、規格等具體資訊'],
        ['✅', '有脈絡', '說明工作背景和目的'],
        ['✅', '有照片', '重要進度建議拍照存證'],
        ['✅', '有明日計畫', '讓主管了解您的規劃'],
        ['❌', '太簡略', '避免只寫「施工」、「會議」'],
        ['❌', '無數據', '不要只寫進度百分比'],
        ['❌', '延遲填寫', '請於當日下班前完成'],
    ]
    
    tips_table = Table(tips_data, colWidths=[0.8*cm, 2*cm, 7.7*cm])
    tips_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MSJH'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(BrandColors.BORDER)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BrandColors.BORDER)),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#e8f5e9'), colors.HexColor('#ffebee'), colors.white, colors.HexColor('#e8f5e9'), colors.HexColor('#ffebee'), colors.white, colors.HexColor('#e8f5e9'), colors.HexColor('#ffebee')]),
    ]))
    story.append(tips_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    # 結尾
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("=" * 50, ParagraphStyle(
        'Divider',
        parent=styles['BodyText'],
        alignment=TA_CENTER,
        fontSize=16,
        textColor=colors.HexColor(BrandColors.PRIMARY)
    )))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("感謝您的使用！", styles['SectionTitle']))
    story.append(Paragraph("""
    如有任何問題，請聯繫：
    <br/>• 系統管理員：分機 1234
    <br/>• Email：support@yujinsheng.com
    <br/>• 服務時間：週一至週五 09:00-18:00
    """, styles['BodyText']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("昱金生能源 管理團隊", styles['BodyText']))
    
    # 生成 PDF
    doc.build(story, 
              onFirstPage=lambda c, d: create_professional_header(c, d, "員工操作手冊", "第 1 章"),
              onLaterPages=lambda c, d: create_professional_header(c, d, "員工操作手冊"))
    
    print(f"✅ 已生成：{OUTPUT_DIR / 'EMPLOYEE_MANUAL_PRO.pdf'}")
    return OUTPUT_DIR / 'EMPLOYEE_MANUAL_PRO.pdf'


if __name__ == '__main__':
    print("="*60)
    print("📄 昱金生能源 - 專業 PDF 手冊生成器 v2.0")
    print("="*60)
    
    generate_professional_employee_manual()
    
    print("\n" + "="*60)
    print("✅ 專業版手冊生成完成！")
    print("="*60)
