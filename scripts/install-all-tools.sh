#!/bin/bash

# OpenClaw 完整自動化工具安裝腳本
# 執行此腳本需要 sudo 權限

set -e

echo "🦞 OpenClaw 完整自動化工具安裝程式"
echo "======================================"
echo
echo "此腳本將安裝以下工具："
echo
echo "📄 文件處理："
echo "   - pandoc (萬能文件轉換器)"
echo "   - wkhtmltopdf (HTML 轉 PDF)"
echo "   - sqlite3 (資料庫)"
echo "   - jq (JSON 處理)"
echo
echo "📊 Python 模組："
echo "   - markdown, pdfkit, reportlab (PDF 生成)"
echo "   - openpyxl (Excel 處理)"
echo "   - python-pptx (PowerPoint 處理)"
echo "   - imap-tools (郵件處理)"
echo "   - google-api-python-client (日曆整合)"
echo "   - playwright (瀏覽器自動化)"
echo "   - langchain, chromadb (AI 進階)"
echo "   - pytesseract (OCR)"
echo "   - pyttsx3, SpeechRecognition (語音)"
echo
echo "======================================"
echo

# 檢查是否為 root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  需要 sudo 權限"
    echo "請執行：sudo ~/.openclaw/workspace/scripts/install-all-tools.sh"
    exit 1
fi

echo "✅ 開始安裝..."
echo

# 系統更新
echo "📦 更新系統套件列表..."
apt update -qq

# 安裝系統工具
echo
echo "📄 安裝文件處理工具..."
apt install -y -qq pandoc wkhtmltopdf sqlite3 jq htop mailutils tesseract-ocr tesseract-ocr-chi-tra rclone 2>/dev/null || {
    echo "⚠️  部分系統套件安裝失敗，繼續進行..."
}

# 安裝 Python 模組
echo
echo "🐍 安裝 Python 模組..."

# 檢查 pip3
if ! command -v pip3 &> /dev/null; then
    echo "安裝 pip3..."
    apt install -y -qq python3-pip
fi

# 安裝文件處理模組
echo "   - 文件處理模組..."
pip3 install --quiet markdown pdfkit reportlab openpyxl python-pptx

# 安裝郵件與日曆模組
echo "   - 郵件與日曆模組..."
pip3 install --quiet imap-tools google-auth google-auth-oauthlib google-api-python-client

# 安裝網頁自動化
echo "   - 瀏覽器自動化工具..."
pip3 install --quiet playwright
playwright install chromium 2>/dev/null || echo "⚠️  Playwright Chromium 安裝失敗"

# 安裝 AI 進階模組
echo "   - AI 進階模組..."
pip3 install --quiet langchain langchain-community chromadb

# 安裝 OCR 模組
echo "   - OCR 模組..."
pip3 install --quiet pytesseract pillow

# 安裝語音模組
echo "   - 語音模組..."
pip3 install --quiet pyttsx3 SpeechRecognition

echo
echo "======================================"
echo "✅ 安裝完成！"
echo "======================================"
echo
echo "已安裝工具："
echo "📄 文件處理：pandoc, wkhtmltopdf, sqlite3, jq"
echo "📊 Python: markdown, pdfkit, reportlab, openpyxl, python-pptx"
echo "📧 郵件：imap-tools"
echo "📅 日曆：google-api-python-client"
echo "🌐 瀏覽器：playwright + chromium"
echo "🤖 AI: langchain, chromadb"
echo "📷 OCR: tesseract, pytesseract"
echo "🎤 語音：pyttsx3, SpeechRecognition"
echo "☁️  雲端：rclone"
echo
echo "🎯 下一步："
echo "1. 測試 PDF 生成：python3 ~/.openclaw/workspace/scripts/test-pdf-gen.py"
echo "2. 查看已安裝工具：~/.openclaw/workspace/scripts/check-installed-tools.sh"
echo
echo "🦞 祝你使用愉快！"
