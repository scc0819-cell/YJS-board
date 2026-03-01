#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成董事長快速指南 PDF
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

# 註冊中文字體
FONT_PATH = '/mnt/c/Windows/Fonts/msjh.ttc'
pdfmetrics.registerFont(TTFont('MicrosoftJhengHei', FONT_PATH))
pdfmetrics.registerFont(TTFont('MicrosoftJhengHei-Bold', FONT_PATH))

# 顏色定義
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
styles.add(ParagraphStyle(name='NormalTC', parent=styles['Normal'], fontName='MicrosoftJhengHei', fontSize=11, textColor=HexColor('#475569'), alignment=TA_JUSTIFY, leading=19))
styles.add(ParagraphStyle(name='BulletPoint', parent=styles['Normal'], fontName='MicrosoftJhengHei', fontSize=11, textColor=HexColor('#475569'), leftIndent=20, leading=17))
styles.add(ParagraphStyle(name='InfoBox', parent=styles['Normal'], fontName='MicrosoftJhengHei', fontSize=10, textColor=HexColor('#1e293b'), leftIndent=20, rightIndent=20, leading=15))

def create_chairman_guide():
    doc = SimpleDocTemplate("/home/yjsclaw/.openclaw/workspace/daily_report_server/docs/CHAIRMAN_GUIDE.pdf", pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2.5*cm, bottomMargin=2*cm)
    story = []
    
    # 封面
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("👔 董事長快速指南", styles['CoverTitle']))
    story.append(Paragraph("智能日報系統 - 3 分鐘掌握全局", styles['CoverSubtitle']))
    story.append(Spacer(1, 1*cm))
    
    info_data = [['📄 版本', 'v3.0'], ['📅 日期', '2026/03/01'], ['👤 適用', '宋啓綸 董事長']]
    info_table = Table(info_data, colWidths=[4*cm, 6*cm])
    info_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (0, -1), 'MicrosoftJhengHei-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 11), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(info_table)
    story.append(Spacer(1, 2*cm))
    
    story.append(PageBreak())
    
    # 第 1 章
    story.append(Paragraph("第 1 章 您的專屬功能", styles['ChapterTitle']))
    story.append(Paragraph("📊 董事長專屬報告", styles['SectionTitle']))
    
    story.append(Paragraph("⏰ 生成時間：每日 08:00 自動生成", styles['BulletPoint']))
    story.append(Paragraph("📍 查看位置：系統首頁 → 「董事長報告」區塊", styles['BulletPoint']))
    story.append(Paragraph("⏱️ 您的操作：只需 3 分鐘，掌握全局", styles['BulletPoint']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("📈 報告內容預覽：", styles['SectionTitle']))
    report_content = """<b>今日摘要</b><br/>• 日報提交率：12/15 (80%) ✅<br/>• 進行中案場：8 個 ✅<br/>• 新增高風險：0 個 ✅<br/><br/><b>各案場進度</b><br/>✅ 仁豐國小：95%（即將完工）<br/>✅ 馬偕護專：等待台電審查<br/>⚠️ 大城國小：85%（廠商延遲）<br/><br/><b>需要您決策</b><br/>• ✅ 無高風險項目<br/><br/><b>補充請求（待判斷）</b><br/>• 楊宗衛：「施工空間問題是否解決？」<br/>  您的回覆：[需要 / 不需要]<br/><br/><b>AI 建議</b><br/>• 整體進度良好<br/>• 注意下週天氣變化"""
    story.append(Paragraph(report_content, styles['InfoBox']))
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("📈 核心指標儀表板", styles['SectionTitle']))
    metrics_data = [['80%', '8', '0', '3min'], ['日報提交率', '進行中案場', '高風險項目', '每日查看時間']]
    metrics_table = Table(metrics_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    metrics_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), PRIMARY), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'MicrosoftJhengHei-Bold'), ('FONTNAME', (0, 1), (-1, -1), 'MicrosoftJhengHei'), ('FONTSIZE', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 12), ('TOPPADDING', (0, 0), (-1, -1), 12), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
    story.append(metrics_table)
    
    story.append(PageBreak())
    
    # 第 2 章
    story.append(Paragraph("第 2 章 每日流程", styles['ChapterTitle']))
    
    timeline = [
        ("⏰ 08:00", "登入系統", "查看董事長專屬報告（3 分鐘）<br/>快速掃描：提交率、案場進度、風險項目"),
        ("📬 08:03", "回覆補充請求", "判斷員工請求是否需要補充（1 分鐘）<br/>點擊「需要」或「不需要」即可"),
        ("🎯 08:04", "掌握全局", "開始一天的工作<br/>如有高風險項目，系統會自動標紅提醒"),
        ("📱 15:00", "快速查看（可選）", "查看即時風險（1 分鐘）<br/>如有異常，系統會主動通知")
    ]
    
    for time, title, desc in timeline:
        story.append(Paragraph(f"<b>{time} {title}</b>", styles['SectionTitle']))
        story.append(Paragraph(desc, styles['NormalTC']))
        story.append(Spacer(1, 15))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("💡 總時間投資：每日 3-5 分鐘", ParagraphStyle('Highlight', parent=styles['Normal'], fontName='MicrosoftJhengHei-Bold', fontSize=12, textColor=SUCCESS, leftIndent=20, rightIndent=20, leading=18)))
    story.append(Paragraph("獲得效益：即時掌握 15 人團隊、8+ 案場進度、風險提前預警", styles['InfoBox']))
    
    story.append(PageBreak())
    
    # 第 3 章
    story.append(Paragraph("第 3 章 預期效益", styles['ChapterTitle']))
    
    benefit_data = [
        ['項目', '目前', '系統啟用後', '節省幅度'],
        ['掌握案場進度', '30 分鐘/天', '3 分鐘/天', '⬇️ 90%'],
        ['員工管理', '2 小時/天', '自動', '⬇️ 100%'],
        ['會議時間', '4 小時/週', '1 小時/週', '⬇️ 75%'],
        ['績效考核', '4 小時/月', '自動生成', '⬇️ 100%'],
        ['總節省', '-', '-', '15 小時/週 = 每年 780 小時']
    ]
    benefit_table = Table(benefit_data, colWidths=[4*cm, 3.5*cm, 3.5*cm, 4*cm])
    benefit_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), PRIMARY), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'MicrosoftJhengHei-Bold'), ('FONTNAME', (0, 1), (-1, -1), 'MicrosoftJhengHei'), ('FONTSIZE', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 10), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), ('BACKGROUND', (0, 5), (-1, 5), WARNING)]))
    story.append(benefit_table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("📊 管理品質提升：", styles['SectionTitle']))
    quality = ["即時性：延遲 1-2 天 → 即時", "準確性：人為錯誤 → 數據驅動", "完整性：遺漏風險 → 全面掃描", "決策依據：主觀判斷 → 客觀數據"]
    for item in quality:
        story.append(Paragraph(f"• {item}", styles['BulletPoint']))
    
    story.append(PageBreak())
    
    # 第 4 章
    story.append(Paragraph("第 4 章 上線時程", styles['ChapterTitle']))
    
    phases = [
        ("✅ 本週", "靜默準備期", "系統就緒、資料模擬、帳號建立（15 人）<br/>歷史郵件分析、教育訓練材料準備"),
        ("🚀 下周 (3/9-3/14)", "宣布 + 試運行", "3/9（一）09:00 宣布系統上線<br/>3/9（一）14:00 員工教育訓練（30 分鐘）<br/>員工開始提交日報，AI 被動學習"),
        ("📈 第 2-3 週", "正式啟用", "第 2 週：50+ 筆日報，AI 開始建議<br/>第 3 週：100+ 筆日報，建議品質提升"),
        ("🎯 第 4 週", "優化完成", "系統穩定運行，精準建議<br/>全面發揮 AI 效益")
    ]
    
    for time, title, desc in phases:
        story.append(Paragraph(f"<b>{time}</b> {title}", styles['SectionTitle']))
        story.append(Paragraph(desc, styles['NormalTC']))
        story.append(Spacer(1, 15))
    
    # 頁尾
    story.append(PageBreak())
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("祝您使用愉快！", ParagraphStyle('Footer', parent=styles['Heading2'], fontName='MicrosoftJhengHei-Bold', fontSize=15, textColor=PRIMARY, alignment=TA_CENTER)))
    story.append(Spacer(1, 20))
    story.append(Paragraph("昱金生能源 AI 助理 Jenny 為您服務", styles['NormalTC']))
    story.append(Spacer(1, 20))
    
    contact_data = [['📞 分機', '1234'], ['📧 Email', 'support@yujinsheng.com'], ['🤖 AI 助理', 'Jenny']]
    contact_table = Table(contact_data, colWidths=[4*cm, 6*cm])
    contact_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (0, -1), 'MicrosoftJhengHei-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 11), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
    story.append(contact_table)
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("© 2026 昱金生能源股份有限公司", ParagraphStyle('Copyright', parent=styles['Normal'], fontName='MicrosoftJhengHei', fontSize=9, textColor=colors.grey, alignment=TA_CENTER)))
    
    doc.build(story)
    print("✅ 董事長快速指南 PDF 已生成")

if __name__ == "__main__":
    create_chairman_guide()
