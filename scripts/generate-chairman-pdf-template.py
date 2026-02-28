#!/usr/bin/env python3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime

FONT_REG='/mnt/c/Windows/Fonts/msjh.ttc'
FONT_BOLD='/mnt/c/Windows/Fonts/msjhbd.ttc'
pdfmetrics.registerFont(TTFont('MSJH', FONT_REG))
pdfmetrics.registerFont(TTFont('MSJHB', FONT_BOLD))

out_dir=Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/2026-03-01')
out_dir.mkdir(parents=True, exist_ok=True)
out=out_dir/'董事長報告模板_v2_示例.pdf'

doc=SimpleDocTemplate(str(out), pagesize=A4, leftMargin=42, rightMargin=42, topMargin=36, bottomMargin=36)
styles=getSampleStyleSheet()

h1=ParagraphStyle('h1', parent=styles['Heading1'], fontName='MSJHB', fontSize=22, leading=28, textColor=colors.HexColor('#0F172A'))
sub=ParagraphStyle('sub', parent=styles['Normal'], fontName='MSJH', fontSize=11, leading=16, textColor=colors.HexColor('#475569'))
sec=ParagraphStyle('sec', parent=styles['Heading2'], fontName='MSJHB', fontSize=13, leading=20, textColor=colors.HexColor('#1D4ED8'))
body=ParagraphStyle('body', parent=styles['Normal'], fontName='MSJH', fontSize=11.2, leading=18, textColor=colors.HexColor('#111827'))

story=[]
story.append(Paragraph('昱金生能源集團｜董事長營運簡報（示例）', h1))
story.append(Paragraph(f'報告日期：{datetime.now().strftime("%Y-%m-%d %H:%M")}（GMT+8）', sub))
story.append(Spacer(1, 12))

story.append(Paragraph('一句話結論', sec))
story.append(Paragraph('今日整體發電健康維持穩定，需優先關注 3 座場站在晴天條件下發電落差超過 3%。', body))
story.append(Spacer(1, 8))

story.append(Paragraph('核心 KPI 儀表', sec))
rows=[
['指標','目前值','目標','狀態'],
['發電達成率','97.8%','≥98.0%','🟡'],
['逆變器可用率','99.2%','≥99.0%','🟢'],
['資料完整率','98.9%','≥99.0%','🟡'],
['P1/P2/P3','0 / 2 / 6','越低越好','🟡'],
]
t=Table(rows, colWidths=[110,90,90,60])
t.setStyle(TableStyle([
('FONTNAME',(0,0),(-1,0),'MSJHB'),('FONTNAME',(0,1),(-1,-1),'MSJH'),
('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E2E8F0')),
('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#0F172A')),
('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#CBD5E1')),
('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#F8FAFC')]),
('ALIGN',(1,1),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
]))
story.append(t)
story.append(Spacer(1,10))

story.append(Paragraph('今日行動清單', sec))
for i,txt in enumerate([
'針對 A 場站檢查逆變器 3 號串接告警（SLA 4 小時）',
'針對 B 場站比對今昨日日照差與發電落差，確認是否遮陰擴大',
'針對 C 場站安排清洗與熱像檢測，48 小時內回報',
],1):
    story.append(Paragraph(f'{i}. {txt}', body))

story.append(Spacer(1,14))
story.append(Paragraph('備註：本版面為 v2 設計樣板（強化留白、字重層級、表格風格）。', sub))

doc.build(story)
print(out)
