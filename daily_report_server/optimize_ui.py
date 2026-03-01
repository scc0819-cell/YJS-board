#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX 深度優化腳本
1. 字體大小調整（14px → 16px）
2. 顏色對比增強
3. 導航欄優化
4. 卡片和按鈕樣式升級
"""

from pathlib import Path

DAILY_DIR = Path('/home/yjsclaw/.openclaw/workspace/daily_report_server')

def optimize_base_html():
    """優化 base.html 的 CSS 樣式"""
    base_path = DAILY_DIR / 'templates' / 'base.html'
    
    if not base_path.exists():
        print("❌ base.html 不存在")
        return
    
    content = base_path.read_text(encoding='utf-8')
    
    # 優化 body 樣式
    old_body = 'body{font-family:-apple-system,BlinkMacSystemFont,"Microsoft JhengHei",sans-serif;background:#f3f4f6;color:#111827}'
    new_body = '''body{font-family:-apple-system,BlinkMacSystemFont,"Microsoft JhengHei",sans-serif;font-size:16px;line-height:1.6;background:linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%);min-height:100vh;color:#1a1a2e}'''
    
    content = content.replace(old_body, new_body)
    
    # 優化頂部導航
    old_top = '.top{background:#111827;color:#fff;padding:14px 20px;'
    new_top = '.top{background:linear-gradient(135deg,#1e3a5f 0%,#0f3460 100%);color:#ffffff;padding:16px 20px;font-size:15px;'
    
    content = content.replace(old_top, new_top)
    
    # 優化卡片
    old_card = '.card{background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:20px}'
    new_card = '.card{background:#ffffff;border-radius:16px;padding:28px;box-shadow:0 4px 16px rgba(0,0,0,0.12);border:1px solid #e0e0e0;margin-bottom:24px}'
    
    content = content.replace(old_card, new_card)
    
    # 優化按鈕
    old_btn = '.btn{padding:8px 14px;'
    new_btn = '.btn{background:linear-gradient(135deg,#0ea5e9 0%,#1e3a5f 100%);color:#ffffff;padding:12px 24px;border-radius:8px;font-size:15px;font-weight:600;border:none;cursor:pointer;transition:all 0.3s}'
    
    content = content.replace(old_btn, new_btn)
    
    # 優化標題
    old_h1 = 'h1{'
    new_h1 = 'h1{color:#1e3a5f;font-size:32px;font-weight:700;margin-bottom:24px}'
    
    if 'h1{color:#1e3a5f' not in content:
        content = content.replace('h1{', new_h1)
    
    # 優化表格
    old_table = 'table{width:100%;border-collapse:collapse}'
    new_table = 'table{width:100%;border-collapse:collapse;font-size:15px}'
    
    content = content.replace(old_table, new_table)
    
    # 優化表格標題
    old_th = 'th{background:#f9fafb;text-align:left;padding:12px 16px;border-bottom:2px solid #e5e7eb;color:#374151}'
    new_th = 'th{background:linear-gradient(135deg,#f0f9ff 0%,#e0f2fe 100%);text-align:left;padding:14px 16px;border-bottom:2px solid #0ea5e9;color:#1e3a5f;font-weight:600;font-size:15px}'
    
    content = content.replace(old_th, new_th)
    
    # 優化表格儲存格
    old_td = 'td{padding:12px 16px;border-bottom:1px solid #e5e7eb;color:#1f2937}'
    new_td = 'td{padding:14px 16px;border-bottom:1px solid #e0e0e0;color:#1a1a2e;font-size:15px}'
    
    content = content.replace(old_td, new_td)
    
    # 寫回檔案
    base_path.write_text(content, encoding='utf-8')
    print("✅ base.html UI 已優化")

if __name__ == "__main__":
    optimize_base_html()
    print("\n🎨 UI 優化完成！請重新整理瀏覽器查看效果。")
