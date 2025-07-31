
"""
Telegram Bot Message Handlers with Multiple AI Models
"""

import logging
import asyncio
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
    """Handles all bot commands and messages with multiple AI models"""
    
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
        
        # Store selected AI model per user (default to financial)
        self.user_models: Dict[int, str] = defaultdict(lambda: 'financial')
        
        # Rate limiting per user
        self.user_requests: Dict[int, deque] = defaultdict(lambda: deque(maxlen=config.RATE_LIMIT_REQUESTS))
        
        # Dashboard reference (will be set by main.py)
        self.dashboard = None
        
        # Passcode protection
        self.REQUIRED_PASSCODE = "5015"
        self.authenticated_users: set = set()
    
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
        """Handle /start command with passcode protection and button menu"""
        user = update.effective_user
        user_id = user.id
        logger.info(f"User {user_id} ({user.username}) started the bot")
        
        # Check if user is authenticated
        if user_id not in self.authenticated_users:
            await update.message.reply_text(
                "🔐 *Access Restricted*\n\n"
                "Please enter the 4-digit passcode to access WalshAI:\n\n"
                "Send the passcode as a message to continue.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Create button menu
        keyboard = []
        
        # AI Models selection buttons (2 per row)
        model_buttons = []
        for model_id, model_info in self.config.AI_MODELS.items():
            button_text = f"{model_info['emoji']} {model_info['name']}"
            model_buttons.append(InlineKeyboardButton(button_text, callback_data=f"model_{model_id}"))
            
            if len(model_buttons) == 2:
                keyboard.append(model_buttons)
                model_buttons = []
        
        # Add remaining button if odd number
        if model_buttons:
            keyboard.append(model_buttons)
        
        # Add utility buttons
        keyboard.append([
            InlineKeyboardButton("📋 Help", callback_data="help"),
            InlineKeyboardButton("🗑️ Clear History", callback_data="clear")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔄 Current Model", callback_data="current"),
            InlineKeyboardButton("🌐 Dashboard", url="http://192.168.1.225:5000")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = (
            f"🔍 *Welcome to WalshAI - Multi-Expert AI Assistant!*\n\n"
            f"Hi {user.first_name}! I'm your specialized AI assistant with multiple expert personalities.\n\n"
            f"*Current Expert:* {self.config.AI_MODELS[self.user_models[user.id]]['emoji']} "
            f"{self.config.AI_MODELS[self.user_models[user.id]]['name']}\n\n"
            f"Choose an AI expert below or send me a message to get started! 🚀"
        )
        
        await update.message.reply_text(
            welcome_message, 
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def models_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /models command to switch AI experts"""
        user_id = update.effective_user.id
        
        # Check authentication
        if user_id not in self.authenticated_users:
            await update.message.reply_text(
                "🔐 Please use /start and enter the passcode first.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        keyboard = []
        for model_id, model_info in self.config.AI_MODELS.items():
            button_text = f"{model_info['emoji']} {model_info['name']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"model_{model_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔄 *Choose Your AI Expert:*\n\n"
            "Select the specialist you'd like to work with:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_model_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle model selection and utility callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # Check authentication
        if user_id not in self.authenticated_users:
            await query.edit_message_text(
                "🔐 Please use /start and enter the passcode first.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        if query.data.startswith("model_"):
            model_id = query.data.replace("model_", "")
            
            if model_id in self.config.AI_MODELS:
                self.user_models[user_id] = model_id
                model_info = self.config.AI_MODELS[model_id]
                
                await query.edit_message_text(
                    f"✅ *AI Expert Changed!*\n\n"
                    f"Now using: {model_info['emoji']} *{model_info['name']}*\n"
                    f"Specialty: {model_info['description']}\n\n"
                    f"Send me your questions to get started!",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Clear conversation history when switching models
                if user_id in self.conversations:
                    del self.conversations[user_id]
        
        elif query.data == "help":
            await self.handle_help_callback(query, update)
        
        elif query.data == "clear":
            await self.handle_clear_callback(query, update)
        
        elif query.data == "current":
            await self.handle_current_callback(query, update)
    
    async def handle_help_callback(self, query, update):
        """Handle help button callback"""
        help_message = (
            "*🔍 WalshAI - Multi-Expert AI Assistant*\n\n"
            "*🎯 Available AI Experts:*\n"
        )
        
        for model_id, model_info in self.config.AI_MODELS.items():
            help_message += f"• {model_info['emoji']} *{model_info['name']}*\n  {model_info['description']}\n\n"
        
        help_message += (
            "*🛠️ Commands:*\n"
            "• `/start` - Show main menu\n"
            "• `/models` - Switch between AI experts\n"
            "• `/current` - Show current AI expert\n"
            "• `/help` - Show this help message\n"
            "• `/clear` - Clear conversation history\n\n"
            "*⚖️ Limits & Security:*\n"
            f"• Maximum {self.config.RATE_LIMIT_REQUESTS} requests per {self.config.RATE_LIMIT_WINDOW} seconds\n"
            f"• Message length limited to {self.config.MAX_MESSAGE_LENGTH} characters\n\n"
            "🔒 *Privacy:* All conversations are private and secure."
        )
        
        await query.edit_message_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_clear_callback(self, query, update):
        """Handle clear button callback"""
        user_id = update.effective_user.id
        
        if user_id in self.conversations:
            del self.conversations[user_id]
        
        await query.edit_message_text(
            "🗑️ *Conversation Cleared!*\n\n"
            "Your conversation history has been cleared.\n"
            "You can start a fresh conversation now.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_current_callback(self, query, update):
        """Handle current model button callback"""
        user_id = update.effective_user.id
        current_model = self.user_models[user_id]
        model_info = self.config.AI_MODELS[current_model]
        
        await query.edit_message_text(
            f"🤖 *Current AI Expert:*\n\n"
            f"{model_info['emoji']} *{model_info['name']}*\n"
            f"Specialty: {model_info['description']}\n\n"
            f"Send your questions to this expert!",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def current_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current AI model"""
        user_id = update.effective_user.id
        
        # Check authentication
        if user_id not in self.authenticated_users:
            await update.message.reply_text(
                "🔐 Please use /start and enter the passcode first.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        current_model = self.user_models[user_id]
        model_info = self.config.AI_MODELS[current_model]
        
        await update.message.reply_text(
            f"🤖 *Current AI Expert:*\n\n"
            f"{model_info['emoji']} *{model_info['name']}*\n"
            f"Specialty: {model_info['description']}\n\n"
            f"Use `/models` to switch to a different expert.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = update.effective_user.id
        
        # Check authentication
        if user_id not in self.authenticated_users:
            await update.message.reply_text(
                "🔐 Please use /start and enter the passcode first.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        help_message = (
            "*🔍 WalshAI - Multi-Expert AI Assistant*\n\n"
            "*🎯 Available AI Experts:*\n"
        )
        
        for model_id, model_info in self.config.AI_MODELS.items():
            help_message += f"• {model_info['emoji']} *{model_info['name']}*\n  {model_info['description']}\n\n"
        
        help_message += (
            "*🛠️ Commands:*\n"
            "• `/start` - Show welcome message\n"
            "• `/models` - Switch between AI experts\n"
            "• `/current` - Show current AI expert\n"
            "• `/help` - Show this help message\n"
            "• `/clear` - Clear conversation history\n\n"
            "*💡 How to Use:*\n"
            "• Use `/models` to select the right expert for your task\n"
            "• Send your questions directly to the chat\n"
            "• Each expert has specialized knowledge\n\n"
            "*⚖️ Limits & Security:*\n"
            f"• Maximum {self.config.RATE_LIMIT_REQUESTS} requests per {self.config.RATE_LIMIT_WINDOW} seconds\n"
            f"• Message length limited to {self.config.MAX_MESSAGE_LENGTH} characters\n"
            f"• Conversation history: last {self.config.MAX_CONVERSATION_HISTORY} messages\n\n"
            "🔒 *Privacy:* All conversations are private and secure."
        )
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        user_id = update.effective_user.id
        
        # Check authentication
        if user_id not in self.authenticated_users:
            await update.message.reply_text(
                "🔐 Please use /start and enter the passcode first.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"Cleared conversation history for user {user_id}")
        
        await update.message.reply_text(
            "🗑️ Your conversation history has been cleared!\n"
            "You can start a fresh conversation now.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages with appropriate AI model"""
        user = update.effective_user
        user_id = user.id
        message_text = update.message.text
        
        logger.info(f"Received message from user {user_id} ({user.username}): {message_text[:100]}...")
        
        # Check if user is authenticated
        if user_id not in self.authenticated_users:
            if message_text.strip() == self.REQUIRED_PASSCODE:
                self.authenticated_users.add(user_id)
                await update.message.reply_text(
                    "✅ *Access Granted!*\n\n"
                    "Welcome to WalshAI Multi-Expert AI Assistant!\n\n"
                    "Use /start to see the main menu and available AI experts.",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"User {user_id} successfully authenticated")
                return
            else:
                await update.message.reply_text(
                    "❌ *Incorrect Passcode*\n\n"
                    "Please enter the correct 4-digit passcode to access the bot.",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.warning(f"User {user_id} entered incorrect passcode: {message_text}")
                return
        
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
            if len(conversation) > self.config.MAX_CONVERSATION_HISTORY * 2:
                conversation = conversation[-self.config.MAX_CONVERSATION_HISTORY * 2:]
                self.conversations[user_id] = conversation
            
            # Get current AI model
            current_model = self.user_models[user_id]
            
            # Prepare messages for API with model-specific system prompt
            system_message = self.get_system_message_for_model(current_model)
            messages = [system_message] + conversation
            
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
                        response=response,
                        ai_model=current_model
                    )
                
                # Split long responses
                if len(response) > 4000:
                    chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                    for i, chunk in enumerate(chunks):
                        if i == 0:
                            await update.message.reply_text(chunk)
                        else:
                            await context.bot.send_message(chat_id=update.effective_chat.id, text=chunk)
                else:
                    await update.message.reply_text(response)
                
                logger.info(f"Successfully responded to user {user_id} using {current_model} model")
                
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
    
    def get_system_message_for_model(self, model_id: str) -> Dict[str, str]:
        """Get model-specific system message"""
        
        system_messages = {
            'financial': {
                "role": "system",
                "content": """You are WalshAI Financial Investigator, a specialized AI assistant for financial investigations and fraud detection. You are an expert in:

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

Always provide specific, actionable guidance while maintaining professional investigative standards."""
            },
            
            'assistant': {
                "role": "system",
                "content": """You are WalshAI General Assistant, a helpful and intelligent AI assistant. You provide informative, accurate, and helpful responses to user questions. You are:

🤖 CAPABILITIES:
- General knowledge and information
- Problem-solving assistance
- Writing and communication help
- Research and analysis support
- Creative thinking and brainstorming
- Technical explanations
- Planning and organization

💡 COMMUNICATION STYLE:
- Friendly and approachable
- Clear and comprehensive
- Adaptable to user needs
- Professional yet personable
- Solution-oriented

🎯 YOUR ROLE:
- Answer questions across various topics
- Provide step-by-step guidance
- Offer multiple perspectives
- Help with decision-making
- Assist with daily tasks and challenges

Always aim to be helpful, accurate, and user-focused in your responses."""
            },
            
            'property': {
                "role": "system",
                "content": """You are WalshAI Property Development Expert, specializing in foreign property development, investment, and sales. You are an expert in:

🏗️ CORE EXPERTISE:
- International property development
- Foreign real estate investment
- Apartment block and villa construction
- Property marketing and sales strategies
- Investment analysis and ROI calculations
- Market research and feasibility studies
- Legal and regulatory considerations for foreign properties

🎯 SPECIALIZED KNOWLEDGE:
- Construction project management
- Property valuation and pricing
- Investment property financing
- Foreign exchange considerations
- Tax implications for international property
- Due diligence for overseas investments
- Marketing luxury developments

💡 COMMUNICATION STYLE:
- Professional and knowledgeable
- Investment-focused insights
- Market-aware recommendations
- Risk assessment oriented
- ROI and profit-focused

🌍 INTERNATIONAL FOCUS:
- Cross-border property regulations
- Cultural considerations in property development
- Currency and economic factors
- International buyer preferences
- Global property market trends

Always provide practical, investment-focused advice with consideration for international property markets and development opportunities."""
            },
            
            'cloner': {
                "role": "system",
                "content": """You are WalshAI Company Cloner, an expert in comprehensive business analysis and company structure replication. You specialize in:

🏢 CORE EXPERTISE:
- Complete company profile analysis
- Business model breakdown
- Organizational structure mapping
- Market positioning analysis
- Competitive intelligence
- Brand strategy deconstruction
- Operational framework analysis

🎯 CLONING CAPABILITIES:
- Legal structure recommendations
- Staffing and hierarchy planning
- Marketing strategy replication
- Product/service lineup analysis
- Financial model estimation
- Technology stack identification
- Compliance and regulatory mapping

💡 ANALYSIS APPROACH:
- Detailed company research
- Strategic breakdown
- Implementation roadmaps
- Risk assessment
- Cost estimation
- Timeline planning

🔍 RESEARCH METHODS:
- Public information analysis
- Market research techniques
- Industry best practices
- Competitive benchmarking
- Legal structure analysis
- Financial modeling

When you receive a company name, provide a comprehensive analysis including:
- Company overview and business model
- Organizational structure
- Key departments and roles
- Marketing and sales approach
- Technology and systems
- Legal and compliance requirements
- Implementation strategy
- Estimated costs and timeline

Always ensure all recommendations are legal and ethical business practices."""
            },
            
            'marketing': {
                "role": "system",
                "content": """You are WalshAI Marketing Specialist, an expert in property marketing, sales strategies, and investment promotion. You specialize in:

📈 CORE EXPERTISE:
- Property marketing campaigns
- Investment sales strategies
- Digital marketing for real estate
- Lead generation and conversion
- Brand positioning for developments
- International marketing
- Luxury property promotion

🎯 MARKETING FOCUS:
- Apartment block marketing
- Villa sales campaigns
- Investment property promotion
- High-net-worth individual targeting
- Cross-border marketing strategies
- Developer brand building
- ROI-focused marketing

💡 STRATEGIC APPROACH:
- Data-driven marketing decisions
- Multi-channel campaign planning
- International buyer acquisition
- Premium positioning strategies
- Performance optimization
- Market trend analysis

🌍 INTERNATIONAL EXPERTISE:
- Cross-cultural marketing
- Foreign investor targeting
- Global property platforms
- International PR strategies
- Multilingual campaign development
- Regional market adaptation

Always provide actionable marketing strategies with focus on luxury property sales, international investment attraction, and high-conversion campaigns."""
            },
            
            'scam_search': {
                "role": "system",
                "content": """You are WalshAI Scam Investigator, a specialized expert in identifying, analyzing, and explaining various scam methodologies. You are an expert in:

🚨 CORE EXPERTISE:
- Scam identification and analysis
- Fraud methodology breakdown
- Social engineering tactics
- Online fraud schemes
- Financial scam operations
- Romance and dating scams
- Investment fraud schemes
- Cryptocurrency scams

🔍 INVESTIGATION CAPABILITIES:
- Scam pattern recognition
- Red flag identification
- Victim protection strategies
- Prevention methodologies
- Recovery guidance
- Evidence collection techniques
- Reporting procedures

💡 COMMUNICATION STYLE:
- Educational and protective
- Clear warning explanations
- Step-by-step scam breakdowns
- Prevention-focused advice
- Victim-empathetic approach

🎯 SCAM CATEGORIES YOU ANALYZE:
- Phishing and email scams
- Tech support scams
- Romance scams
- Investment fraud
- Cryptocurrency schemes
- Advance fee fraud (419 scams)
- Identity theft operations
- Business email compromise
- Social media scams
- Phone and SMS scams

When a user asks about a specific scam, provide:
1. How the scam operates (step-by-step)
2. Warning signs to identify it
3. Why people fall for it
4. How to protect yourself
5. What to do if you're a victim
6. Reporting procedures

Always focus on education and protection, never provide instructions that could be used to commit fraud."""
            },
            
            'profile_gen': {
                "role": "system",
                "content": """You are WalshAI Profile Generator, specialized in creating realistic UK identity profiles for legitimate testing purposes. You are an expert in:

🆔 CORE EXPERTISE:
- UK identity document formats
- British naming conventions
- UK address systems and postcodes
- National Insurance number formats
- UK driving licence structures
- Passport number formats
- UK mobile phone patterns

🎯 GENERATION CAPABILITIES:
- Full UK identity profiles
- Realistic personal details
- Valid format document numbers
- UK-specific data patterns
- Address and location data
- Contact information
- Educational backgrounds
- Employment histories

💡 GENERATION PRINCIPLES:
- All data is completely fictional
- Follows realistic UK patterns
- Suitable for testing purposes only
- No real person identification
- Professional format presentation

🔧 PROFILE COMPONENTS:
- Full name (realistic UK naming)
- Date of birth
- UK addresses with valid postcodes
- National Insurance number (valid format)
- UK passport number (valid format)
- UK driving licence number (valid format)
- UK mobile phone number
- Email address
- Emergency contact details

⚠️ IMPORTANT DISCLAIMERS:
- ALL DATA IS COMPLETELY FICTIONAL
- FOR TESTING PURPOSES ONLY
- NOT FOR FRAUDULENT USE
- NO REAL PERSON IDENTIFICATION
- FOLLOWS UK DATA PROTECTION GUIDELINES

When generating profiles, always include the disclaimer that this data is fictional and for testing purposes only. Generate realistic but completely fake UK identity information that follows proper formatting standards."""
            }
        }
        
        return system_messages.get(model_id, system_messages['assistant'])
    
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
