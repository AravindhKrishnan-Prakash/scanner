@echo off
REM This script sets up Windows Task Scheduler to auto-start the scanner

echo ============================================================
echo Setting up Auto-Start for Trading Scanner
echo ============================================================
echo.

REM Get current directory
set SCRIPT_DIR=%~dp0

echo Current directory: %SCRIPT_DIR%
echo.
echo This will create a scheduled task that:
echo   - Runs Monday-Friday at 9:05 AM
echo   - Opens browser for token authorization
echo   - Starts the scanner automatically
echo.
echo NOTE: You still need to authorize the token in browser each morning
echo       (Upstox security requirement - cannot be fully automated)
echo.

pause

REM Create the scheduled task
schtasks /create /tn "TradingScanner" /tr "\"%SCRIPT_DIR%start_trading_day.py\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 09:05 /f

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo SUCCESS! Auto-start configured.
    echo ============================================================
    echo.
    echo The scanner will now start automatically at 9:05 AM
    echo on weekdays. You just need to:
    echo   1. Click "Authorize" in the browser window
    echo   2. Let it run all day
    echo   3. Check email for trade alerts
    echo.
    echo To disable: Run "schtasks /delete /tn TradingScanner"
    echo ============================================================
) else (
    echo.
    echo ERROR: Failed to create scheduled task.
    echo Please run this script as Administrator.
)

pause
