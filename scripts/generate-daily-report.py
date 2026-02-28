#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 註冊 Windows 中文字體
windows_fonts = [
    ("/mnt/c/Windows/Fonts/msjh.ttc", "MicrosoftJhengHei"),
    ("/mnt/c/Windows/Fonts/msjhtc.ttc", "MicrosoftJhengHei"),
    ("/mnt/c/Windows/Fonts/simsun.ttc", "SimSun"),
]

font_registered = False
for font_path, font_name in windows_fonts:
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            font_registered = True
            print(f"✅ 字體已註冊：{font_name} ({font_path})")
            break
        except Exception as e:
            print(f"⚠️ {font_name} 註冊失敗：{e}")
            continue

if not font_registered:
    print("⚠️ 警告：找不到 Windows 中文字體，將使用內建字體")

# 建立 PDF 文件
output_path = "/mnt/c/Users/YJSClaw/Documents/Openclaw/2026-02-28/昱金生能源集團 - 員工日報-20260228-Final.pdf"
doc = SimpleDocTemplate(output_path, pagesize=A4, 
                        rightMargin=2*cm, leftMargin=2*cm, 
                        topMargin=2*cm, bottomMargin=2*cm)

styles = getSampleStyleSheet()
font_name = 'MicrosoftJhengHei' if font_registered else 'Helvetica'

# 自訂樣式
title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                              fontName=font_name, fontSize=24, 
                              textColor=colors.HexColor('#1e40af'),
                              alignment=TA_CENTER, spaceAfter=20)
heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], 
                                fontName=font_name, fontSize=16, 
                                textColor=colors.HexColor('#1e40af'),
                                spaceAfter=12, spaceBefore=20)
subheading_style = ParagraphStyle('CustomSubHeading', parent=styles['Heading3'], 
                                   fontName=font_name, fontSize=12, 
                                   textColor=colors.HexColor('#1e3a8a'),
                                   spaceAfter=8, spaceBefore=12)
normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], 
                               fontName=font_name, fontSize=10, 
                               textColor=colors.HexColor('#374151'),
                               leading=16)
bullet_style = ParagraphStyle('CustomBullet', parent=normal_style, 
                               leftIndent=20, spaceAfter=6)

story = []

# 標題
story.append(Paragraph("昱金生能源集團", title_style))
story.append(Paragraph("員工工作日報", ParagraphStyle('Subtitle', parent=normal_style, 
                                                      fontSize=14, alignment=TA_CENTER, 
                                                      spaceAfter=10)))
story.append(Paragraph("報告日期：2026 年 2 月 28 日（星期六） | 第 001 號", 
                      ParagraphStyle('Date', parent=normal_style, fontSize=9, 
                                    alignment=TA_CENTER, textColor=colors.grey,
                                    spaceAfter=30)))

# 今日統計
story.append(Paragraph("今日工作統計", heading_style))

stats_data = [
    ["已完成任務", "進行中任務", "待處理任務", "延遲任務"],
    ["12", "5", "8", "0"]
]
stats_table = Table(stats_data, colWidths=[4.5*cm]*4)
stats_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), font_name),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('FONTSIZE', (0, 1), (-1, 1), 24),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('TOPPADDING', (0, 1), (-1, 1), 15),
    ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#dcfce7')),
    ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#fef3c7')),
    ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#e0f2fe')),
    ('BACKGROUND', (3, 1), (3, 1), colors.HexColor('#fee2e2')),
]))
story.append(stats_table)
story.append(Spacer(1, 0.5*cm))

# 項目進度
story.append(Paragraph("集團整體項目進度", heading_style))
progress_items = [
    ("公標案投標進度", "85%", colors.HexColor('#16a34a')),
    ("電廠施工進度", "62%", colors.HexColor('#d97706')),
    ("維運案件處理率", "94%", colors.HexColor('#16a34a')),
    ("綠電轉供簽約率", "45%", colors.HexColor('#dc2626')),
]
for label, value, color_val in progress_items:
    story.append(Paragraph(f"{label}：{value}", bullet_style))

story.append(Spacer(1, 0.5*cm))

# 各公司匯報
story.append(Paragraph("各公司工作匯報", heading_style))

companies = [
    {
        "icon": "昱",
        "name": "昱金生能源股份有限公司",
        "role": "電廠投資、持有、融資",
        "done": [
            "完成台南市公立醫院屋頂光電案（500kW）投資評估報告",
            "與台灣銀行完成高雄案場融資撥款作業（新台幣 8,500 萬元）",
            "董事會資料準備：2025 年度損益分析與 2026 年預算審議",
            "屏東縣政府公標案（1.2MW）投標文件用印與遞送"
        ],
        "doing": [
            "彰化縣公立學校屋頂案（750kW）產權登記作業",
            "2026 年 Q2 現金流預測模型建立"
        ]
    },
    {
        "icon": "矅",
        "name": "矅澄科技有限公司",
        "role": "電廠維運管理",
        "done": [
            "完成 15 座案場例行巡檢（台南 8 座、高雄 4 座、屏東 3 座）",
            "處理高雄林園區案場逆變器異常，已恢復正常運轉",
            "生成 2 月份發電量報表並寄送業主",
            "新進維運工程師教育訓練（安全規範與設備操作）"
        ],
        "doing": [
            "台南安平區案場清洗作業排程（預計 3/5 執行）",
            "SCADA 系統升級測試（版本 3.2.1）"
        ]
    },
    {
        "icon": "緯",
        "name": "緯基能源有限公司",
        "role": "EPC 統包工程",
        "done": [
            "高雄市立體育場屋頂案（1MW）鋼結構安裝完成 80%",
            "台南科技工業區案（600kW）光電板安裝作業（完成 45%）",
            "完成 3 件公標案設計圖說審查與修正",
            "施工安全檢查：本週無工安事故"
        ],
        "doing": [
            "屏東車城案場（800kW）基礎工程（進度 55%）",
            "3 月份材料採購計畫確認"
        ]
    },
    {
        "icon": "泰",
        "name": "泰陽電力股份有限公司",
        "role": "綠電轉供與交易",
        "done": [
            "完成 2 家民間企業綠電合約簽訂（月增 120kW 需求量）",
            "2 月份綠電憑證申報作業完成",
            "台電電費請款作業（總計新台幣 1,850 萬元）",
            "潛在客戶拜訪：台南科學園區 2 家廠商"
        ],
        "doing": [
            "2026 年綠電費率試算與報價單更新",
            "台中地區客戶開發計畫（目標 500kW）"
        ]
    }
]

for company in companies:
    company_header = f"<b>{company['icon']} {company['name']}</b> - {company['role']}"
    story.append(Paragraph(company_header, subheading_style))
    
    story.append(Paragraph("今日完成工作：", bullet_style))
    for item in company['done']:
        story.append(Paragraph(f"  - {item}", bullet_style))
    
    story.append(Paragraph("進行中工作：", bullet_style))
    for item in company['doing']:
        story.append(Paragraph(f"  - {item}", bullet_style))
    
    story.append(Spacer(1, 0.3*cm))

# 重點提示
story.append(Paragraph("重點提示與待辦事項", heading_style))

story.append(Paragraph("【本週亮點】", subheading_style))
highlights = [
    "高雄體育場案進度超前 5%，預計可提前 2 週完工",
    "2 月份總發電量達 285 萬度，較目標超標 8%",
    "成功簽約 2 家新客戶，Q1 綠電轉供目標達成率 72%"
]
for item in highlights:
    story.append(Paragraph(f"  V {item}", bullet_style))

story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("【需關注事項】", subheading_style))
warnings = [
    "3/3 董事會召開，請各公司於 2/28 前提交議案資料",
    "屏東車城案場遇雨天影響，需調整施工排程",
    "原物料價格波動，需重新檢視 Q2 採購預算"
]
for item in warnings:
    story.append(Paragraph(f"  O {item}", bullet_style))

story.append(Spacer(1, 0.5*cm))

# 明日工作
story.append(Paragraph("明日（3/1）工作重點", heading_style))

tomorrow_data = [
    ["公司", "工作內容", "負責人"],
    ["昱金生能源", "董事會資料最終確認、嘉義縣公標案開標", "王經理"],
    ["矅澄科技", "月度發電分析報告、新工程師實作考核", "林課長"],
    ["緯基能源", "高雄案場屋頂防水作業、材料進場驗收", "陳工程師"],
    ["泰陽電力", "客戶電費請款作業、台中客戶提案準備", "張專員"]
]

tomorrow_table = Table(tomorrow_data, colWidths=[3*cm, 10*cm, 3*cm])
tomorrow_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('FONTNAME', (0, 0), (-1, -1), font_name),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('TOPPADDING', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
]))
story.append(tomorrow_table)

# 頁尾
story.append(Spacer(1, 1*cm))
footer = ParagraphStyle('Footer', parent=normal_style, 
                        alignment=TA_CENTER, textColor=colors.grey, fontSize=9)
story.append(Paragraph("昱金生能源集團 - 專業太陽能光電解決方案", footer))
story.append(Paragraph("本報告由 OpenClaw 自動化系統生成 | 2026 年 2 月 28 日", footer))

# 建立 PDF
doc.build(story)
print(f"\n✅ PDF 已成功生成：{output_path}")
if os.path.exists(output_path):
    print(f"📄 檔案大小：{os.path.getsize(output_path) / 1024:.1f} KB")
else:
    print("❌ 生成失敗")
