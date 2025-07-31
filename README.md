# DeepSeek AI Telegram Bot

A fully portable Telegram chatbot powered by DeepSeek's cost-effective AI API. Works seamlessly on Windows, macOS, and Linux.

## Features

- 🤖 AI-powered conversations using DeepSeek's language model
- 💰 Cost-effective pricing through DeepSeek API
- 💬 Context-aware responses with conversation history
- 🚦 Built-in rate limiting and spam protection
- 📝 Support for long messages and responses
- 🔒 Secure API key management
- 📊 Comprehensive logging and error handling
- 🖥️ **Fully portable** - easy to run on any Windows PC

## Windows PC Setup Guide

### Step 1: Install Python

1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation by opening Command Prompt and typing: `python --version`

### Step 2: Download the Bot

1. Download all project files to a folder on your PC (e.g., `C:\telegram-bot\`)
2. Open Command Prompt in that folder:
   - Hold Shift + Right-click in the folder → "Open PowerShell window here"
   - Or navigate: `cd C:\telegram-bot\`

### Step 3: Install Dependencies

Run this command in your Command Prompt:
```cmd
pip install python-telegram-bot requests python-dotenv
```

### Step 4: Get Your API Keys

#### Telegram Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Choose a name (e.g., "My AI Bot") and username (e.g., "my_ai_bot")
4. Copy the token (looks like: `123456789:ABCdef123456789-xyz`)

#### DeepSeek API Key
1. Visit [DeepSeek Platform](https://platform.deepseek.com)
2. Sign up and verify your account
3. Go to "API Keys" section
4. Create a new API key and copy it
5. **Important**: Add credits to your DeepSeek account for the bot to work

### Step 5: Configure the Bot

1. Copy `.env.example` and rename it to `.env`
2. Open `.env` in Notepad
3. Replace the placeholders with your real keys:
```
TELEGRAM_BOT_TOKEN=your_real_telegram_token_here
DEEPSEEK_API_KEY=your_real_deepseek_key_here
```

### Step 6: Run the Bot

In Command Prompt, run:
```cmd
python main.py
```

You should see:
```
Starting Telegram bot...
Application started
```

## Using Your Bot

1. Find your bot on Telegram (search for the username you created)
2. Send `/start` to begin
3. Send any message to chat with the AI
4. Use `/help` for available commands
5. Use `/clear` to reset conversation history

## Available Commands

- `/start` - Welcome message and bot introduction
- `/help` - Show all available commands
- `/clear` - Clear your conversation history with the bot

## Troubleshooting

### "Python is not recognized"
- Reinstall Python and check "Add Python to PATH"
- Try `python3` instead of `python`
- Restart Command Prompt after installation

### "Bot not responding"
- Check your API keys in the `.env` file
- Ensure the bot is running (you should see "Application started")
- Verify your Telegram bot token with @BotFather

### "Insufficient Balance" error
- Add credits to your DeepSeek account
- Check your API usage limits
- Verify your DeepSeek API key is correct

### Permission errors
- Run Command Prompt as Administrator
- Or use: `pip install --user python-telegram-bot requests python-dotenv`

## Moving to Another PC

This bot is designed to be fully portable:

1. Copy the entire project folder to the new PC
2. Install Python on the new PC (with PATH option checked)
3. Install dependencies: `pip install python-telegram-bot requests python-dotenv`
4. Run: `python main.py`

No database or complex setup required!

## Configuration Options

You can customize the bot by editing `.env`:

```
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
DEEPSEEK_API_KEY=your_api_key

# Optional (with defaults)
MAX_MESSAGE_LENGTH=4000
MAX_CONVERSATION_HISTORY=10
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_WINDOW=60
LOG_LEVEL=INFO
```

## Project Structure

- `main.py` - Bot startup and orchestration
- `config.py` - Configuration and environment management
- `bot_handlers.py` - Telegram command and message handlers
- `deepseek_client.py` - DeepSeek API client with retry logic
- `.env.example` - Template for environment variables
- `README.md` - This guide

## Security Notes

- Keep your `.env` file secure and never share it
- Both API keys are sensitive - treat them like passwords
- The bot stores conversation history in memory only (not permanently saved)

## Cost Information

- DeepSeek API is very cost-effective compared to other AI providers
- Typical usage: $0.001 per 1K tokens (extremely affordable)
- Monitor your usage on the DeepSeek Platform dashboard

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all API keys are correct
3. Ensure you have credits in your DeepSeek account
4. Check the console output for error messages

## License

MIT License - Free to use and modify