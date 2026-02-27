#!/bin/bash

# OpenClaw 工具檢查腳本

echo "🦞 OpenClaw 已安裝工具檢查"
echo "=========================="
echo

# 檢查系統工具
echo "📦 系統工具："
tools=("pandoc" "wkhtmltopdf" "sqlite3" "jq" "htop" "tesseract" "rclone")
for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        version=$($tool --version 2>&1 | head -1)
        echo "   ✅ $tool: $version"
    else
        echo "   ❌ $tool: 未安裝"
    fi
done

echo
echo "🐍 Python 模組："
modules=("markdown" "pdfkit" "reportlab" "openpyxl" "pptx" "imaplib" "google" "playwright" "langchain" "chromadb" "pytesseract" "pyttsx3" "speech_recognition")
for module in "${modules[@]}"; do
    if python3 -c "import $module" 2>/dev/null; then
        echo "   ✅ $module"
    else
        echo "   ❌ $module: 未安裝"
    fi
done

echo
echo "🌐 Playwright 瀏覽器："
if python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo "   ✅ Playwright 已安裝"
    if [ -f ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome ]; then
        echo "   ✅ Chromium 瀏覽器已安裝"
    else
        echo "   ⚠️  Chromium 瀏覽器未安裝，執行：playwright install chromium"
    fi
else
    echo "   ❌ Playwright: 未安裝"
fi

echo
echo "📊 總結："
installed=0
total=$((${#tools[@]} + ${#modules[@]} + 2))

for tool in "${tools[@]}"; do
    command -v $tool &> /dev/null && ((installed++))
done

for module in "${modules[@]}"; do
    python3 -c "import $module" 2>/dev/null && ((installed++))
done

command -v playwright &> /dev/null && ((installed++))
[ -f ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome ] && ((installed++))

echo "   已安裝：$installed / $total"
echo "   完成度：$((installed * 100 / total))%"
echo
echo "=========================="
