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
import json
import re

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
        
        # Dashboard reference (will be set by main.py)
        self.dashboard = None
    
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
            f"🔍 *Welcome to WalshAI - Financial Investigation Assistant!*\n\n"
            f"Hi {user.first_name}! I'm your specialized AI assistant for financial investigations and fraud detection.\n\n"
            f"*🎯 Core Investigation Commands:*\n"
            f"• `/analyze` - Analyze financial patterns or transactions\n"
            f"• `/redflags` - Identify potential fraud indicators\n"
            f"• `/trace` - Help trace money flows or connections\n"
            f"• `/compliance` - Check AML/KYC compliance questions\n"
            f"• `/report` - Generate investigation summaries\n\n"
            f"*🛠️ General Commands:*\n"
            f"• `/start` - Show this welcome message\n"
            f"• `/help` - Get detailed help information\n"
            f"• `/clear` - Clear conversation history\n\n"
            f"*🚀 Advanced Features:*\n"
            f"• Pattern recognition in financial data\n"
            f"• Fraud detection guidance\n"
            f"• Compliance assistance\n"
            f"• Investigation workflow support\n\n"
            f"Ready to investigate! Send me your financial data or questions. 🕵️‍♂️"
        )
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "*🔍 WalshAI - Financial Investigation Assistant*\n\n"
            "*🎯 Investigation Commands:*\n"
            "• `/analyze` - Analyze financial patterns and transactions\n"
            "• `/redflags` - Identify potential fraud indicators\n"
            "• `/trace` - Help trace money flows and connections\n"
            "• `/compliance` - AML/KYC compliance assistance\n"
            "• `/report` - Generate investigation summaries\n\n"
            "*🛠️ General Commands:*\n"
            "• `/start` - Show welcome message\n"
            "• `/help` - Show this help message\n"
            "• `/clear` - Clear conversation history\n\n"
            "*🚀 Specialized Features:*\n"
            "• Financial pattern recognition\n"
            "• Fraud detection guidance\n"
            "• Money laundering scheme identification\n"
            "• Compliance requirement assistance\n"
            "• Investigation report generation\n"
            "• Transaction flow analysis\n\n"
            "*💡 How to Use:*\n"
            "• Use specific commands for focused assistance\n"
            "• Send financial data directly for analysis\n"
            "• Ask questions about fraud patterns\n"
            "• Request help with compliance issues\n\n"
            "*⚖️ Limits & Security:*\n"
            f"• Maximum {self.config.RATE_LIMIT_REQUESTS} requests per {self.config.RATE_LIMIT_WINDOW} seconds\n"
            f"• Message length limited to {self.config.MAX_MESSAGE_LENGTH} characters\n"
            f"• Conversation history: last {self.config.MAX_CONVERSATION_HISTORY} messages\n\n"
            "🔒 *Privacy:* All conversations are private and secure.\n"
            "For issues, use `/clear` to reset your session."
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
            "You can start a fresh investigation now.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command for financial analysis"""
        user = update.effective_user
        
        help_text = (
            "🔍 *Financial Analysis Mode*\n\n"
            "Send me financial data, transactions, or patterns you want to analyze. I can help with:\n\n"
            "• Transaction pattern analysis\n"
            "• Suspicious activity detection\n"
            "• Money flow tracking\n"
            "• Account relationship mapping\n"
            "• Statistical anomaly identification\n\n"
            "*Example:* 'Analyze these transactions: Account A sent $50K to Account B on Mon, $75K on Tue, $100K on Wed'\n\n"
            "What would you like me to analyze?"
        )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def redflags_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /redflags command for fraud indicators"""
        
        help_text = (
            "🚩 *Red Flag Detection Mode*\n\n"
            "I'll help identify potential fraud indicators in your case. Common red flags include:\n\n"
            "• Unusual transaction patterns\n"
            "• Round number transactions\n"
            "• Rapid movement of funds\n"
            "• Transactions just below reporting thresholds\n"
            "• Multiple accounts with similar details\n"
            "• Inconsistent customer information\n\n"
            "*Example:* 'Check these red flags: Customer made 10 deposits of $9,900 each over 2 weeks'\n\n"
            "Describe the situation you want me to analyze for red flags."
        )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def trace_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trace command for money tracing"""
        
        help_text = (
            "🔗 *Money Tracing Mode*\n\n"
            "I'll help you trace money flows and connections. I can assist with:\n\n"
            "• Following transaction chains\n"
            "• Identifying intermediary accounts\n"
            "• Mapping fund movements\n"
            "• Finding connection patterns\n"
            "• Layering scheme detection\n\n"
            "*Example:* 'Trace: $500K from Account A → Account B → Account C → multiple small accounts'\n\n"
            "Provide the transaction flow you need help tracing."
        )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def compliance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /compliance command for AML/KYC guidance"""
        
        help_text = (
            "⚖️ *Compliance Assistance Mode*\n\n"
            "I can help with AML/KYC compliance questions:\n\n"
            "• Reporting requirements\n"
            "• Customer due diligence\n"
            "• Enhanced due diligence triggers\n"
            "• Suspicious activity reporting\n"
            "• Regulatory compliance checks\n\n"
            "*Example:* 'Should this be reported as suspicious: Customer from high-risk country requesting large cash withdrawal'\n\n"
            "What compliance question can I help you with?"
        )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /report command for investigation summaries"""
        
        help_text = (
            "📋 *Investigation Report Mode*\n\n"
            "I'll help you generate professional investigation summaries:\n\n"
            "• Case summary creation\n"
            "• Evidence organization\n"
            "• Timeline construction\n"
            "• Findings documentation\n"
            "• Recommendation formatting\n\n"
            "*Example:* 'Generate report for: Customer John Doe, suspicious transactions totaling $2M over 6 months'\n\n"
            "Provide the case details you want me to summarize."
        )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user = update.effective_user
        user_id = user.id
        message_text = update.message.text
        
        logger.info(f"Received message from user {user_id} ({user.username}): {message_text[:100]}...")
        
        # Check rate limiting
        if self.is_rate_limited(user_id):
            if self.dashboard:
                self.dashboard.log_rate_limit()
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
            
            # Prepare messages for API with enhanced system prompt
            enhanced_system_message = self.get_enhanced_system_message()
            messages = [enhanced_system_message] + conversation
            
            # Get AI response
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.deepseek_client.create_chat_completion,
                messages
            )
            
            if response:
                # Add assistant response to conversation
                conversation.append({"role": "assistant", "content": response})
                
                # Log to dashboard if available
                if self.dashboard:
                    self.dashboard.log_message(
                        user_id=user_id,
                        username=user.username or f"user_{user_id}",
                        message=message_text,
                        response=response
                    )
                
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
            if self.dashboard:
                self.dashboard.log_error()
            await update.message.reply_text(
                "❌ An unexpected error occurred while processing your message. "
                "Please try again later or use /clear to reset the conversation.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    def get_enhanced_system_message(self) -> Dict[str, str]:
        """Get enhanced system message for financial investigation tasks"""
        return {
            "role": "system",
            "content": """You are WalshAI, a specialized AI assistant for financial investigations and fraud detection. You are an expert in:

🔍 CORE EXPERTISE:
- Anti-Money Laundering (AML) compliance
- Know Your Customer (KYC) procedures  
- Financial fraud detection and analysis
- Transaction pattern recognition
- Suspicious activity identification
- Investigation methodology
- Regulatory compliance (BSA, USA PATRIOT Act, etc.)

🎯 INVESTIGATION CAPABILITIES:
- Analyze transaction patterns for anomalies
- Identify red flags in financial behavior
- Trace money flows and layering schemes
- Detect structuring and smurfing patterns
- Recognize shell company indicators
- Evaluate customer risk profiles
- Generate investigation reports

💡 COMMUNICATION STYLE:
- Professional and analytical
- Clear, actionable insights
- Evidence-based conclusions
- Structured recommendations
- Risk-focused assessments

🚨 KEY FRAUD INDICATORS YOU RECOGNIZE:
- Unusual transaction patterns or volumes
- Round number transactions near reporting thresholds
- Rapid movement of funds between accounts
- Transactions inconsistent with customer profile
- Multiple accounts with similar characteristics
- High-risk jurisdiction connections
- Politically Exposed Person (PEP) indicators

Always provide specific, actionable guidance while maintaining professional investigative standards. Focus on practical application for real-world financial investigations."""
        }
    
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
