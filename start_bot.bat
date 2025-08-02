
@echo off
title WalshAI Telegram Bot - Optimized
echo ========================================
echo    WalshAI Telegram Bot - Starting...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import telegram" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install python-telegram-bot requests python-dotenv flask
)

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and add your API keys
    echo.
    echo Required in .env file:
    echo TELEGRAM_BOT_TOKEN=your_bot_token_here
    echo DEEPSEEK_API_KEY=your_deepseek_key_here
    pause
    exit /b 1
)

echo Starting optimized bot...
echo Web Dashboard: http://localhost:5000
echo Press Ctrl+C to stop the bot
echo.

python main.py

if errorlevel 1 (
    echo.
    echo Bot stopped with error. Check the logs above.
    pause
)
