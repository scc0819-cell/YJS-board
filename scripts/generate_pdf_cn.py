#!/usr/bin/env python3
"""
昱金生能源集團 - 員工日報分析報告生成器 (完整版 - 支援中文)
使用 reportlab 與 Noto Sans CJK 字體
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 註冊中文字體
font_paths = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]

# 嘗試註冊字體
try:
    pdfmetrics.registerFont(TTFont('NotoSansCJK', font_paths[0]))
    pdfmetrics.registerFont(TTFont('NotoSansCJK-Bold', font_paths[1]))
    print("✅ 中文字體註冊成功")
except Exception as e:
    print(f"⚠️ 字體註冊失敗：{e}")

# 員工日報數據
EMPLOYEE_REPORTS = [
    {"name": "高竹妤", "email": "cukao@yjsenergy.com", "position": "設計工程師", "score": 92, "risk_level": "低", "category": "設計圖面/竣工備查",
     "today_work": ["P 圖：56-A 竣工備查、52-A 竣工備查、12-1 設備登記", "修改結構審查圖面：61-A、61-B、58-A、26-1"],
     "tomorrow_plan": ["嘗試用 tekla 蓋 43-A 的鋼構", "P 圖：56-A 竣工備查"],
     "analysis": "負責多個案場的設計圖面修改與竣工圖製作，工作量飽滿且效率高，同時處理 6 個以上案場圖面。",
     "actions": ["確認圖面審查通過狀況", "追蹤 tekla 鋼構建模進度"]},
    {"name": "陳明德", "email": "alexchen@yjsenergy.com", "position": "工程師", "score": 90, "risk_level": "中", "category": "行政作業/會議準備",
     "today_work": ["整理同意備案資料提供縣府備查", "每一案需列印用印及蓋與正本相符", "收到漳和光電球場電力技師資料，用印後連同展延函送給漳和組長", "馬偕明天開會，與 ERIC 確認狀況"],
     "risks": ["馬偕開會當天變天，擔心土壤未乾影響夯實進度", "用印作業耗時"],
     "analysis": "大量行政作業（用印、備查）仍按時完成，主動關注馬偕案場天候風險，責任心強。",
     "actions": ["追蹤馬偕會議結果", "確認土壤夯實條件與天候影響評估"]},
    {"name": "陳谷濱 (BEN)", "email": "eng@yjsenergy.com", "position": "工程師", "score": 88, "risk_level": "低", "category": "現場現勘/物料協調",
     "today_work": ["北斗國中 - 空拍、台電設計課現勘", "永靖國中 - 物料置放區校方協調（預計下周進物料）"],
     "analysis": "負責多個彰化案場的現勘與物料協調，永靖國中預計下周進物料，進度掌控良好。",
     "actions": ["確認北斗國中現勘結果", "追蹤永靖國中物料進場時程"]},
    {"name": "張億峖", "email": "eng@yjsenergy.com", "position": "工程師", "score": 87, "risk_level": "低", "category": "路權申辦/物料配送",
     "today_work": ["申辦忠孝國小路權", "陸豐送電錶給工班"],
     "analysis": "負責路權申辦與電錶配送，陸豐國小進度良好，工作明確。",
     "actions": ["確認忠孝國小路權進度", "追蹤陸豐國小掛錶進度"]},
    {"name": "楊宗衛", "email": "eng@yjsenergy.com", "position": "工程師", "score": 85, "risk_level": "中", "category": "工程會議/巡場",
     "today_work": ["2/25 行程規劃", "上午 - 馬偕工程會議", "下午 - 馬偕光電球場 - 巡場"],
     "analysis": "負責馬偕護專案場的工程會議與現場巡視，需關注天候對施工進度的影響。",
     "actions": ["追蹤馬偕會議結論", "確認天候影響評估"]},
    {"name": "李雅婷", "email": "colleenlee@yjsenergy.com", "position": "行政/標案", "score": 82, "risk_level": "中", "category": "政府標案/進度追蹤",
     "today_work": ["併審&同備&免雜進度更新（2/24 與 2/13 進度同）", "詢問修樹廠商報價：31 萬合國小 +38 長安國小"],
     "risks": ["進度與 2/13 相同，可能停滯"],
     "analysis": "負責政府標案進度追蹤，修樹報價進行中，但進度停滯需加強追蹤力度。",
     "actions": ["催促修樹廠商儘快報價", "主動追蹤標案審查進度，避免停滯"]},
    {"name": "陳靜儒", "email": "mat@yjsenergy.com", "position": "物料/行政", "score": 75, "risk_level": "低", "category": "行政支援",
     "today_work": ["工作日誌（無具體內容）"],
     "analysis": "日報內容較簡略，建議增加具體工作項目與進度說明，以提升回報品質。",
     "actions": ["建議完善日報內容，具體列舉工作項目", "增加進度百分比或完成狀況說明"]}
]

def create_pdf():
    output_path = "/home/yjsclaw/.openclaw/workspace/reports/2026-02-25_員工日報分析報告_完整版.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    content = []
    styles = getSampleStyleSheet()
    
    # 自訂樣式（使用中文）
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#2c5282'),
                                  spaceAfter=30, alignment=TA_CENTER, fontName='NotoSansCJK-Bold')
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#666666'),
                                     spaceAfter=20, alignment=TA_CENTER, fontName='NotoSansCJK')
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#2c5282'),
                                    spaceAfter=12, spaceBefore=12, fontName='NotoSansCJK-Bold')
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=14, textColor=colors.HexColor('#4299e1'),
                                       spaceAfter=10, spaceBefore=10, fontName='NotoSansCJK-Bold')
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#333333'),
                                   spaceAfter=6, leading=16, fontName='NotoSansCJK')
    footer_style = ParagraphStyle('Footer', parent=normal_style, alignment=TA_CENTER, fontSize=9,
                                   textColor=colors.HexColor('#999999'))
    
    # 標題
    content.append(Paragraph("昱金生能源集團", title_style))
    content.append(Paragraph("員工工作日報分析報告", subtitle_style))
    content.append(Paragraph("報告日期：2026 年 2 月 25 日", ParagraphStyle('temp', parent=normal_style, alignment=TA_CENTER)))
    content.append(Spacer(1, 0.5*cm))
    
    # 基本資訊
    meta_data = [["報告日期", "2026-02-25"], ["分析員工人數", "7 位"], ["平均評分", "85.6 分"]]
    meta_table = Table(meta_data, colWidths=[6*cm, 6*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'NotoSansCJK'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    content.append(meta_table)
    content.append(Spacer(1, 0.5*cm))
    
    # 評分分佈
    content.append(Paragraph("評分分佈", heading_style))
    score_dist = [
        ["評分等級", "人數", "員工名單"],
        ["優秀 (90-100 分)", "2 位", "高竹妤 (92)、陳明德 (90)"],
        ["良好 (85-89 分)", "3 位", "陳谷濱 (88)、張億峖 (87)、楊宗衛 (85)"],
        ["普通 (80-84 分)", "1 位", "李雅婷 (82)"],
        ["待改進 (75-79 分)", "1 位", "陳靜儒 (75)"]
    ]
    score_table = Table(score_dist, colWidths=[5*cm, 3*cm, 7*cm])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSansCJK-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f0fff4')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#ebf8ff')),
    ]))
    content.append(score_table)
    content.append(Spacer(1, 0.5*cm))
    
    # 個別員工分析
    content.append(Paragraph("個別員工詳細分析", heading_style))
    
    for i, emp in enumerate(EMPLOYEE_REPORTS, 1):
        content.append(Paragraph(f"{i}. {emp['name']} - {emp['position']}", subheading_style))
        
        emp_info = [["信箱", emp["email"]], ["評分", f"{emp['score']} 分"], ["風險等級", emp["risk_level"]], ["工作類別", emp["category"]]]
        emp_table = Table(emp_info, colWidths=[3*cm, 10*cm])
        emp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
            ('FONTNAME', (0, 0), (0, -1), 'NotoSansCJK-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        content.append(emp_table)
        
        content.append(Paragraph("<b>今日工作：</b>", normal_style))
        for work in emp["today_work"]:
            content.append(Paragraph(f"  • {work}", normal_style))
        
        if emp.get("tomorrow_plan"):
            content.append(Paragraph("<b>明日計畫：</b>", normal_style))
            for plan in emp["tomorrow_plan"]:
                content.append(Paragraph(f"  • {plan}", normal_style))
        
        if emp.get("risks"):
            content.append(Paragraph("<b>風險事項：</b>", normal_style))
            for risk in emp["risks"]:
                content.append(Paragraph(f"  ⚠ {risk}", normal_style))
        
        content.append(Paragraph("<b>分析評語：</b>", normal_style))
        content.append(Paragraph(f"  {emp['analysis']}", normal_style))
        
        content.append(Paragraph("<b>行動建議：</b>", normal_style))
        for action in emp["actions"]:
            content.append(Paragraph(f"  ✓ {action}", normal_style))
        
        content.append(Spacer(1, 0.3*cm))
    
    # 風險提示
    content.append(Paragraph("風險提示彙總", heading_style))
    risk_data = [
        ["風險等級", "事項", "負責人", "建議處理"],
        ["中", "馬偕護專案場 - 天候影響土壤夯實進度", "陳明德、楊宗衛", "關注天氣預報，評估延期可能"],
        ["中", "政府標案進度停滯", "李雅婷", "主動聯繫承辦窗口"],
        ["中", "用印行政作業耗時", "陳明德", "評估批量用印流程優化"]
    ]
    risk_table = Table(risk_data, colWidths=[2*cm, 6*cm, 4*cm, 4*cm])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSansCJK-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    content.append(risk_table)
    content.append(Spacer(1, 0.5*cm))
    
    # 董事長行動建議
    content.append(Paragraph("董事長行動建議", heading_style))
    content.append(Paragraph("<b>今日優先處理：</b>", normal_style))
    for p in ["關心馬偕護專會議結果及天候影響", "催促李雅婷追蹤政府標案審查進度", "與陳靜儒溝通完善日報內容"]:
        content.append(Paragraph(f"  🔥 {p}", normal_style))
    
    content.append(Spacer(1, 0.3*cm))
    content.append(Paragraph("<b>本週追蹤事項：</b>", normal_style))
    for t in ["永靖國中物料進場（預計下周）", "修樹廠商報價（合國小、長安國小）", "忠孝國小路權申辦進度", "陸豐國小掛錶進度"]:
        content.append(Paragraph(f"  📅 {t}", normal_style))
    
    content.append(Spacer(1, 0.3*cm))
    content.append(Paragraph("<b>表揚建議：</b>", normal_style))
    content.append(Paragraph("  🏆 高竹妤 (92 分) - 設計圖面工作效率優異", normal_style))
    content.append(Paragraph("  🏆 陳明德 (90 分) - 行政作業按時完成，主動關注風險", normal_style))
    
    content.append(Spacer(1, 1*cm))
    content.append(Paragraph("─────────────────────────────────────────", footer_style))
    content.append(Paragraph("報告生成：昱金生能源集團 AI 助理 Jenny", footer_style))
    content.append(Paragraph("聯絡信箱：johnnys@yjsenergy.com | 生成時間：2026-02-28", footer_style))
    
    doc.build(content)
    print(f"✅ PDF 已生成：{output_path}")
    return output_path

if __name__ == "__main__":
    create_pdf()
