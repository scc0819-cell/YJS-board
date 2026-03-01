#!/usr/bin/env python3
"""
昱金生能源 - PDF 生成器
生成三份文件：員工手冊、董事長指南、模擬情境報告
風格：現代、簡潔、專業、視覺化
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime

# 註冊中文字體
FONT_PATH = '/mnt/c/Windows/Fonts/msjh.ttc'  # 微軟正黑體
try:
    pdfmetrics.registerFont(TTFont('MicrosoftJhengHei', FONT_PATH))
    print(f"✅ 字體已註冊：{FONT_PATH}")
except Exception as e:
    print(f"⚠️  字體註冊失敗：{e}")
    print("   使用預設字體（可能無法顯示中文）")

# 檔案路徑
WORKSPACE = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server')
OUTPUT_DIR = WORKSPACE / 'docs'
OUTPUT_DIR.mkdir(exist_ok=True)

# 樣式定義
def get_styles():
    """定義文件樣式"""
    styles = getSampleStyleSheet()
    
    # 標題風格
    try:
        styles.add(ParagraphStyle(
            name='Title',
            parent=styles['Heading1'],
            fontName='MicrosoftJhengHei',
            fontSize=24,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            leading=32
        ))
    except KeyError:
        pass  # 樣式已存在
    
    # 副標題
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Heading2'],
        fontName='MicrosoftJhengHei',
        fontSize=16,
        textColor=colors.HexColor('#16213e'),
        spaceAfter=20,
        leading=24
    ))
    
    # 章節標題
    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading3'],
        fontName='MicrosoftJhengHei',
        fontSize=14,
        textColor=colors.HexColor('#0f3460'),
        spaceAfter=15,
        spaceBefore=20,
        leading=20
    ))
    
    # 內文
    styles.add(ParagraphStyle(
        name='NormalTC',
        parent=styles['Normal'],
        fontName='MicrosoftJhengHei',
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        alignment=TA_JUSTIFY,
        leading=18
    ))
    
    # 重點提示
    styles.add(ParagraphStyle(
        name='Highlight',
        parent=styles['Normal'],
        fontName='MicrosoftJhengHei',
        fontSize=11,
        textColor=colors.HexColor('#e94560'),
        alignment=TA_LEFT,
        leading=18
    ))
    
    return styles


def create_header(canvas, doc, title):
    """頁首"""
    canvas.saveState()
    # 背景色塊
    canvas.setFillColor(colors.HexColor('#1a1a2e'))
    canvas.rect(0, A4[1] - 60, A4[0], 60, fill=1)
    
    # 標題
    canvas.setFillColor(colors.white)
    canvas.setFont('MicrosoftJhengHei', 16)
    canvas.drawCentredString(A4[0]/2, A4[1] - 40, title)
    
    # 公司名稱
    canvas.setFont('MicrosoftJhengHei', 10)
    canvas.drawCentredString(A4[0]/2, A4[1] - 25, '昱金生能源股份有限公司')
    
    # 頁腳
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.setFont('MicrosoftJhengHei', 9)
    canvas.drawCentredString(A4[0]/2, 30, f'第 {canvas.getPageNumber()} 頁')
    canvas.restoreState()


def generate_employee_manual():
    """生成員工操作手冊"""
    print("\n📘 生成：員工操作手冊...")
    
    doc = SimpleDocTemplate(
        str(OUTPUT_DIR / 'EMPLOYEE_MANUAL.pdf'),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = get_styles()
    story = []
    
    # 封面
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("員工操作手冊", styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("昱金生能源 - 智能日報系統", styles['Subtitle']))
    story.append(Spacer(1, 0.5*inch))
    
    # 版本資訊
    story.append(Paragraph(f"版本：1.0 | 更新日期：{datetime.now().strftime('%Y-%m-%d')}", styles['NormalTC']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("適用對象：全體員工", styles['NormalTC']))
    story.append(PageBreak())
    
    # 目錄
    story.append(Paragraph("目錄", styles['SectionTitle']))
    toc_data = [
        ['1. 系統介紹', '第 2 頁'],
        ['2. 快速開始', '第 2 頁'],
        ['3. 填寫日報步驟', '第 3 頁'],
        ['4. 查看 AI 建議', '第 4 頁'],
        ['5. 常見問題', '第 5 頁'],
        ['6. 填寫技巧', '第 6 頁'],
    ]
    toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
    toc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    
    # 第 1 章：系統介紹
    story.append(Paragraph("1. 系統介紹", styles['SectionTitle']))
    story.append(Paragraph("""
    這是公司的<b>智能日報系統</b>，幫助您：
    """, styles['NormalTC']))
    
    features = [
        ['📝', '快速記錄每日工作'],
        ['🤖', '獲得 AI 工作建議'],
        ['📊', '掌握案場進度'],
        ['💡', '提升工作效率'],
    ]
    features_table = Table(features, colWidths=[0.5*inch, 3.5*inch])
    features_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 0.5*inch))
    
    # 系統流程圖（用文字描述）
    story.append(Paragraph("系統運作流程：", styles['NormalTC']))
    flow_data = [
        ['員工登入', '→', '填寫日報', '→', 'AI 分析', '→', '生成建議'],
    ]
    flow_table = Table(flow_data, colWidths=[1.2*inch, 0.3*inch, 1.2*inch, 0.3*inch, 1.2*inch, 0.3*inch, 1.2*inch])
    flow_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#1a1a2e')),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#0f3460')),
        ('BACKGROUND', (4, 0), (4, 0), colors.HexColor('#e94560')),
        ('BACKGROUND', (6, 0), (6, 0), colors.HexColor('#16213e')),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('TEXTCOLOR', (2, 0), (2, 0), colors.white),
        ('TEXTCOLOR', (4, 0), (4, 0), colors.white),
        ('TEXTCOLOR', (6, 0), (6, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
    ]))
    story.append(flow_table)
    story.append(Spacer(1, 0.5*inch))
    story.append(PageBreak())
    
    # 第 2 章：快速開始
    story.append(Paragraph("2. 快速開始", styles['SectionTitle']))
    
    story.append(Paragraph("<b>步驟 1：登入系統</b>", styles['NormalTC']))
    story.append(Paragraph("""
    網址：[系統網址待提供]<br/>
    帳號：您的員工編號<br/>
    密碼：初始密碼將個別通知
    """, styles['NormalTC']))
    
    login_example = [
        ['範例：', ''],
        ['帳號', '23102'],
        ['密碼', 'Welcome2026!（首次登入需修改）'],
    ]
    login_table = Table(login_example, colWidths=[1*inch, 3*inch])
    login_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    story.append(login_table)
    story.append(Spacer(1, 0.5*inch))
    story.append(PageBreak())
    
    # 第 3 章：填寫日報步驟
    story.append(Paragraph("3. 填寫日報步驟", styles['SectionTitle']))
    
    steps = [
        ['步驟', '動作', '說明'],
        ['1️⃣', '進入日報頁面', '登入後點擊「填寫日報」按鈕'],
        ['2️⃣', '選擇日期', '預設為今日，可補填過去 7 天'],
        ['3️⃣', '填寫工作項目', '包含案場名稱、工作內容、進度'],
        ['4️⃣', '送出日報', '檢查無誤後點擊「送出」'],
    ]
    steps_table = Table(steps, colWidths=[0.8*inch, 1.5*inch, 3.7*inch])
    steps_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(steps_table)
    story.append(Spacer(1, 0.5*inch))
    
    # 好的日報範例
    story.append(Paragraph("<b>✅ 好的日報範例</b>", styles['NormalTC']))
    good_example = [
        ['案場', '仁豐國小'],
        ['工作內容', '• 完成最後 5 片光電板安裝<br/>• 測試電壓正常<br/>• 清理現場'],
        ['進度', '95%'],
        ['問題', '無'],
        ['明日計畫', '準備初驗文件'],
    ]
    good_table = Table(good_example, colWidths=[1.2*inch, 4.8*inch])
    good_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#4caf50')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(good_table)
    story.append(Spacer(1, 0.3*inch))
    
    # 不好的日報範例
    story.append(Paragraph("<b>❌ 不好的日報範例</b>", styles['NormalTC']))
    bad_example = [
        ['案場', '仁豐國小'],
        ['工作內容', '施工（太籠統）'],
        ['進度', '50%'],
        ['問題', '無'],
    ]
    bad_table = Table(bad_example, colWidths=[1.2*inch, 4.8*inch])
    bad_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ffebee')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#f44336')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(bad_table)
    story.append(PageBreak())
    
    # 第 4 章：查看 AI 建議
    story.append(Paragraph("4. 查看 AI 建議", styles['SectionTitle']))
    story.append(Paragraph("""
    <b>時間</b>：提交日報後 30 分鐘<br/>
    <b>位置</b>：系統首頁 → 「AI 建議」區塊
    """, styles['NormalTC']))
    
    ai_example = """
    <b>楊宗衛你好，</b><br/><br/>
    <b>✨ 今日工作亮點</b><br/>
    • 仁豐國小進度達到 95%，即將完工！<br/>
    • 主動聯繫台電確認進度，積極度佳<br/><br/>
    <b>💡 明日建議</b><br/>
    • 優先準備仁豐國小初驗文件<br/>
    • 馬偕護專併聯申請如未回覆，可發 Email 催促<br/><br/>
    <b>需要協助嗎？隨時告訴我！</b>
    """
    story.append(Paragraph(ai_example, styles['NormalTC']))
    story.append(Spacer(1, 0.5*inch))
    story.append(PageBreak())
    
    # 第 5 章：常見問題
    story.append(Paragraph("5. 常見問題", styles['SectionTitle']))
    
    faq_data = [
        ['<b>Q1: 忘記密碼怎麼辦？</b>', 'A: 點擊「忘記密碼」，系統會發送重設連結到您的 Email。'],
        ['<b>Q2: 可以補填過去的日報嗎？</b>', 'A: 可以，最多可補填過去 7 天的日報。'],
        ['<b>Q3: 如果今天沒有工作要回報呢？</b>', 'A: 還是建議填寫，可以記錄休假、教育訓練、會議等。'],
        ['<b>Q4: AI 建議準確嗎？</b>', 'A: AI 會根據您的日報和歷史資料學習，越用越精準。'],
        ['<b>Q5: 收到「補充請求」是什麼？</b>', 'A: AI 分析您的工作記錄時，如有不清楚的地方，會請求補充說明。'],
    ]
    faq_table = Table(faq_data, colWidths=[2.5*inch, 3.5*inch])
    faq_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(faq_table)
    story.append(PageBreak())
    
    # 第 6 章：填寫技巧
    story.append(Paragraph("6. 填寫技巧", styles['SectionTitle']))
    
    tips = [
        ['✅', '具體明確', '描述實際完成的工作內容'],
        ['✅', '有數據', '使用百分比、數量等具體數字'],
        ['✅', '有明日計畫', '讓主管了解您的規劃'],
        ['❌', '太籠統', '避免只寫「施工」、「會議」'],
        ['❌', '無數據', '不要只寫進度百分比'],
    ]
    tips_table = Table(tips, colWidths=[0.5*inch, 1.2*inch, 4.3*inch])
    tips_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    story.append(tips_table)
    story.append(Spacer(1, 0.5*inch))
    
    # 結尾
    story.append(Paragraph("感謝您的使用！", styles['Subtitle']))
    story.append(Paragraph("昱金生能源 管理團隊", styles['NormalTC']))
    
    # 生成 PDF
    doc.build(story, onFirstPage=lambda c, d: create_header(c, d, "員工操作手冊"),
              onLaterPages=lambda c, d: create_header(c, d, "員工操作手冊"))
    
    print(f"✅ 已生成：{OUTPUT_DIR / 'EMPLOYEE_MANUAL.pdf'}")


def generate_chairman_guide():
    """生成董事長快速指南"""
    print("\n👔 生成：董事長快速指南...")
    
    doc = SimpleDocTemplate(
        str(OUTPUT_DIR / 'CHAIRMAN_GUIDE.pdf'),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = get_styles()
    story = []
    
    # 封面
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("董事長快速指南", styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("昱金生能源 - AI 管理系統", styles['Subtitle']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"版本：1.0 | 更新日期：{datetime.now().strftime('%Y-%m-%d')}", styles['NormalTC']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("適用對象：宋啓綸 董事長", styles['NormalTC']))
    story.append(PageBreak())
    
    # 目錄
    story.append(Paragraph("目錄", styles['SectionTitle']))
    toc_data = [
        ['1. 您的專屬功能', '第 2 頁'],
        ['2. 儀表板預覽', '第 3 頁'],
        ['3. 每日流程', '第 4 頁'],
        ['4. 預期效益', '第 5 頁'],
        ['5. 上線時程', '第 6 頁'],
    ]
    toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
    toc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    
    # 第 1 章：您的專屬功能
    story.append(Paragraph("1. 您的專屬功能", styles['SectionTitle']))
    
    story.append(Paragraph("<b>1️⃣ 董事長專屬報告</b>", styles['NormalTC']))
    story.append(Paragraph("""
    <b>時間</b>：每日 08:00 自動生成<br/>
    <b>內容</b>：案場進度、風險預警、補充請求、AI 建議<br/>
    <b>您的操作</b>：3 分鐘掌握全局
    """, styles['NormalTC']))
    
    report_example = """
    <b>📊 董事長專屬報告 - 2026-03-04</b><br/><br/>
    <b>📈 今日摘要:</b><br/>
    • 日報提交率：12/15 (80%) ✅<br/>
    • 進行中案場：8 個 ✅<br/>
    • 新增高風險：0 個 ✅<br/><br/>
    <b>🏭 各案場進度:</b><br/>
    • ✅ 仁豐國小：95%（即將完工）<br/>
    • ✅ 馬偕護專：等待台電審查<br/>
    • ⚠️  大城國小：85%（廠商延遲）<br/><br/>
    <b>🎯 需要您決策:</b><br/>
    • ✅ 無高風險項目<br/><br/>
    <b>📬 補充請求（待判斷）:</b><br/>
    • 楊宗衛：「施工空間問題是否解決？」<br/>
    &nbsp;&nbsp;您的回覆：[需要 / 不需要]<br/><br/>
    <b>🤖 AI 建議:</b><br/>
    • 整體進度良好<br/>
    • 注意下週天氣變化
    """
    story.append(Paragraph(report_example, styles['NormalTC']))
    story.append(Spacer(1, 0.5*inch))
    story.append(PageBreak())
    
    # 第 2 章：儀表板預覽
    story.append(Paragraph("2. 儀表板預覽", styles['SectionTitle']))
    
    dashboard = """
    <b>┌─────────────────────────────────────────┐</b><br/>
    <b>│  昱金生能源 - 董事長儀表板                │</b><br/>
    <b>├─────────────────────────────────────────┤</b><br/>
    <b>│                                         │</b><br/>
    <b>│  📊 今日摘要                            │</b><br/>
    <b>│  • 日報提交率：80%                      │</b><br/>
    <b>│  • 進行中案場：8 個                     │</b><br/>
    <b>│  • 高風險：0 個                         │</b><br/>
    <b>│                                         │</b><br/>
    <b>│  🏭 案場進度（地圖）                     │</b><br/>
    <b>│  ✅ 仁豐國小 95%                        │</b><br/>
    <b>│  ✅ 馬偕護專 等待審查                    │</b><br/>
    <b>│  ⚠️  大城國小 85%                        │</b><br/>
    <b>│                                         │</b><br/>
    <b>│  📬 待您判斷（2 筆）                     │</b><br/>
    <b>│  1. 楊宗衛：施工空間問題                │</b><br/>
    <b>│  2. 陳明德：驗收人員安排                │</b><br/>
    <b>│                                         │</b><br/>
    <b>│  ⏰ 逾期提醒（0 筆）                      │</b><br/>
    <b>│                                         │</b><br/>
    <b>└─────────────────────────────────────────┘</b>
    """
    story.append(Paragraph(dashboard, styles['NormalTC']))
    story.append(Spacer(1, 0.5*inch))
    story.append(PageBreak())
    
    # 第 3 章：每日流程
    story.append(Paragraph("3. 每日流程", styles['SectionTitle']))
    
    daily_flow = [
        ['時間', '動作', '說明'],
        ['08:00', '登入系統', '查看董事長報告（3 分鐘）'],
        ['08:03', '回覆補充請求', '判斷需要/不需要（1 分鐘）'],
        ['08:04', '掌握全局', '開始一天工作'],
        ['15:00', '快速查看', '可選，查看即時風險（1 分鐘）'],
    ]
    flow_table = Table(daily_flow, colWidths=[1*inch, 1.5*inch, 3.5*inch])
    flow_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    story.append(flow_table)
    story.append(Spacer(1, 0.5*inch))
    
    weekly_flow = [
        ['每週一 08:30', '查看週報', '掌握團隊整體表現（5 分鐘）'],
        ['每月 1 號 08:30', '查看月報', '個人績效排名（10 分鐘）'],
    ]
    weekly_table = Table(weekly_flow, colWidths=[1.5*inch, 2*inch, 2.5*inch])
    weekly_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    story.append(weekly_table)
    story.append(PageBreak())
    
    # 第 4 章：預期效益
    story.append(Paragraph("4. 預期效益", styles['SectionTitle']))
    
    time_saving = [
        ['項目', '目前', '系統啟用後', '節省'],
        ['掌握案場進度', '30 分鐘/天', '3 分鐘/天', '90%↓'],
        ['員工管理', '2 小時/天', '自動', '100%↓'],
        ['會議時間', '4 小時/週', '1 小時/週', '75%↓'],
        ['<b>總節省</b>', '<b>-</b>', '<b>-</b>', '<b>15 小時/週</b>'],
    ]
    time_table = Table(time_saving, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    time_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (-1, -1), (-1, -1), colors.HexColor('#e94560')),
        ('TEXTCOLOR', (-1, -1), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    story.append(time_table)
    story.append(Spacer(1, 0.5*inch))
    
    quality_improve = [
        ['項目', '改善前', '改善後'],
        ['即時性', '延遲 1-2 天', '即時'],
        ['準確性', '人為錯誤', '數據驅動'],
        ['完整性', '遺漏風險', '全面掃描'],
        ['決策依據', '主觀判斷', '客觀數據'],
    ]
    quality_table = Table(quality_improve, colWidths=[1.5*inch, 2.25*inch, 2.25*inch])
    quality_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    story.append(quality_table)
    story.append(PageBreak())
    
    # 第 5 章：上線時程
    story.append(Paragraph("5. 上線時程", styles['SectionTitle']))
    
    timeline = [
        ['本週', '靜默準備期', '系統就緒、資料模擬'],
        ['下周', '宣布 + 試運行', '員工開始使用'],
        ['第 2-3 週', '正式啟用', 'AI 建議品質提升'],
        ['第 4 週', '優化', '系統穩定運行'],
    ]
    timeline_table = Table(timeline, colWidths=[1.2*inch, 2*inch, 2.8*inch])
    timeline_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    story.append(timeline_table)
    story.append(Spacer(1, 0.5*inch))
    
    # 結尾
    story.append(Paragraph("祝您使用愉快！", styles['Subtitle']))
    story.append(Paragraph("昱金生能源 AI 助理 Jenny", styles['NormalTC']))
    
    # 生成 PDF
    doc.build(story, onFirstPage=lambda c, d: create_header(c, d, "董事長快速指南"),
              onLaterPages=lambda c, d: create_header(c, d, "董事長快速指南"))
    
    print(f"✅ 已生成：{OUTPUT_DIR / 'CHAIRMAN_GUIDE.pdf'}")


def generate_simulation_report():
    """生成模擬情境報告"""
    print("\n📊 生成：模擬情境報告...")
    
    doc = SimpleDocTemplate(
        str(OUTPUT_DIR / 'SIMULATION_REPORT.pdf'),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = get_styles()
    story = []
    
    # 封面
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("模擬情境報告", styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("系統正式上線後運作情境", styles['Subtitle']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['NormalTC']))
    story.append(Paragraph("目的：讓董事長預覽系統正式上線後的實際運作狀況", styles['NormalTC']))
    story.append(PageBreak())
    
    # 情境 1：員工提交日報
    story.append(Paragraph("情境 1：員工提交日報", styles['SectionTitle']))
    story.append(Paragraph("<b>時間</b>：2026-03-03 08:30", styles['NormalTC']))
    story.append(Paragraph("<b>員工</b>：楊宗衛（23102）", styles['NormalTC']))
    story.append(Paragraph("<b>案場</b>：仁豐國小", styles['NormalTC']))
    
    report_content = """
    <b>工作項目：</b><br/>
    1. 仁豐國小 - 光電板安裝<br/>
    &nbsp;&nbsp;• 進度：95%<br/>
    &nbsp;&nbsp;• 內容：完成最後 5 片光電板安裝<br/>
    &nbsp;&nbsp;• 問題：無<br/><br/>
    2. 馬偕護專 - 併聯申請<br/>
    &nbsp;&nbsp;• 進度：等待台電審查<br/>
    &nbsp;&nbsp;• 內容：已電話聯繫台電，預計下週回覆<br/><br/>
    <b>明日計畫：</b><br/>
    • 仁豐國小：準備初驗文件<br/>
    • 馬偕護專：等待台電回覆
    """
    story.append(Paragraph(report_content, styles['NormalTC']))
    story.append(Spacer(1, 0.5*inch))
    story.append(PageBreak())
    
    # 情境 2：AI 即時反饋
    story.append(Paragraph("情境 2：AI 即時反饋", styles['SectionTitle']))
    story.append(Paragraph("<b>時間</b>：2026-03-03 09:00（30 分鐘後）", styles['NormalTC']))
    
    ai_feedback = """
    <b>🤖 AI 工作建議 - 2026-03-03</b><br/><br/>
    <b>楊宗衛你好，</b><br/><br/>
    <b>✨ 今日工作亮點</b><br/>
    • 仁豐國小進度達到 95%，即將完工！<br/>
    • 主動聯繫台電確認進度，積極度佳<br/><br/>
    <b>💡 明日建議</b><br/>
    • 優先準備仁豐國小初驗文件<br/>
    &nbsp;&nbsp;包含：施工照片、測試報告、材料清單<br/>
    • 馬偕護專併聯申請如未回覆，可發 Email 催促<br/><br/>
    <b>⚠️ 注意事項</b><br/>
    • 根據歷史郵件，仁豐國小曾有施工空間問題<br/>
    • 請確認初驗前所有問題已解決<br/><br/>
    <b>📚 學習建議</b><br/>
    • 參考大城國小驗收經驗（2025-12）<br/>
    • 提前準備常見缺失改善報告<br/><br/>
    <b>需要協助嗎？隨時告訴我！</b>
    """
    story.append(Paragraph(ai_feedback, styles['NormalTC']))
    story.append(Spacer(1, 0.5*inch))
    story.append(PageBreak())
    
    # 情境 3：董事長專屬報告
    story.append(Paragraph("情境 3：董事長專屬報告", styles['SectionTitle']))
    story.append(Paragraph("<b>時間</b>：2026-03-04 08:00", styles['NormalTC']))
    
    chairman_report = """
    <b>📊 董事長專屬報告</b><br/><br/>
    <b>報告日期</b>: 2026-03-03<br/>
    <b>生成時間</b>: 08:00<br/><br/>
    <b>📈 今日摘要</b><br/>
    | 指標 | 數值 | 狀態 |<br/>
    |------|------|------|<br/>
    | 日報提交率 | 12/15 (80%) | ✅ |<br/>
    | 進行中案場 | 8 個 | ✅ |<br/>
    | 新增高風險 | 0 個 | ✅ |<br/>
    | 任務更新 | 5 個 | ✅ |<br/><br/>
    <b>🏭 各案場進度</b><br/><br/>
    <b>✅ 仁豐國小</b><br/>
    • 進度：95% → 即將完工<br/>
    • 負責人：楊宗衛<br/>
    • 狀態：準備初驗<br/><br/>
    <b>✅ 馬偕護專</b><br/>
    • 進度：等待台電審查<br/>
    • 負責人：楊宗衛<br/>
    • 狀態：正常<br/><br/>
    <b>⚠️ 大城國小</b><br/>
    • 進度：85%<br/>
    • 負責人：張億峖<br/>
    • 風險：廠商延遲（已處理）<br/><br/>
    <b>🎯 需要您決策</b><br/>
    • ✅ 無高風險項目<br/><br/>
    <b>📬 補充請求（待您判斷）</b><br/>
    共 2 筆待確認：<br/>
    1. 楊宗衛：「仁豐國小施工空間問題是否解決？」<br/>
    &nbsp;&nbsp;您的判斷：[需要 / 不需要]<br/>
    2. 陳明德：「馬偕護專驗收人員安排」<br/>
    &nbsp;&nbsp;您的判斷：[需要 / 不需要]<br/><br/>
    <b>🤖 AI 綜合建議</b><br/>
    • 整體進度良好<br/>
    • 仁豐國小預計本週完工<br/>
    • 注意下週天氣變化（可能有雨）
    """
    story.append(Paragraph(chairman_report, styles['NormalTC']))
    story.append(Spacer(1, 0.5*inch))
    story.append(PageBreak())
    
    # 情境 4：補充請求追蹤
    story.append(Paragraph("情境 4：補充請求追蹤", styles['SectionTitle']))
    story.append(Paragraph("<b>時間</b>：2026-03-04 09:00", styles['NormalTC']))
    
    supplement_request = """
    <b>📬 資訊補充請求</b><br/><br/>
    <b>楊宗衛你好，</b><br/><br/>
    AI 分析您的歷史郵件時，發現以下資訊需要補充：<br/><br/>
    <b>❓ 問題：</b><br/>
    「仁豐國小案場進度回報」中提到的「現場施工空間不足」問題是否已解決？<br/><br/>
    <b>📋 背景：</b><br/>
    • 案場：仁豐國小<br/>
    • 來源郵件：2026-02-20<br/>
    • 期限：3 天內（2026-03-07）<br/><br/>
    請回覆此問題，幫助 AI 更了解案場狀況。<br/><br/>
    <b>楊宗衛回覆：</b><br/>
    已解決！廠商調整了施工範圍，問題已排除。<br/><br/>
    <b>系統更新：</b><br/>
    • ✅ 員工已回覆<br/>
    • ✅ AI 記憶更新<br/>
    • ✅ 董事長判斷：不需要（已標記）
    """
    story.append(Paragraph(supplement_request, styles['NormalTC']))
    story.append(Spacer(1, 0.5*inch))
    story.append(PageBreak())
    
    # 預期效益
    story.append(Paragraph("預期效益", styles['SectionTitle']))
    
    time_saving = [
        ['項目', '目前', '系統啟用後', '節省'],
        ['掌握案場進度', '30 分鐘/天', '3 分鐘/天', '90%↓'],
        ['員工管理', '2 小時/天', '自動', '100%↓'],
        ['會議時間', '4 小時/週', '1 小時/週', '75%↓'],
        ['績效考核', '4 小時/月', '自動', '100%↓'],
        ['<b>總節省</b>', '<b>-</b>', '<b>-</b>', '<b>15 小時/週</b>'],
    ]
    time_table = Table(time_saving, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    time_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftJhengHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (-1, -1), (-1, -1), colors.HexColor('#e94560')),
        ('TEXTCOLOR', (-1, -1), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    story.append(time_table)
    story.append(Spacer(1, 0.5*inch))
    
    # 結尾
    story.append(Paragraph("報告結束", styles['Subtitle']))
    story.append(Paragraph("昱金生能源 AI 助理", styles['NormalTC']))
    
    # 生成 PDF
    doc.build(story, onFirstPage=lambda c, d: create_header(c, d, "模擬情境報告"),
              onLaterPages=lambda c, d: create_header(c, d, "模擬情境報告"))
    
    print(f"✅ 已生成：{OUTPUT_DIR / 'SIMULATION_REPORT.pdf'}")


if __name__ == '__main__':
    print("="*60)
    print("📄 昱金生能源 - PDF 生成器")
    print("="*60)
    
    generate_employee_manual()
    generate_chairman_guide()
    generate_simulation_report()
    
    print("\n" + "="*60)
    print("✅ 所有 PDF 已生成完成！")
    print("="*60)
    print(f"\n📁 存放路徑：{OUTPUT_DIR}")
    print("\n📄 已生成檔案:")
    for pdf in OUTPUT_DIR.glob('*.pdf'):
        print(f"   ✅ {pdf.name}")
    print("\n💡 這些檔案位於 C 槽，可直接在 Windows 中開啟查看")
