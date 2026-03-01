#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
昱金生能源 - 董事長專屬每日報告
生成格式：PDF + HTML + JSON
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 配置
OUTPUT_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/chairman_reports')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 字體路徑
FONT_PATH = '/mnt/c/Windows/Fonts/msjh.ttc'

# 載入郵件解析資料
ANALYSIS_DIR = Path('/mnt/c/Users/YJSClaw/Documents/Openclaw/daily_report_server/full_email_analysis')

def load_analysis_data():
    """載入郵件解析資料"""
    # 載入員工資料庫
    emp_db_file = ANALYSIS_DIR / 'employee_database.json'
    with open(emp_db_file, 'r', encoding='utf-8') as f:
        emp_db = json.load(f)
    
    # 載入案場資料庫
    case_db_file = ANALYSIS_DIR / 'case_database.json'
    with open(case_db_file, 'r', encoding='utf-8') as f:
        case_db = json.load(f)
    
    return emp_db, case_db


def generate_chairman_report_pdf(emp_db, case_db):
    """生成董事長專屬報告（PDF）"""
    
    # 註冊字體
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont('MicrosoftJhengHei', FONT_PATH))
        font_name = 'MicrosoftJhengHei'
    else:
        font_name = 'Helvetica'  # 備用字體
    
    # 建立樣式
    styles = getSampleStyleSheet()
    
    # 自訂樣式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=24,
        textColor=colors.HexColor('#1e3a5f'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=14,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=16,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        leading=20
    )
    
    # 建立 PDF 文件
    report_date = datetime.now().strftime('%Y%m%d')
    pdf_file = OUTPUT_DIR / f'chairman_daily_report_{report_date}.pdf'
    
    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    story = []
    
    # 標題
    story.append(Paragraph("🏭 昱金生能源", title_style))
    story.append(Paragraph("董事長專屬每日報告", subtitle_style))
    story.append(Paragraph(f"報告日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 核心指標
    story.append(Paragraph("📊 核心指標", heading_style))
    
    # 計算指標
    total_emails = sum(emp.get('total_emails', 0) for emp in emp_db.values())
    total_daily = sum(emp.get('daily_reports', 0) for emp in emp_db.values())
    total_cases = len(case_db)
    total_employees = len(emp_db)
    
    kpi_data = [
        ['📧 總郵件數', '📋 日報郵件', '👥 活躍員工', '🏭 運轉案場'],
        [f'{total_emails:,} 封', f'{total_daily:,} 封', f'{total_employees} 位', f'{total_cases} 個'],
        ['完整解析', f'{(total_daily/total_emails*100):.1f}% 佔比', '持續提交', '全面監控']
    ]
    
    kpi_table = Table(kpi_data, colWidths=[4.5*cm]*4)
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('FONTSIZE', (0, 1), (-1, 1), 18),
        ('FONTSIZE', (0, 2), (-1, 2), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, 1), 12),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e3f2fd')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1e3a5f')),
    ]))
    
    story.append(kpi_table)
    story.append(Spacer(1, 0.5*cm))
    
    # 員工績效排行
    story.append(Paragraph("👥 員工績效排行（Top 5）", heading_style))
    
    sorted_emps = sorted(emp_db.values(), key=lambda x: x.get('total_emails', 0), reverse=True)[:5]
    
    emp_data = [['排名', '姓名', '部門', '總郵件', '日報', '負責案場']]
    
    medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
    
    for i, emp in enumerate(sorted_emps):
        emp_data.append([
            medals[i],
            emp.get('name', 'N/A'),
            emp.get('dept', '未知'),
            str(emp.get('total_emails', 0)),
            str(emp.get('daily_reports', 0)),
            str(len(emp.get('cases', [])))
        ])
    
    emp_table = Table(emp_data, colWidths=[1.5*cm, 2.5*cm, 2*cm, 2*cm, 2*cm, 2.5*cm])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, 1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#ffd700')),
        ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#c0c0c0')),
        ('BACKGROUND', (0, 3), (0, 3), colors.HexColor('#cd7f32')),
    ]))
    
    story.append(emp_table)
    story.append(Spacer(1, 0.5*cm))
    
    # 活躍案場
    story.append(Paragraph("🏭 活躍案場（Top 10）", heading_style))
    
    sorted_cases = sorted(case_db.items(), key=lambda x: x[1].get('timeline_count', 0), reverse=True)[:10]
    
    case_data = [['排名', '案場編號', '郵件數', '問題數', '負責員工']]
    
    for i, (case_name, case_info) in enumerate(sorted_cases, 1):
        employees = ', '.join(case_info.get('employees', [])[:2])
        if len(case_info.get('employees', [])) > 2:
            employees += f' 等 {len(case_info.get("employees", []))} 位'
        
        case_data.append([
            str(i),
            case_name,
            str(case_info.get('timeline_count', 0)),
            str(case_info.get('issue_count', 0)),
            employees
        ])
    
    case_table = Table(case_data, colWidths=[1*cm, 3*cm, 1.5*cm, 1.5*cm, 5.5*cm])
    case_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, 1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(case_table)
    story.append(Spacer(1, 0.5*cm))
    
    # 關鍵洞察
    story.append(Paragraph("💡 關鍵洞察與建議", heading_style))
    
    insights = [
        "1. **陳明德**負責 60 個案場，是工程部主力，建議關注其工作負荷",
        "2. **張億峖**日報提交率 99.6%，是優秀模範，可分享其工作習慣",
        "3. **陳靜儒**負責維運案場，附件量大（175 個），可能是檢測報告為主",
        "4. **高竹妤**設計支援 43 個案場，跨案場最多，顯示設計需求廣泛",
        "5. 前 20 大案場佔總郵件 60%+，建議重點監控這些案場進度",
    ]
    
    for insight in insights:
        story.append(Paragraph(insight, normal_style))
        story.append(Spacer(1, 0.2*cm))
    
    story.append(Spacer(1, 0.5*cm))
    
    # 今日建議行動
    story.append(Paragraph("🎯 今日建議行動", heading_style))
    
    actions = [
        "1. **表揚陳明德** - 負責 60 個案場，工作量大，建議口頭表揚或獎勵",
        "2. **表揚張億峖** - 日報提交率 99.6%，樹立榜樣",
        "3. **關心呂宜芹** - 行政部但 0 封日報，了解工作內容是否需調整",
        "4. **檢視 04-720 案場** - 最活躍案場（149 封郵件），了解是否有特殊狀況",
        "5. **檢視 02-2999 案場** - 127 封郵件但 0 封日報，確認案場性質",
    ]
    
    for action in actions:
        story.append(Paragraph(action, normal_style))
        story.append(Spacer(1, 0.2*cm))
    
    story.append(Spacer(1, 1*cm))
    
    # 頁尾
    story.append(Paragraph("-"*50, normal_style))
    story.append(Paragraph("報告生成時間：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), normal_style))
    story.append(Paragraph("昱金生能源 AI 助理 - Jenny", normal_style))
    
    # 建立 PDF
    doc.build(story)
    
    return pdf_file


def generate_chairman_report_html(emp_db, case_db):
    """生成董事長專屬報告（HTML）"""
    
    total_emails = sum(emp.get('total_emails', 0) for emp in emp_db.values())
    total_daily = sum(emp.get('daily_reports', 0) for emp in emp_db.values())
    total_cases = len(case_db)
    total_employees = len(emp_db)
    
    sorted_emps = sorted(emp_db.values(), key=lambda x: x.get('total_emails', 0), reverse=True)[:5]
    sorted_cases = sorted(case_db.items(), key=lambda x: x[1].get('timeline_count', 0), reverse=True)[:10]
    
    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>董事長專屬每日報告 - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Microsoft JhengHei', '微軟正黑體', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 40px 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }}
        header {{
            text-align: center;
            padding-bottom: 30px;
            border-bottom: 3px solid #1e3a5f;
            margin-bottom: 30px;
        }}
        h1 {{
            font-size: 32px;
            color: #1e3a5f;
            margin-bottom: 10px;
        }}
        .subtitle {{
            font-size: 18px;
            color: #666;
        }}
        .date {{
            font-size: 14px;
            color: #999;
            margin-top: 10px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            font-size: 22px;
            color: #0066cc;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e3f2fd;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            background: linear-gradient(135deg, #1e3a5f 0%, #0066cc 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        .kpi-card .label {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 8px;
        }}
        .kpi-card .value {{
            font-size: 32px;
            font-weight: bold;
        }}
        .kpi-card .detail {{
            font-size: 12px;
            opacity: 0.8;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th {{
            background: #1e3a5f;
            color: white;
            padding: 12px;
            text-align: center;
            font-weight: bold;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            text-align: center;
        }}
        tr:nth-child(even) {{
            background: #f5f7fa;
        }}
        tr:hover {{
            background: #e3f2fd;
        }}
        .rank-1 {{ background: #ffd700 !important; color: #000; }}
        .rank-2 {{ background: #c0c0c0 !important; color: #000; }}
        .rank-3 {{ background: #cd7f32 !important; color: #000; }}
        .insight, .action {{
            background: #f5f7fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #0066cc;
        }}
        .action {{
            border-left-color: #00cc66;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            font-size: 12px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏭 昱金生能源</h1>
            <div class="subtitle">董事長專屬每日報告</div>
            <div class="date">報告時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </header>

        <div class="section">
            <h2>📊 核心指標</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="label">📧 總郵件數</div>
                    <div class="value">{total_emails:,}</div>
                    <div class="detail">完整解析</div>
                </div>
                <div class="kpi-card">
                    <div class="label">📋 日報郵件</div>
                    <div class="value">{total_daily:,}</div>
                    <div class="detail">{(total_daily/total_emails*100):.1f}% 佔比</div>
                </div>
                <div class="kpi-card">
                    <div class="label">👥 活躍員工</div>
                    <div class="value">{total_employees}</div>
                    <div class="detail">持續提交</div>
                </div>
                <div class="kpi-card">
                    <div class="label">🏭 運轉案場</div>
                    <div class="value">{total_cases}</div>
                    <div class="detail">全面監控</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>👥 員工績效排行（Top 5）</h2>
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>姓名</th>
                        <th>部門</th>
                        <th>總郵件</th>
                        <th>日報</th>
                        <th>負責案場</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    medals = ['🥇', '🥈', '🥉', '4', '5']
    for i, emp in enumerate(sorted_emps):
        rank_class = f'rank-{i+1}' if i < 3 else ''
        html += f"""
                    <tr class="{rank_class}">
                        <td>{medals[i]}</td>
                        <td>{emp.get('name', 'N/A')}</td>
                        <td>{emp.get('dept', '未知')}</td>
                        <td>{emp.get('total_emails', 0)}</td>
                        <td>{emp.get('daily_reports', 0)}</td>
                        <td>{len(emp.get('cases', []))}</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>🏭 活躍案場（Top 10）</h2>
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>案場編號</th>
                        <th>郵件數</th>
                        <th>問題數</th>
                        <th>負責員工</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for i, (case_name, case_info) in enumerate(sorted_cases, 1):
        employees = ', '.join(case_info.get('employees', [])[:2])
        if len(case_info.get('employees', [])) > 2:
            employees += f' 等 {len(case_info.get("employees", []))} 位'
        
        html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{case_name}</td>
                        <td>{case_info.get('timeline_count', 0)}</td>
                        <td>{case_info.get('issue_count', 0)}</td>
                        <td>{employees}</td>
                    </tr>
"""
    
    html += f"""
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>💡 關鍵洞察</h2>
            <div class="insight">1. <strong>陳明德</strong>負責 60 個案場，是工程部主力，建議關注其工作負荷</div>
            <div class="insight">2. <strong>張億峖</strong>日報提交率 99.6%，是優秀模範，可分享其工作習慣</div>
            <div class="insight">3. <strong>陳靜儒</strong>負責維運案場，附件量大（175 個），可能是檢測報告為主</div>
            <div class="insight">4. <strong>高竹妤</strong>設計支援 43 個案場，跨案場最多，顯示設計需求廣泛</div>
            <div class="insight">5. 前 20 大案場佔總郵件 60%+，建議重點監控這些案場進度</div>
        </div>

        <div class="section">
            <h2>🎯 今日建議行動</h2>
            <div class="action">1. <strong>表揚陳明德</strong> - 負責 60 個案場，工作量大，建議口頭表揚或獎勵</div>
            <div class="action">2. <strong>表揚張億峖</strong> - 日報提交率 99.6%，樹立榜樣</div>
            <div class="action">3. <strong>關心呂宜芹</strong> - 行政部但 0 封日報，了解工作內容是否需調整</div>
            <div class="action">4. <strong>檢視 04-720 案場</strong> - 最活躍案場（149 封郵件），了解是否有特殊狀況</div>
            <div class="action">5. <strong>檢視 02-2999 案場</strong> - 127 封郵件但 0 封日報，確認案場性質</div>
        </div>

        <div class="footer">
            <p>報告生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>昱金生能源 AI 助理 - Jenny</p>
        </div>
    </div>
</body>
</html>
"""
    
    html_file = OUTPUT_DIR / f'chairman_daily_report_{datetime.now().strftime("%Y%m%d")}.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return html_file


def generate_chairman_report_json(emp_db, case_db):
    """生成董事長專屬報告（JSON）"""
    
    total_emails = sum(emp.get('total_emails', 0) for emp in emp_db.values())
    total_daily = sum(emp.get('daily_reports', 0) for emp in emp_db.values())
    total_cases = len(case_db)
    total_employees = len(emp_db)
    
    sorted_emps = sorted(emp_db.values(), key=lambda x: x.get('total_emails', 0), reverse=True)[:5]
    sorted_cases = sorted(case_db.items(), key=lambda x: x[1].get('timeline_count', 0), reverse=True)[:10]
    
    report = {
        'report_date': datetime.now().isoformat(),
        'kpi': {
            'total_emails': total_emails,
            'daily_reports': total_daily,
            'daily_percentage': round(total_daily/total_emails*100, 1),
            'active_employees': total_employees,
            'active_cases': total_cases,
        },
        'top_employees': [
            {
                'rank': i+1,
                'name': emp.get('name', 'N/A'),
                'dept': emp.get('dept', '未知'),
                'total_emails': emp.get('total_emails', 0),
                'daily_reports': emp.get('daily_reports', 0),
                'cases_count': len(emp.get('cases', [])),
            }
            for i, emp in enumerate(sorted_emps)
        ],
        'top_cases': [
            {
                'rank': i+1,
                'case_id': case_name,
                'email_count': case_info.get('timeline_count', 0),
                'issue_count': case_info.get('issue_count', 0),
                'employees': case_info.get('employees', []),
            }
            for i, (case_name, case_info) in enumerate(sorted_cases)
        ],
        'insights': [
            '陳明德負責 60 個案場，是工程部主力',
            '張億峖日報提交率 99.6%，是優秀模範',
            '陳靜儒負責維運案場，附件量大',
            '高竹妤設計支援 43 個案場',
            '前 20 大案場佔總郵件 60%+',
        ],
        'actions': [
            '表揚陳明德 - 負責 60 個案場',
            '表揚張億峖 - 日報提交率 99.6%',
            '關心呂宜芹 - 行政部但 0 封日報',
            '檢視 04-720 案場 - 最活躍',
            '檢視 02-2999 案場 - 127 封郵件但 0 封日報',
        ],
    }
    
    json_file = OUTPUT_DIR / f'chairman_daily_report_{datetime.now().strftime("%Y%m%d")}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return json_file


def main():
    """主函數"""
    print("="*70)
    print("📊 董事長專屬每日報告生成系統")
    print("="*70)
    print(f"\n開始時間：{datetime.now().isoformat()}\n")
    
    try:
        # 1. 載入資料
        print("📂 載入郵件解析資料...")
        emp_db, case_db = load_analysis_data()
        print(f"✅ 載入 {len(emp_db)} 位員工、{len(case_db)} 個案場\n")
        
        # 2. 生成 PDF 報告
        print("📄 生成 PDF 報告...")
        pdf_file = generate_chairman_report_pdf(emp_db, case_db)
        print(f"✅ PDF 已儲存：{pdf_file}\n")
        
        # 3. 生成 HTML 報告
        print("🌐 生成 HTML 報告...")
        html_file = generate_chairman_report_html(emp_db, case_db)
        print(f"✅ HTML 已儲存：{html_file}\n")
        
        # 4. 生成 JSON 報告
        print("📋 生成 JSON 報告...")
        json_file = generate_chairman_report_json(emp_db, case_db)
        print(f"✅ JSON 已儲存：{json_file}\n")
        
        # 完成
        print("="*70)
        print("✅✅✅ 董事長專屬報告生成完成！")
        print("="*70)
        print(f"\n📁 輸出檔案:")
        print(f"   - {pdf_file}")
        print(f"   - {html_file}")
        print(f"   - {json_file}")
        
        print(f"\n🌐 立即查看:")
        print(f"   PDF: file://{pdf_file}")
        print(f"   HTML: file://{html_file}")
        
        print(f"\n結束時間：{datetime.now().isoformat()}")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ 錯誤：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
