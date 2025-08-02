#!/usr/bin/env python3
"""
Telegram Bot with DeepSeek AI Integration and Web Dashboard
Main application entry point
"""

import logging
import os
import threading
import time
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import Config
from bot_handlers import BotHandlers
from web_dashboard import BotDashboard

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot"""
    try:
        # Load configuration
        config = Config()

        # Validate required environment variables
        if not config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not config.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY is required")

        # Create application with optimized settings for faster responses
        application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).read_timeout(8).write_timeout(8).build()

        # Initialize bot handlers
        bot_handlers = BotHandlers(config)

        # Test DeepSeek connection at startup
        logger.info("Testing DeepSeek API connection...")
        if bot_handlers.deepseek_client.test_connection():
            logger.info("✅ DeepSeek API connection successful")
        else:
            logger.warning("⚠️ DeepSeek API connection failed - check your API key and credits")

        # Initialize web dashboard
        dashboard = BotDashboard(bot_handlers)
        bot_handlers.dashboard = dashboard  # Link dashboard to handlers

        # Start web dashboard in a separate thread
        dashboard_thread = threading.Thread(
            target=lambda: dashboard.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False),
            daemon=True
        )
        dashboard_thread.start()
        logger.info("Web Dashboard started on http://0.0.0.0:5000")

        # Register handlers
        application.add_handler(CommandHandler("start", bot_handlers.start_command))
        application.add_handler(CommandHandler("help", bot_handlers.help_command))
        application.add_handler(CommandHandler("clear", bot_handlers.clear_command))
        application.add_handler(CommandHandler("models", bot_handlers.models_command))
        application.add_handler(CommandHandler("current", bot_handlers.current_command))

        # Callback query handler for model selection
        application.add_handler(CallbackQueryHandler(bot_handlers.handle_model_selection))

        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.handle_message))

        # Add error handler
        application.add_error_handler(bot_handlers.error_handler)

        logger.info("Starting WalshAI Multi-Expert AI Bot...")
        logger.info("Dashboard available at: http://localhost:5000")

        # Give dashboard a moment to start
        time.sleep(2)

        # Start the bot
        application.run_polling(
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True
        )

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()