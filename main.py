#!/usr/bin/env python3
"""
Telegram Bot with DeepSeek AI Integration
Main application entry point
"""

import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config
from bot_handlers import BotHandlers

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
        
        # Create application
        application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Initialize bot handlers
        bot_handlers = BotHandlers(config)
        
        # Register handlers
        application.add_handler(CommandHandler("start", bot_handlers.start_command))
        application.add_handler(CommandHandler("help", bot_handlers.help_command))
        application.add_handler(CommandHandler("clear", bot_handlers.clear_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.handle_message))
        
        # Add error handler
        application.add_error_handler(bot_handlers.error_handler)
        
        logger.info("Starting WalshAI Telegram bot...")
        
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
