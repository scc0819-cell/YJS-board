#!/usr/bin/env python3
"""昱金生能源 - 專業 PDF 手冊生成器 v3.0"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime
import os

# 字體
FONT_PATH = '/mnt/c/Windows/Fonts/msjh.ttc'
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('MSJH', FONT_PATH))
    print(f"✅ 字體已註冊：{FONT_PATH}")

WORKSPACE = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server')
OUTPUT_DIR = WORKSPACE / 'docs'
OUTPUT_DIR.mkdir(exist_ok=True)

# 配色
C = {
    'PRIMARY': '#1e3a5f', 'DARK': '#0f172a', 'ACCENT': '#0ea5e9',
    'SUCCESS': '#10b981', 'DANGER': '#ef4444', 'LIGHT': '#f8fafc',
    'BORDER': '#e2e8f0', 'TEXT': '#1e293b', 'MEDIUM': '#475569'
}

def get_styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle('CT', fontName='MSJH', fontSize=32, textColor=colors.HexColor(C['DARK']),
        alignment=TA_CENTER, leading=42))
    s.add(ParagraphStyle('CS', fontName='MSJH', fontSize=18, textColor=colors.HexColor(C['PRIMARY']),
        alignment=TA_CENTER, leading=28))
    s.add(ParagraphStyle('CH', fontName='MSJH', fontSize=20, textColor=colors.HexColor(C['DARK']),
        spaceAfter=25, spaceBefore=30, leading=30))
    s.add(ParagraphStyle('SH', fontName='MSJH', fontSize=16, textColor=colors.HexColor(C['PRIMARY']),
        spaceAfter=18, spaceBefore=25, leading=24))
    s.add(ParagraphStyle('SS', fontName='MSJH', fontSize=13, textColor=colors.HexColor(C['PRIMARY']),
        spaceAfter=12, spaceBefore=18, leading=20))
    s.add(ParagraphStyle('BT', fontName='MSJH', fontSize=11, textColor=colors.HexColor(C['TEXT']),
        alignment=TA_JUSTIFY, leading=20, spaceAfter=10))
    s.add(ParagraphStyle('CODE', fontName='MSJH', fontSize=10, textColor='#dc2626',
        backColor=colors.HexColor('#f1f5f9'), borderWidth=1, borderColor=colors.HexColor(C['BORDER']),
        borderPadding=8))
    return s

def header(canvas, doc, title):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor(C['PRIMARY']))
    canvas.rect(0, A4[1]-15, A4[0], 15, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont('MSJH', 9)
    canvas.drawString(2*cm, A4[1]-12, '昱金生能源股份有限公司')
    canvas.drawRightString(A4[0]-2*cm, A4[1]-12, title)
    canvas.restoreState()

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor(C['BORDER']))
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 2.5*cm, A4[0]-2*cm, 2.5*cm)
    canvas.setFillColor(colors.HexColor('#94a3b8'))
    canvas.setFont('MSJH', 9)
    canvas.drawRightString(A4[0]-2*cm, 2*cm, f'第 {canvas.getPageNumber()} 頁')
    canvas.restoreState()

def gen_manual():
    print("\n📘 生成專業版員工手冊...")
    doc = SimpleDocTemplate(str(OUTPUT_DIR/'EMPLOYEE_MANUAL_PRO.pdf'), pagesize=A4,
        rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=3*cm, bottomMargin=3*cm)
    s = get_styles()
    story = []
    
    # 封面
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("昱金生能源", s['CT']))
    story.append(Paragraph("YUJINSHENG ENERGY", ParagraphStyle('EN', fontName='MSJH', fontSize=14,
        textColor=colors.HexColor(C['MEDIUM']), alignment=TA_CENTER)))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("員工操作手冊", s['CS']))
    story.append(Paragraph("智能日報系統", ParagraphStyle('DS', fontName='MSJH', fontSize=14,
        textColor=colors.HexColor(C['MEDIUM']), alignment=TA_CENTER)))
    story.append(Spacer(1, 2*cm))
    
    ver = [['文件版本', 'v3.0 正式版'], ['更新日期', datetime.now().strftime('%Y/%m/%d')],
           ['適用對象', '全體員工（15 人）'], ['保密等級', '內部機密'],
           ['權限', '游若誼：Manager | 其餘：Employee']]
    vt = Table(ver, colWidths=[3*cm, 5*cm])
    vt.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSJH'),('FONTSIZE',(0,0),(-1,-1),10),
        ('ALIGN',(0,0),(0,-1),'LEFT'),('ALIGN',(1,0),(1,-1),'RIGHT'),
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor(C['LIGHT'])),
        ('BOX',(0,0),(-1,-1),1,colors.HexColor(C['BORDER']))]))
    story.append(vt)
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("© 2026 昱金生能源 版權所有",
        ParagraphStyle('CP', fontName='MSJH', fontSize=9, textColor=colors.HexColor('#94a3b8'),
            alignment=TA_CENTER)))
    story.append(PageBreak())
    
    # 目錄
    story.append(Paragraph("目錄", s['CH']))
    toc = [['第 1 章','系統概論','1'],['1.1','系統介紹','1'],['1.2','系統特色','2'],['1.3','使用效益','3'],
           ['第 2 章','快速開始','4'],['2.1','系統登入','4'],['2.2','介面導覽','6'],
           ['第 3 章','填寫日報','9'],['3.1','基本流程','9'],['3.2','優秀範例','11'],
           ['第 4 章','AI 功能','15'],['第 5 章','常見問題','19'],['第 6 章','最佳實踐','22']]
    tt = Table(toc, colWidths=[1.5*cm, 8*cm, 1.5*cm])
    tt.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSJH'),('FONTSIZE',(0,0),(-1,-1),10),
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor(C['PRIMARY'])),('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('BOX',(0,0),(-1,-1),1,colors.HexColor(C['BORDER']))]))
    story.append(tt)
    story.append(PageBreak())
    
    # 第 1 章
    story.append(Paragraph("第 1 章 系統概論", s['CH']))
    story.append(Paragraph("1.1 系統介紹", s['SH']))
    story.append(Paragraph("""昱金生能源智能日報系統是一套整合 AI 技術的專案管理工具，
    專為太陽能光電工程團隊設計。系統協助員工記錄每日工作進度，並透過 AI 分析提供即時建議，
    提升團隊協作效率。""", s['BT']))
    
    arch = [['層級','組成','說明'],['使用者層','員工/主管/董事長','網頁瀏覽器'],
            ['應用層','日報系統/AI/通知','Flask Web'],['資料層','SQLite/郵件','結構儲存'],
            ['基礎層','WSL2/Windows','本地部署']]
    at = Table(arch, colWidths=[2.5*cm, 5*cm, 5*cm])
    at.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSJH'),('FONTSIZE',(0,0),(-1,-1),10),
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor(C['PRIMARY'])),('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('BOX',(0,0),(-1,-1),1,colors.HexColor(C['BORDER'])),('INNERGRID',(0,0),(-1,-1),0.5,colors.HexColor(C['BORDER']))]))
    story.append(at)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("1.2 系統特色", s['SH']))
    for icon, title, desc in [('🤖','AI 智慧分析','自動分析工作，提供個人化建議'),
                              ('📊','即時進度','掌握案場進度'), ('🔔','智慧提醒','自動提醒'),
                              ('📧','郵件整合','分析歷史郵件'), ('📱','多裝置','電腦/平板/手機'),
                              ('🔒','權限管理','分層控制')]:
        story.append(Paragraph(f"{icon} <b>{title}</b>", s['SS']))
        story.append(Paragraph(desc, s['BT']))
        story.append(Spacer(1, 0.3*cm))
    story.append(PageBreak())
    
    story.append(Paragraph("1.3 使用效益", s['SH']))
    ben = [['項目','傳統','系統後','改善'],['進度掌握','30 分/天','3 分/天','⬇️90%'],
           ['錯誤遺漏','15%','<2%','⬇️87%'], ['溝通成本','高','低','⬇️60%'],
           ['決策速度','慢','即時','⬆️300%']]
    bt = Table(ben, colWidths=[3*cm, 3*cm, 3*cm, 3*cm])
    bt.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSJH'),('FONTSIZE',(0,0),(-1,-1),10),
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor(C['PRIMARY'])),('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('BOX',(0,0),(-1,-1),1,colors.HexColor(C['BORDER'])),('INNERGRID',(0,0),(-1,-1),0.5,colors.HexColor(C['BORDER']))]))
    story.append(bt)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>適用人員（15 人）</b>", s['SS']))
    usr = [['管理部','宋啓綸、游若誼、洪淑嫆、楊傑麟、褚佩瑜','管理監督'],
           ['工程部','楊宗衛、張億峖、陳明德、李雅婷、陳谷濱','案場施工'],
           ['維運部','陳靜儒','電廠維護'], ['行政部','林天睛、呂宜芹','行政'],
           ['設計部','顏呈晞、高竹妤','設計']]
    ut = Table(usr, colWidths=[2*cm, 6*cm, 3.5*cm])
    ut.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSJH'),('FONTSIZE',(0,0),(-1,-1),9),
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor(C['PRIMARY'])),('TEXTCOLOR',(0,0),(0,-1),colors.white),
        ('BOX',(0,0),(-1,-1),1,colors.HexColor(C['BORDER'])),('INNERGRID',(0,0),(-1,-1),0.5,colors.HexColor(C['BORDER']))]))
    story.append(ut)
    story.append(PageBreak())
    
    # 第 2 章
    story.append(Paragraph("第 2 章 快速開始", s['CH']))
    story.append(Paragraph("2.1 系統登入", s['SH']))
    story.append(Paragraph("<b>步驟 1：開啟瀏覽器</b>", s['SS']))
    story.append(Paragraph("支援：Chrome、Edge、Firefox（建議 Chrome）", s['BT']))
    story.append(Paragraph("<b>步驟 2：輸入網址</b>", s['SS']))
    story.append(Paragraph("http://localhost:5000", s['CODE']))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>步驟 3：輸入帳號密碼</b>", s['SS']))
    for i, step in enumerate(['輸入員工編號（例：23102）', '輸入密碼：Welcome2026!',
                              '點擊登入', '首次登入需修改密碼'], 1):
        story.append(Paragraph(f"<b>{i}.</b> {step}", s['BT']))
    story.append(Spacer(1, 0.5*cm))
    
    acc = [['編號','姓名','部門','權限','密碼'],['20101','宋啓綸','管理部','Admin','Welcome2026!'],
           ['20102','游若誼','管理部','Manager','Welcome2026!'], ['23102','楊宗衛','工程部','Employee','Welcome2026!'],
           ['24302','張億峖','工程部','Manager','Welcome2026!'], ['25105','陳明德','工程部','Manager','Welcome2026!']]
    act = Table(acc, colWidths=[1.5*cm, 2*cm, 2*cm, 2*cm, 3*cm])
    act.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSJH'),('FONTSIZE',(0,0),(-1,-1),9),
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor(C['PRIMARY'])),('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('BOX',(0,0),(-1,-1),1,colors.HexColor(C['BORDER'])),('INNERGRID',(0,0),(-1,-1),0.5,colors.HexColor(C['BORDER']))]))
    story.append(act)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("<b>⚠️</b> 首次登入必須修改密碼，每 90 天更換", s['BT']))
    story.append(PageBreak())
    
    # 第 3 章
    story.append(Paragraph("第 3 章 填寫日報", s['CH']))
    story.append(Paragraph("3.1 基本流程", s['SH']))
    flow = [['登入','→','進入','→','選日期','→','填寫','→','送出']]
    ft = Table(flow, colWidths=[1.5*cm, 0.5*cm, 1.5*cm, 0.5*cm, 1.5*cm, 0.5*cm, 1.5*cm, 0.5*cm, 1.5*cm])
    ft.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSJH'),('FONTSIZE',(0,0),(-1,-1),10),
        ('BACKGROUND',(0,0),(0,0),colors.HexColor(C['PRIMARY'])),('BACKGROUND',(2,0),(2,0),colors.HexColor(C['ACCENT'])),
        ('BACKGROUND',(4,0),(4,0),colors.HexColor(C['SUCCESS'])),('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),('BOX',(0,0),(-1,-1),1,colors.HexColor(C['BORDER']))]))
    story.append(ft)
    story.append(Spacer(1, 0.5*cm))
    
    for icon, title, desc in [('1️⃣','登入系統','使用員工編號和密碼'), ('2️⃣','點擊填寫日報','首頁綠色按鈕'),
                              ('3️⃣','選擇日期','預設今日，可補填 7 天'), ('4️⃣','選擇案場','下拉選單'),
                              ('5️⃣','填寫內容','具體描述'), ('6️⃣','填寫進度','0-100%'),
                              ('7️⃣','記錄問題','詳細描述'), ('8️⃣','檢查送出','確認無誤')]:
        story.append(Paragraph(f"{icon} <b>{title}</b>", s['SS']))
        story.append(Paragraph(desc, s['BT']))
        story.append(Spacer(1, 0.2*cm))
    story.append(PageBreak())
    
    # 範例
    story.append(Paragraph("3.2 優秀範例", s['SH']))
    good = [['案場','仁豐國小'],['工作','1.光電板安裝 (15-20 片)\n2.逆變器測試\n3.清潔'],
            ['內容','• 完成 15-20 片安裝，M8 螺栓\n• 測試正常 (DC600V,AC220V)\n• 清理回收'],
            ['進度','95%'], ['問題','無'], ['明日','1.初驗文件\n2.聯繫台電']]
    gt = Table(good, colWidths=[2*cm, 8.5*cm])
    gt.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSJH'),('FONTSIZE',(0,0),(-1,-1),10),
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#e8f5e9')),
        ('BOX',(0,0),(-1,-1),2,colors.HexColor(C['SUCCESS'])),
        ('INNERGRID',(0,0),(-1,-1),0.5,colors.HexColor(C['BORDER'])),('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(gt)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("<b>❌ 錯誤範例</b>", s['SS']))
    bad = [['案場','仁豐國小'],['工作','施工'],['內容','安裝'],['進度','50%'],['問題','無'],['明日','繼續']]
    btt = Table(bad, colWidths=[2*cm, 8.5*cm])
    btt.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSJH'),('FONTSIZE',(0,0),(-1,-1),10),
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#ffebee')),
        ('BOX',(0,0),(-1,-1),2,colors.HexColor(C['DANGER'])),
        ('INNERGRID',(0,0),(-1,-1),0.5,colors.HexColor(C['BORDER'])),('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(btt)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("""<b>💡 建議：</b><br/>• 使用具體數字<br/>• 描述完整流程<br/>• 說明進度計算<br/>• 列出明日目標""", s['BT']))
    story.append(PageBreak())
    
    # Q&A
    story.append(Paragraph("第 5 章 常見問題", s['CH']))
    qa = [['<b>Q1. 忘記密碼？</b>','A. 點忘記密碼→輸入 Email→收信重設'],
          ['<b>Q2. 可補填？</b>','A. 7 天內可補，超過找主管'],
          ['<b>Q3. 無工作？</b>','A. 仍填寫（休假/訓練/會議）'],
          ['<b>Q4. AI 準確？</b>','A. 越用越準，可回饋'],
          ['<b>Q5. 補充請求？</b>','A. 3 天內回覆']]
    qat = Table(qa, colWidths=[4*cm, 8*cm])
    qat.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSJH'),('FONTSIZE',(0,0),(-1,-1),10),
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor(C['LIGHT'])),
        ('BOX',(0,0),(-1,-1),1,colors.HexColor(C['BORDER'])),('INNERGRID',(0,0),(-1,-1),0.5,colors.HexColor(C['BORDER'])),
        ('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(qat)
    story.append(PageBreak())
    
    # 最佳實踐
    story.append(Paragraph("第 6 章 最佳實踐", s['CH']))
    tips = [['✅','具體明確','描述實際工作'],['✅','有數據','用數字百分比'],
            ['✅','有脈絡','說明背景'],['✅','有照片','重要進度拍照'],
            ['✅','有計畫','列明日目標'],['❌','太簡略','避免施工會議'],
            ['❌','無數據','不只百分比'],['❌','延遲','當日下班前']]
    tipt = Table(tips, colWidths=[0.8*cm, 2*cm, 6.7*cm])
    tipt.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSJH'),('FONTSIZE',(0,0),(-1,-1),10),
        ('ALIGN',(0,0),(0,-1),'CENTER'),('BOX',(0,0),(-1,-1),1,colors.HexColor(C['BORDER'])),
        ('INNERGRID',(0,0),(-1,-1),0.5,colors.HexColor(C['BORDER']))]))
    story.append(tipt)
    
    # 結尾
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("="*50, ParagraphStyle('DIV', fontName='MSJH', fontSize=16,
        textColor=colors.HexColor(C['PRIMARY']), alignment=TA_CENTER)))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("感謝使用！", s['SH']))
    story.append(Paragraph("""聯繫方式：<br/>• 分機 1234<br/>• support@yujinsheng.com<br/>• 週一~五 09:00-18:00""", s['BT']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("昱金生能源 管理團隊", s['BT']))
    
    doc.build(story, onFirstPage=lambda c,d: (header(c,d,"員工手冊"), footer(c,d)),
              onLaterPages=lambda c,d: (header(c,d,"員工手冊"), footer(c,d)))
    print(f"✅ 已生成：{OUTPUT_DIR/'EMPLOYEE_MANUAL_PRO.pdf'}")

if __name__ == '__main__':
    print("="*60)
    print("📄 昱金生能源 - 專業手冊 v3.0")
    print("="*60)
    gen_manual()
    print("\n✅ 完成！")
