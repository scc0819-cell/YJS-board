#!/usr/bin/env python3
"""
昱金生能源 - PDF 生成器 (簡化版)
生成三份文件：員工手冊、董事長指南、模擬情境報告
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime

# 註冊中文字體
FONT_PATH = '/mnt/c/Windows/Fonts/msjh.ttc'
pdfmetrics.registerFont(TTFont('MicrosoftJhengHei', FONT_PATH))
print(f"✅ 字體已註冊：{FONT_PATH}")

# 檔案路徑
WORKSPACE = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server')
OUTPUT_DIR = WORKSPACE / 'docs'
OUTPUT_DIR.mkdir(exist_ok=True)

def get_styles():
    """定義文件樣式"""
    styles = getSampleStyleSheet()
    
    # 自訂樣式（避免衝突）
    custom_styles = {
        'Title': ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='MicrosoftJhengHei',
            fontSize=24,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            leading=32
        ),
        'Subtitle': ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontName='MicrosoftJhengHei',
            fontSize=16,
            textColor=colors.HexColor('#16213e'),
            spaceAfter=20,
            leading=24
        ),
        'SectionTitle': ParagraphStyle(
            'CustomSection',
            parent=styles['Heading3'],
            fontName='MicrosoftJhengHei',
            fontSize=14,
            textColor=colors.HexColor('#0f3460'),
            spaceAfter=15,
            spaceBefore=20,
            leading=20
        ),
        'NormalTC': ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName='MicrosoftJhengHei',
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            alignment=TA_JUSTIFY,
            leading=18
        ),
    }
    
    return custom_styles


def create_header(canvas, doc, title):
    """頁首"""
    canvas.saveState()
    canvas.setFillColor(colors.HexColor('#1a1a2e'))
    canvas.rect(0, A4[1] - 60, A4[0], 60, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont('MicrosoftJhengHei', 16)
    canvas.drawCentredString(A4[0]/2, A4[1] - 40, title)
    canvas.setFont('MicrosoftJhengHei', 10)
    canvas.drawCentredString(A4[0]/2, A4[1] - 25, '昱金生能源股份有限公司')
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.setFont('MicrosoftJhengHei', 9)
    canvas.drawCentredString(A4[0]/2, 30, f'第 {canvas.getPageNumber()} 頁')
    canvas.restoreState()


def generate_employee_manual():
    """生成員工操作手冊"""
    print("\n📘 生成：員工操作手冊...")
    
    doc = SimpleDocTemplate(str(OUTPUT_DIR / 'EMPLOYEE_MANUAL.pdf'), pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = get_styles()
    story = []
    
    # 封面
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("員工操作手冊", styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("昱金生能源 - 智能日報系統", styles['Subtitle']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"版本：1.0 | 更新日期：{datetime.now().strftime('%Y-%m-%d')}", styles['NormalTC']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("適用對象：全體員工", styles['NormalTC']))
    story.append(PageBreak())
    
    # 系統介紹
    story.append(Paragraph("1. 系統介紹", styles['SectionTitle']))
    story.append(Paragraph("這是公司的<b>智能日報系統</b>，幫助您：", styles['NormalTC']))
    
    features = [['📝', '快速記錄每日工作'], ['🤖', '獲得 AI 工作建議'], 
                ['📊', '掌握案場進度'], ['💡', '提升工作效率']]
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
    story.append(PageBreak())
    
    # 填寫日報步驟
    story.append(Paragraph("2. 填寫日報步驟", styles['SectionTitle']))
    
    steps = [['步驟', '動作', '說明'],
             ['1️⃣', '進入日報頁面', '登入後點擊「填寫日報」按鈕'],
             ['2️⃣', '選擇日期', '預設為今日，可補填過去 7 天'],
             ['3️⃣', '填寫工作項目', '包含案場名稱、工作內容、進度'],
             ['4️⃣', '送出日報', '檢查無誤後點擊「送出」']]
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
    good_example = [['案場', '仁豐國小'],
                    ['工作內容', '• 完成最後 5 片光電板安裝\n• 測試電壓正常\n• 清理現場'],
                    ['進度', '95%'],
                    ['問題', '無'],
                    ['明日計畫', '準備初驗文件']]
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
    bad_example = [['案場', '仁豐國小'],
                   ['工作內容', '施工（太籠統）'],
                   ['進度', '50%'],
                   ['問題', '無']]
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
    
    # 常見問題
    story.append(Paragraph("3. 常見問題", styles['SectionTitle']))
    faq_data = [
        ['<b>Q1: 忘記密碼怎麼辦？</b>', 'A: 點擊「忘記密碼」，系統會發送重設連結到您的 Email。'],
        ['<b>Q2: 可以補填過去的日報嗎？</b>', 'A: 可以，最多可補填過去 7 天的日報。'],
        ['<b>Q3: AI 建議準確嗎？</b>', 'A: AI 會根據您的日報和歷史資料學習，越用越精準。'],
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
    
    # 結尾
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("感謝您的使用！", styles['Subtitle']))
    story.append(Paragraph("昱金生能源 管理團隊", styles['NormalTC']))
    
    doc.build(story, onFirstPage=lambda c, d: create_header(c, d, "員工操作手冊"),
              onLaterPages=lambda c, d: create_header(c, d, "員工操作手冊"))
    print(f"✅ 已生成：{OUTPUT_DIR / 'EMPLOYEE_MANUAL.pdf'}")


def generate_chairman_guide():
    """生成董事長快速指南"""
    print("\n👔 生成：董事長快速指南...")
    
    doc = SimpleDocTemplate(str(OUTPUT_DIR / 'CHAIRMAN_GUIDE.pdf'), pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
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
    
    # 您的專屬功能
    story.append(Paragraph("1. 您的專屬功能", styles['SectionTitle']))
    story.append(Paragraph("<b>1️⃣ 董事長專屬報告</b>", styles['NormalTC']))
    story.append(Paragraph("<b>時間</b>：每日 08:00 自動生成", styles['NormalTC']))
    story.append(Paragraph("<b>內容</b>：案場進度、風險預警、補充請求、AI 建議", styles['NormalTC']))
    story.append(Paragraph("<b>您的操作</b>：3 分鐘掌握全局", styles['NormalTC']))
    story.append(Spacer(1, 0.3*inch))
    
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
    <b>📬 補充請求（待判斷）:</b><br/>
    • 楊宗衛：「施工空間問題是否解決？」<br/>
    &nbsp;&nbsp;您的回覆：[需要 / 不需要]<br/><br/>
    <b>🤖 AI 建議:</b><br/>
    • 整體進度良好<br/>
    • 注意下週天氣變化
    """
    story.append(Paragraph(report_example, styles['NormalTC']))
    story.append(PageBreak())
    
    # 每日流程
    story.append(Paragraph("2. 每日流程", styles['SectionTitle']))
    
    daily_flow = [['時間', '動作', '說明'],
                  ['08:00', '登入系統', '查看董事長報告（3 分鐘）'],
                  ['08:03', '回覆補充請求', '判斷需要/不需要（1 分鐘）'],
                  ['08:04', '掌握全局', '開始一天工作']]
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
    
    # 預期效益
    story.append(Paragraph("3. 預期效益", styles['SectionTitle']))
    
    time_saving = [['項目', '目前', '系統啟用後', '節省'],
                   ['掌握案場進度', '30 分鐘/天', '3 分鐘/天', '90%↓'],
                   ['員工管理', '2 小時/天', '自動', '100%↓'],
                   ['會議時間', '4 小時/週', '1 小時/週', '75%↓'],
                   ['<b>總節省</b>', '<b>-</b>', '<b>-</b>', '<b>15 小時/週</b>']]
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
    
    # 結尾
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("祝您使用愉快！", styles['Subtitle']))
    story.append(Paragraph("昱金生能源 AI 助理 Jenny", styles['NormalTC']))
    
    doc.build(story, onFirstPage=lambda c, d: create_header(c, d, "董事長快速指南"),
              onLaterPages=lambda c, d: create_header(c, d, "董事長快速指南"))
    print(f"✅ 已生成：{OUTPUT_DIR / 'CHAIRMAN_GUIDE.pdf'}")


def generate_simulation_report():
    """生成模擬情境報告"""
    print("\n📊 生成：模擬情境報告...")
    
    doc = SimpleDocTemplate(str(OUTPUT_DIR / 'SIMULATION_REPORT.pdf'), pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
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
    
    # 情境 1
    story.append(Paragraph("情境 1：員工提交日報", styles['SectionTitle']))
    story.append(Paragraph("<b>時間</b>：2026-03-03 08:30", styles['NormalTC']))
    story.append(Paragraph("<b>員工</b>：楊宗衛（23102）", styles['NormalTC']))
    story.append(Paragraph("<b>案場</b>：仁豐國小", styles['NormalTC']))
    story.append(Spacer(1, 0.3*inch))
    
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
    story.append(PageBreak())
    
    # 情境 2
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
    <b>需要協助嗎？隨時告訴我！</b>
    """
    story.append(Paragraph(ai_feedback, styles['NormalTC']))
    story.append(PageBreak())
    
    # 預期效益
    story.append(Paragraph("預期效益", styles['SectionTitle']))
    
    time_saving = [['項目', '目前', '系統啟用後', '節省'],
                   ['掌握案場進度', '30 分鐘/天', '3 分鐘/天', '90%↓'],
                   ['員工管理', '2 小時/天', '自動', '100%↓'],
                   ['會議時間', '4 小時/週', '1 小時/週', '75%↓'],
                   ['<b>總節省</b>', '<b>-</b>', '<b>-</b>', '<b>15 小時/週</b>']]
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
    
    # 結尾
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("報告結束", styles['Subtitle']))
    story.append(Paragraph("昱金生能源 AI 助理", styles['NormalTC']))
    
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
    print(f"\n💡 這些檔案位於 C 槽，可直接在 Windows 中開啟查看")
