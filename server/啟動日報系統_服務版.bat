@echo off
REM 昱金生能源集團 - 員工日報系統 啟動腳本 (Windows 版本)
REM 可放入 Windows 排程任務，開機自動執行

echo ============================================
echo   昱金生能源集團 - 員工日報系統
echo   啟動中...
echo ============================================

cd /d C:\Users\YJSClaw\Documents\Openclaw\daily_report_server

REM 檢查是否已在運行
tasklist /FI "WINDOWTITLE eq python3*" 2>nul | find "python3" >nul
if %errorlevel% equ 0 (
    echo 服務已在運行中
    pause
    exit /b
)

REM 啟動服務
start /min python3 app.py

echo 服務已啟動！
echo 訪問網址：http://localhost:5000
echo ============================================
timeout /t 3
exit
