"""
Telegram Bot Message Handlers
"""

import logging
import asyncio
from typing import Dict, List
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from deepseek_client import DeepSeekClient
from config import Config
import time
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class BotHandlers:
    """Handles all bot commands and messages"""
    
    def __init__(self, config: Config):
        self.config = config
        self.deepseek_client = DeepSeekClient(
            api_key=config.DEEPSEEK_API_KEY,
            api_url=config.DEEPSEEK_API_URL,
            model=config.DEEPSEEK_MODEL,
            timeout=config.REQUEST_TIMEOUT,
            max_retries=config.MAX_RETRIES
        )
        
        # Store conversation history per user
        self.conversations: Dict[int, List[Dict[str, str]]] = defaultdict(list)
        
        # Rate limiting per user
        self.user_requests: Dict[int, deque] = defaultdict(lambda: deque(maxlen=config.RATE_LIMIT_REQUESTS))
    
    def is_rate_limited(self, user_id: int) -> bool:
        """Check if user is rate limited"""
        now = time.time()
        user_queue = self.user_requests[user_id]
        
        # Remove old requests outside the window
        while user_queue and now - user_queue[0] > self.config.RATE_LIMIT_WINDOW:
            user_queue.popleft()
        
        # Check if limit exceeded
        if len(user_queue) >= self.config.RATE_LIMIT_REQUESTS:
            return True
        
        # Add current request
        user_queue.append(now)
        return False
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        welcome_message = (
            f"🤖 *Welcome to WalshAI!*\n\n"
            f"Hi {user.first_name}! I'm your personal AI assistant powered by advanced language models.\n\n"
            f"*Available Commands:*\n"
            f"• `/start` - Show this welcome message\n"
            f"• `/help` - Get help and usage information\n"
            f"• `/clear` - Clear conversation history\n\n"
            f"*How to use:*\n"
            f"Just send me any message and I'll respond using AI! "
            f"I can help with questions, creative writing, analysis, and much more.\n\n"
            f"Let's start chatting! 💬"
        )
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "*🤖 WalshAI Help*\n\n"
            "*Available Commands:*\n"
            "• `/start` - Show welcome message\n"
            "• `/help` - Show this help message\n"
            "• `/clear` - Clear your conversation history\n\n"
            "*How it works:*\n"
            "• Send any text message and I'll respond using advanced AI\n"
            "• I remember our conversation context for better responses\n"
            "• Each user has their own private conversation history\n\n"
            "*Features:*\n"
            "• Natural language conversations\n"
            "• Context-aware responses\n"
            "• Rate limiting for fair usage\n"
            "• Error handling and retry logic\n\n"
            "*Limits:*\n"
            f"• Maximum {self.config.RATE_LIMIT_REQUESTS} requests per {self.config.RATE_LIMIT_WINDOW} seconds\n"
            f"• Message length limited to {self.config.MAX_MESSAGE_LENGTH} characters\n"
            f"• Conversation history limited to last {self.config.MAX_CONVERSATION_HISTORY} messages\n\n"
            "If you encounter any issues, try again in a few moments. "
            "For persistent problems, use `/clear` to reset your conversation."
        )
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        user_id = update.effective_user.id
        
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"Cleared conversation history for user {user_id}")
        
        await update.message.reply_text(
            "🗑️ Your conversation history has been cleared!\n"
            "You can start a fresh conversation now.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user = update.effective_user
        user_id = user.id
        message_text = update.message.text
        
        logger.info(f"Received message from user {user_id} ({user.username}): {message_text[:100]}...")
        
        # Check rate limiting
        if self.is_rate_limited(user_id):
            await update.message.reply_text(
                "⏰ You're sending messages too quickly! "
                f"Please wait a moment before sending another message.\n"
                f"Limit: {self.config.RATE_LIMIT_REQUESTS} messages per {self.config.RATE_LIMIT_WINDOW} seconds.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check message length
        if len(message_text) > self.config.MAX_MESSAGE_LENGTH:
            await update.message.reply_text(
                f"📝 Your message is too long! "
                f"Please keep it under {self.config.MAX_MESSAGE_LENGTH} characters.\n"
                f"Current length: {len(message_text)} characters",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Get conversation history
            conversation = self.conversations[user_id]
            
            # Add user message to conversation
            conversation.append({"role": "user", "content": message_text})
            
            # Limit conversation history
            if len(conversation) > self.config.MAX_CONVERSATION_HISTORY * 2:  # *2 because each exchange has user+assistant
                conversation = conversation[-self.config.MAX_CONVERSATION_HISTORY * 2:]
                self.conversations[user_id] = conversation
            
            # Prepare messages for API
            messages = [self.deepseek_client.get_system_message()] + conversation
            
            # Get AI response
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.deepseek_client.create_chat_completion,
                messages
            )
            
            if response:
                # Add assistant response to conversation
                conversation.append({"role": "assistant", "content": response})
                
                # Split long responses
                if len(response) > 4000:
                    # Split into chunks
                    chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                    for i, chunk in enumerate(chunks):
                        if i == 0:
                            await update.message.reply_text(chunk)
                        else:
                            await context.bot.send_message(chat_id=update.effective_chat.id, text=chunk)
                else:
                    await update.message.reply_text(response)
                
                logger.info(f"Successfully responded to user {user_id}")
                
            else:
                await update.message.reply_text(
                    "🚫 I can't generate a response right now. This is likely because:\n\n"
                    "💳 **AI service needs credits** - Check your account balance\n"
                    "⚡ High server load\n"
                    "🌐 Network issues\n\n"
                    "**To fix**: Add credits to your AI service account, then try again.\n"
                    "If you recently added credits, wait a few minutes for them to activate.\n\n"
                    "Use /clear to reset our conversation if needed.",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.warning(f"Failed to get response from DeepSeek API for user {user_id}")
        
        except Exception as e:
            logger.error(f"Error handling message from user {user_id}: {e}")
            await update.message.reply_text(
                "❌ An unexpected error occurred while processing your message. "
                "Please try again later or use /clear to reset the conversation.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the bot"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Try to send error message to user if possible
        if isinstance(update, Update) and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="🔧 A technical error occurred. Please try again later.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to send error message to user: {e}")
