@echo off
echo DeepSeek AI Telegram Bot
echo =========================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org and check "Add Python to PATH"
    pause
    exit /b 1
)

:: Check if .env file exists
if not exist ".env" (
    echo Error: .env file not found!
    echo Please copy .env.example to .env and add your API keys
    pause
    exit /b 1
)

:: Install dependencies if needed
echo Installing dependencies...
pip install python-telegram-bot requests python-dotenv

echo.
echo Starting Telegram Bot...
echo Press Ctrl+C to stop the bot
echo.

:: Run the bot
python main.py

pause