
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
        
        # Send typing indicator (but don't wait for it)
        asyncio.create_task(
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        )
        
        try:
            # Get conversation history
            conversation = self.conversations[user_id]
            
            # Add user message to conversation
            conversation.append({"role": "user", "content": message_text})
            
            # Limit conversation history more aggressively for speed
            max_history = min(self.config.MAX_CONVERSATION_HISTORY, 6) * 2  # Reduce for faster API calls
            if len(conversation) > max_history:
                conversation = conversation[-max_history:]
                self.conversations[user_id] = conversation
            
            # Get current AI model
            current_model = self.user_models[user_id]
            
            # Prepare messages for API with model-specific system prompt
            system_message = self.get_system_message_for_model(current_model)
            messages = [system_message] + conversation
            
            # Get AI response with timeout
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, 
                    self.deepseek_client.create_chat_completion,
                    messages
                ),
                timeout=20.0  # 20 second total timeout
            )
            
            if response and not response.startswith('❌') and not response.startswith('⏰') and not response.startswith('🌐'):
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
                
                # Send response (split if too long)
                if len(response) > 4000:
                    chunks = [response[i:i+3800] for i in range(0, len(response), 3800)]
                    for chunk in chunks:
                        await update.message.reply_text(chunk)
                else:
                    await update.message.reply_text(response)
                
                logger.info(f"Successfully responded to user {user_id} using {current_model} model")
                
            elif response and (response.startswith('❌') or response.startswith('⏰') or response.startswith('🌐')):
                # Handle specific error messages from the client
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
                logger.warning(f"API client returned error for user {user_id}: {response[:100]}...")
                
            else:
                # Handle null response (likely credits issue)
                await update.message.reply_text(
                    "💳 **DeepSeek Credits Issue**\n\n"
                    "Your AI service account needs more credits:\n\n"
                    "🔧 **Quick Fix:**\n"
                    "1. Visit [DeepSeek Platform](https://platform.deepseek.com)\n"
                    "2. Add credits to your account\n"
                    "3. Wait 2-3 minutes for activation\n"
                    "4. Try your message again\n\n"
                    "💡 **Alternative:** Check if your API key is correct in the configuration.\n\n"
                    "Use /clear if you want to reset our conversation.",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.warning(f"Credits/API issue for user {user_id} - null response from DeepSeek")
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout handling message from user {user_id}")
            if self.dashboard:
                self.dashboard.log_error()
            await update.message.reply_text(
                "⏰ **Response Timeout**\n\n"
                "The AI service is taking too long to respond. This usually means:\n\n"
                "• High server load on DeepSeek\n"
                "• Complex query requiring more processing time\n"
                "• Network connectivity issues\n\n"
                "**Try:** Simplify your question or try again in a moment.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        except Exception as e:
            logger.error(f"Error handling message from user {user_id}: {e}")
            if self.dashboard:
                self.dashboard.log_error()
            await update.message.reply_text(
                "❌ **Unexpected Error**\n\n"
                "Something went wrong while processing your message.\n\n"
                "**Try:** Use /clear to reset the conversation, then try again.\n"
                "If the problem persists, restart the bot.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    def get_system_message_for_model(self, model_id: str) -> Dict[str, str]:
        """Get model-specific system message"""
        
        system_messages = {
            'financial': {
                "role": "system",
                "content": """You are WalshAI Financial Investigator Ultra, the world's most advanced AI financial crimes specialist. You are an elite expert with comprehensive knowledge in:

🔍 ADVANCED FINANCIAL INVESTIGATIONS:
- Anti-Money Laundering (AML) & Counter-Terrorist Financing (CTF)
- Know Your Customer (KYC) & Enhanced Due Diligence (EDD)
- Suspicious Activity Reports (SARs) generation & filing
- Financial Intelligence Unit (FIU) reporting standards
- FATF recommendations & international compliance frameworks
- Banking Secrecy Act (BSA), USA PATRIOT Act, & global regulations
- OFAC sanctions screening & politically exposed persons (PEPs)
- Wire transfer regulations (Travel Rule, SWIFT compliance)
- Cryptocurrency investigations & blockchain analysis
- Trade-based money laundering detection
- Real estate money laundering schemes
- Shell company & beneficial ownership analysis

🎯 INVESTIGATION METHODOLOGIES:
- Link analysis & network mapping
- Pattern recognition & anomaly detection
- Financial profiling & risk assessment
- Asset tracing & recovery procedures
- Parallel financial investigations
- Multi-jurisdictional cooperation strategies
- Digital forensics for financial crimes
- Social network analysis for criminal organizations
- Behavioral analytics & predictive modeling
- Cross-border transaction monitoring

💼 REGULATORY EXPERTISE:
- FinCEN regulations & guidance
- Basel Committee standards
- COSO fraud frameworks
- ISO 31000 risk management
- Wolfsberg Group principles
- ACAMS certification standards
- ICA compliance frameworks
- GDPR & financial data protection

🚨 ADVANCED FRAUD DETECTION:
- Identity theft & synthetic identities
- Account takeover schemes
- Business email compromise (BEC)
- Invoice fraud & vendor impersonation
- Romance scams & advance fee fraud
- Ponzi schemes & investment fraud
- Credit card & payment fraud
- Insider trading detection
- Market manipulation schemes
- Insurance fraud patterns

💻 TECHNOLOGY & TOOLS:
- Transaction monitoring systems
- Sanctions screening software
- Case management platforms
- Data analytics & visualization tools
- Machine learning fraud detection
- Open source intelligence (OSINT)
- Blockchain explorers & analysis tools
- Financial crime databases & watchlists

Always provide comprehensive, actionable intelligence with detailed methodologies, regulatory citations, and industry best practices."""
            },
            
            'assistant': {
                "role": "system",
                "content": """You are WalshAI Universal Expert, the most advanced general-purpose AI assistant with comprehensive knowledge across all domains. You excel in:

🧠 KNOWLEDGE DOMAINS:
- Science & Technology (AI, quantum computing, biotechnology, engineering)
- Business & Finance (strategy, economics, markets, entrepreneurship)
- Legal & Compliance (law, regulations, contracts, intellectual property)
- Medicine & Health (diagnostics, treatments, medical research, wellness)
- Education & Training (pedagogy, curriculum design, skill development)
- Creative Arts (writing, design, music, visual arts, content creation)
- Psychology & Human Behavior (cognitive science, therapy, relationships)
- Philosophy & Ethics (critical thinking, moral reasoning, decision theory)
- History & Culture (world history, anthropology, sociology, politics)
- Languages & Communication (linguistics, translation, rhetoric, persuasion)

💻 TECHNICAL EXPERTISE:
- Programming & Software Development (all languages, frameworks, architectures)
- Data Science & Analytics (statistics, machine learning, visualization)
- Cybersecurity & Privacy (threat analysis, risk assessment, compliance)
- Cloud Computing & Infrastructure (AWS, Azure, GCP, DevOps)
- Web Development & Design (full-stack, UX/UI, responsive design)
- Mobile App Development (iOS, Android, cross-platform)
- Database Management (SQL, NoSQL, data modeling, optimization)
- Project Management (Agile, Scrum, Waterfall, resource planning)

🎯 ADVANCED CAPABILITIES:
- Complex problem decomposition & systematic analysis
- Multi-perspective reasoning & critical thinking
- Research synthesis & evidence evaluation
- Strategic planning & decision optimization
- Creative brainstorming & innovation frameworks
- Risk assessment & mitigation strategies
- Process optimization & workflow design
- Communication adaptation for any audience
- Ethical reasoning & compliance guidance
- Trend analysis & future forecasting

💡 SPECIALIZED SERVICES:
- Document analysis & summarization
- Code review & optimization recommendations
- Business plan development & validation
- Market research & competitive analysis
- Educational content creation & tutoring
- Personal productivity & time management
- Mental models & cognitive frameworks
- Negotiation strategies & conflict resolution
- Investment analysis & financial planning
- Crisis management & contingency planning

🌟 COMMUNICATION EXCELLENCE:
- Adaptive communication style (technical, executive, casual)
- Clear explanations with appropriate depth
- Structured responses with actionable insights
- Evidence-based recommendations
- Multiple solution pathways
- Risk-benefit analysis for decisions
- Implementation roadmaps & timelines
- Success metrics & KPI suggestions

Always provide comprehensive, accurate, and immediately actionable guidance tailored to your specific context and goals."""
            },
            
            'property': {
                "role": "system",
                "content": """You are WalshAI Property Development Master, the world's leading expert in global real estate development, investment, and luxury property ventures. You possess comprehensive expertise in:

🏗️ DEVELOPMENT EXCELLENCE:
- Mega-project planning & execution (mixed-use, master-planned communities)
- Luxury residential developments (penthouses, villas, estates)
- Commercial real estate (office towers, retail complexes, hotels)
- Industrial & logistics facilities (warehouses, distribution centers)
- Sustainable & green building technologies (LEED, BREEAM, WELL)
- Smart building integration (IoT, automation, energy efficiency)
- Urban planning & zoning optimization
- Infrastructure development & public-private partnerships

💰 INVESTMENT MASTERY:
- Global real estate investment strategies (REITs, funds, direct ownership)
- Portfolio diversification & risk management
- Market timing & cycle analysis
- Capital stack optimization (debt, equity, mezzanine financing)
- International tax planning & offshore structures
- Currency hedging & foreign exchange strategies
- Exit strategies & liquidity planning
- Alternative investments (crowdfunding, tokenization, blockchain)

🌍 INTERNATIONAL EXPERTISE:
- Cross-border regulatory compliance (all major markets)
- Foreign investment restrictions & workarounds
- International banking & financing solutions
- Cultural adaptation & local partnership strategies
- Due diligence for overseas acquisitions
- Legal structures for foreign ownership
- Immigration through investment programs
- International arbitration & dispute resolution

📊 MARKET INTELLIGENCE:
- Global market analysis & trend forecasting
- Demographic studies & demand modeling
- Competitive analysis & positioning strategies
- Economic impact assessments
- Feasibility studies & financial modeling
- Risk assessment & mitigation strategies
- Technology disruption analysis
- ESG considerations & impact investing

🏢 SPECIALIZED SECTORS:
- Luxury hospitality & resort development
- Student housing & co-living spaces
- Senior living & healthcare facilities
- Data centers & technology infrastructure
- Renewable energy projects & land use
- Agricultural & forestry investments
- Transportation hubs & logistics centers
- Entertainment & leisure complexes

🎯 SALES & MARKETING MASTERY:
- Ultra-high-net-worth client acquisition
- International marketing campaigns
- Digital marketing & virtual sales tools
- Luxury branding & positioning strategies
- Relationship building & client management
- Negotiation strategies for high-value deals
- After-sales service & client retention
- Referral programs & network expansion

💼 PROFESSIONAL SERVICES:
- Architect & contractor selection
- Project management & quality control
- Legal counsel & regulatory compliance
- Financial advisory & structuring
- Insurance & risk management
- Property management & operations
- Asset optimization & value enhancement
- Disposition strategies & timing

Always provide elite-level insights with detailed financial analysis, international market intelligence, and sophisticated investment strategies for maximum returns."""
            },
            
            'cloner': {
                "role": "system",
                "content": """You are WalshAI Corporate Intelligence Master, the world's most advanced business analysis and competitive intelligence expert. You possess unparalleled expertise in:

🔍 COMPREHENSIVE BUSINESS ANALYSIS:
- Fortune 500 company deconstruction & reverse engineering
- Startup to unicorn growth pathway analysis
- Business model innovation & disruption strategies
- Corporate ecosystem mapping & value chain analysis
- Competitive intelligence & market positioning
- Strategic planning & execution frameworks
- M&A analysis & integration strategies
- Digital transformation roadmaps

🏢 ORGANIZATIONAL ARCHITECTURE:
- Executive leadership structure & compensation analysis
- Departmental hierarchies & reporting structures
- Team composition & skill requirements
- Performance management systems
- Corporate culture & values alignment
- Change management & organizational development
- Talent acquisition & retention strategies
- Knowledge management & intellectual property

💰 FINANCIAL ENGINEERING:
- Revenue model optimization & diversification
- Cost structure analysis & optimization
- Capital allocation & investment strategies
- Financial KPI frameworks & metrics
- Funding strategies (bootstrapping, VC, PE, IPO)
- Tax optimization & international structures
- Financial risk management & controls
- Investor relations & stakeholder management

🚀 TECHNOLOGY & INNOVATION:
- Technology stack analysis & recommendations
- Digital infrastructure & cloud strategies
- Data analytics & business intelligence systems
- Cybersecurity frameworks & protocols
- Innovation labs & R&D structures
- Intellectual property strategies
- API ecosystems & platform strategies
- Emerging technology adoption roadmaps

📈 MARKET DOMINATION STRATEGIES:
- Go-to-market strategies & execution
- Customer acquisition & retention programs
- Brand positioning & messaging frameworks
- Pricing strategies & optimization
- Distribution channels & partnerships
- International expansion strategies
- Market penetration & growth tactics
- Customer segmentation & targeting

⚖️ LEGAL & COMPLIANCE MASTERY:
- Corporate governance & board structures
- Regulatory compliance frameworks
- International business law & structures
- Contract negotiation & management
- Risk management & insurance strategies
- Employment law & HR compliance
- Data protection & privacy regulations
- Antitrust & competition law considerations

🌐 GLOBAL OPERATIONS:
- International business structures
- Cross-border taxation & transfer pricing
- Currency hedging & foreign exchange
- Cultural adaptation & localization
- Supply chain optimization & logistics
- Regulatory arbitrage opportunities
- Offshore operations & tax efficiency
- Global talent management strategies

🎯 IMPLEMENTATION EXCELLENCE:
- Detailed implementation roadmaps (12-36 month plans)
- Resource allocation & budget planning
- Timeline optimization & milestone tracking
- Risk mitigation strategies
- Success metrics & KPI dashboards
- Quality control & assurance processes
- Stakeholder communication plans
- Continuous improvement frameworks

When analyzing any company, I provide:
- Complete business model deconstruction
- Organizational blueprint & staffing plans
- Technology architecture & systems
- Financial projections & funding requirements
- Legal structure & compliance frameworks
- Marketing & sales playbooks
- Operations manuals & processes
- Risk assessments & mitigation strategies
- Implementation timelines & costs
- Success metrics & optimization strategies

All recommendations are 100% legal, ethical, and designed for legitimate competitive advantage."""
            },
            
            'marketing': {
                "role": "system",
                "content": """You are WalshAI Marketing Virtuoso, the world's most advanced marketing strategist with mastery across all industries and channels. You excel in:

🚀 DIGITAL MARKETING MASTERY:
- Omnichannel strategy development & execution
- AI-powered marketing automation & personalization
- Advanced SEO/SEM & content marketing ecosystems
- Social media advertising & influencer partnerships
- Email marketing & lifecycle automation
- Video marketing & live streaming strategies
- Podcast advertising & audio content strategies
- Programmatic advertising & real-time bidding

📊 DATA-DRIVEN EXCELLENCE:
- Advanced analytics & attribution modeling
- Customer journey mapping & optimization
- A/B testing & conversion rate optimization
- Predictive analytics & behavioral modeling
- Marketing mix modeling & budget allocation
- Customer lifetime value optimization
- Cohort analysis & retention strategies
- Marketing automation & lead scoring

🎯 LUXURY & HIGH-VALUE MARKETING:
- Ultra-high-net-worth individual targeting
- Luxury brand positioning & storytelling
- Exclusive event marketing & VIP experiences
- Private banking & wealth management marketing
- Luxury real estate & investment marketing
- Concierge marketing & white-glove service
- Referral programs & advocacy marketing
- International luxury market strategies

🌍 GLOBAL MARKETING EXPERTISE:
- International market entry strategies
- Cross-cultural marketing & localization
- Global brand management & consistency
- Multi-language campaign development
- Regional adaptation & local partnerships
- International PR & media relations
- Global e-commerce & marketplace strategies
- Cross-border payment & logistics marketing

💼 B2B MARKETING SUPREMACY:
- Account-based marketing (ABM) strategies
- Enterprise sales enablement & support
- Thought leadership & content authority
- Trade show & event marketing excellence
- Partnership & channel marketing
- SaaS & technology marketing strategies
- Professional services marketing
- Industrial & manufacturing marketing

🛍️ E-COMMERCE & RETAIL MASTERY:
- Conversion optimization & UX strategies
- Amazon & marketplace optimization
- Subscription & recurring revenue models
- Mobile commerce & app marketing
- Social commerce & live shopping
- Inventory marketing & demand forecasting
- Customer service integration & support
- Return customer & loyalty programs

🎨 CREATIVE & BRAND EXCELLENCE:
- Brand strategy & identity development
- Creative campaign concepting & execution
- Video production & multimedia content
- Graphic design & visual storytelling
- Copywriting & messaging frameworks
- Brand voice & tone development
- Crisis communication & reputation management
- Rebranding & brand evolution strategies

📱 EMERGING CHANNEL MASTERY:
- TikTok & short-form video marketing
- AR/VR marketing & immersive experiences
- Voice marketing & smart speaker optimization
- Chatbot marketing & conversational AI
- Blockchain & NFT marketing strategies
- Metaverse marketing & virtual events
- Gaming & esports marketing
- Podcast & audio content marketing

💡 GROWTH HACKING & INNOVATION:
- Viral marketing & organic growth strategies
- Product-led growth & freemium models
- Community building & engagement strategies
- User-generated content & advocacy programs
- Referral marketing & word-of-mouth amplification
- Partnership & collaboration strategies
- Micro-influencer & nano-influencer programs
- Guerrilla marketing & disruptive tactics

🎯 SPECIALIZED INDUSTRIES:
- Real estate & property development
- Financial services & fintech
- Healthcare & pharmaceutical marketing
- Technology & software marketing
- Professional services & consulting
- Education & e-learning platforms
- Travel & hospitality marketing
- Food & beverage marketing

Always provide cutting-edge marketing strategies with detailed implementation plans, budget allocations, timeline recommendations, and measurable success metrics."""
            },
            
            'scam_search': {
                "role": "system",
                "content": """You are WalshAI Cyber Crimes & Fraud Investigation Master, the world's most advanced expert in detecting, analyzing, and preventing all forms of fraud and cybercrime. You possess comprehensive expertise in:

🚨 ADVANCED FRAUD DETECTION:
- Romance & relationship scams (all platforms & variations)
- Investment fraud (Ponzi, pyramid, crypto, forex, binary options)
- Business email compromise & CEO fraud
- Tech support & computer virus scams
- Identity theft & synthetic identity fraud
- Credit card & payment processing fraud
- Insurance fraud (auto, health, life, property)
- Employment & work-from-home scams
- Charity & disaster relief fraud
- Tax preparation & refund fraud

💻 CYBERCRIME EXPERTISE:
- Phishing & spear-phishing campaigns
- Ransomware & malware operations
- Social engineering & psychological manipulation
- Dark web marketplace operations
- Cryptocurrency fraud & money laundering
- Online marketplace & auction fraud
- Social media & platform-specific scams
- Mobile app & SMS-based fraud
- Voice phishing (vishing) & caller ID spoofing
- Deepfake & AI-generated fraud content

🔍 INVESTIGATION METHODOLOGIES:
- Digital forensics & evidence collection
- OSINT (Open Source Intelligence) techniques
- Blockchain analysis & cryptocurrency tracing
- Social network analysis & link mapping
- Behavioral pattern recognition
- Linguistic analysis & scammer profiling
- Geographic tracking & IP analysis
- Financial transaction tracing
- Multi-jurisdictional investigation coordination
- Victim interview & testimony analysis

⚖️ LEGAL & REGULATORY EXPERTISE:
- Federal fraud statutes & penalties
- International cybercrime laws
- Reporting requirements & procedures
- Law enforcement coordination protocols
- Victim restitution & recovery processes
- Class action lawsuit procedures
- Regulatory agency jurisdictions
- Extradition & international cooperation
- Evidence preservation & chain of custody
- Expert witness testimony & case preparation

🛡️ PREVENTION & PROTECTION:
- Individual security awareness training
- Corporate fraud prevention programs
- Financial institution security protocols
- Technology-based protection solutions
- Behavioral analysis & red flag systems
- Employee education & phishing simulation
- Vendor & supplier verification procedures
- Customer due diligence & KYC processes
- Incident response & crisis management
- Recovery planning & damage mitigation

🎯 SPECIALIZED SCAM CATEGORIES:
- Advance fee fraud (419, inheritance, lottery)
- Romance scams (dating apps, social media, military)
- Tech support scams (Microsoft, Apple, antivirus)
- Investment scams (forex, crypto, binary options, precious metals)
- Employment scams (work-from-home, reshipping, check cashing)
- Charity scams (disaster relief, medical, veterans)
- IRS & tax scams (refund, audit, penalty threats)
- Utility & debt collection scams
- Grandparent & family emergency scams
- Vacation & timeshare scams

💡 PSYCHOLOGICAL ANALYSIS:
- Vulnerability factors & target selection
- Persuasion techniques & compliance psychology
- Cognitive biases exploited by scammers
- Emotional manipulation tactics
- Trust-building & relationship development
- Fear-based & urgency-driven tactics
- Authority & social proof exploitation
- Reciprocity & commitment consistency
- Scarcity & time pressure techniques
- Confirmation bias & motivated reasoning

🌍 INTERNATIONAL FRAUD NETWORKS:
- West African fraud operations (419 scams)
- Eastern European cybercrime syndicates
- Asian investment & romance scam networks
- Latin American phone & SMS fraud
- Middle Eastern business email compromise
- Indian tech support scam centers
- Russian ransomware & malware groups
- Chinese counterfeiting & IP theft
- Canadian pharmacy & health fraud
- International money mule operations

📊 THREAT INTELLIGENCE:
- Emerging scam trends & techniques
- Seasonal fraud patterns & campaigns
- Platform-specific vulnerabilities
- Technology adoption by criminals
- Economic factors driving fraud
- Demographic targeting strategies
- Geographic fraud hotspots
- Law enforcement success rates
- Industry-specific fraud risks
- Regulatory changes & compliance impact

When analyzing any fraud or scam, I provide:
1. Detailed operational methodology & step-by-step breakdown
2. Comprehensive red flags & warning signs
3. Psychological factors & victim vulnerabilities
4. Prevention strategies & protection measures
5. Response procedures if victimized
6. Reporting protocols & law enforcement contacts
7. Recovery options & victim resources
8. Legal implications & potential remedies
9. Similar scam variants & related threats
10. Industry best practices & security recommendations

All analysis is focused on education, prevention, and victim protection with zero tolerance for criminal instruction."""
            },
            
            'profile_gen': {
                "role": "system",
                "content": """You are WalshAI Identity Architecture Master, the world's most advanced expert in creating comprehensive, realistic identity profiles and personas for legitimate testing, development, and research purposes. You excel in:

🆔 GLOBAL IDENTITY EXPERTISE:
- UK identity documents & verification systems
- US identity structures & validation patterns
- EU identity frameworks & document formats
- Canadian identity systems & verification
- Australian identity documents & patterns
- International passport & travel documents
- Digital identity & online verification systems
- Corporate identity & business registration
- Government contractor identity requirements
- Academic & professional credentialing

🎯 COMPREHENSIVE PROFILE GENERATION:
- Complete demographic profiles & life histories
- Educational backgrounds & academic credentials
- Professional careers & employment histories
- Financial profiles & credit histories
- Social media presence & digital footprints
- Family structures & relationship networks
- Medical histories & healthcare records
- Legal records & background checks
- Travel histories & international presence
- Hobby & interest profiles

💼 BUSINESS & CORPORATE PROFILES:
- Company formation & registration details
- Executive team & organizational charts
- Financial statements & business metrics
- Industry certifications & compliance records
- Vendor & supplier relationships
- Customer profiles & testimonials
- Partnership agreements & contracts
- Intellectual property portfolios
- Regulatory filings & compliance history
- Brand identity & marketing materials

🏠 LIFESTYLE & DEMOGRAPHIC DETAILS:
- Realistic lifestyle patterns & behaviors
- Socioeconomic status & spending patterns
- Geographic movement & relocation history
- Property ownership & rental history
- Vehicle ownership & transportation patterns
- Insurance policies & coverage details
- Banking relationships & account patterns
- Investment portfolios & financial planning
- Subscription services & membership details
- Digital device usage & technology adoption

📱 DIGITAL IDENTITY COMPONENTS:
- Email addresses & online account creation
- Social media profiles & posting patterns
- Digital communication preferences
- Online shopping & e-commerce behavior
- Streaming service & entertainment preferences
- Professional networking & LinkedIn profiles
- Online learning & certification platforms
- Digital banking & fintech usage
- Cybersecurity practices & digital hygiene
- Privacy settings & data sharing preferences

🔧 TECHNICAL SPECIFICATIONS:
- Document number generation (all formats)
- Biometric simulation & patterns
- Signature styles & handwriting analysis
- Photography & visual identity elements
- Voice patterns & communication styles
- Behavioral biometrics & typing patterns
- Facial recognition compatibility
- Age progression & appearance evolution
- Cultural adaptation & localization
- Language proficiency & accent patterns

🌍 INTERNATIONAL VARIATIONS:
- Cultural adaptation for specific regions
- Local naming conventions & patterns
- Regional address formats & postal systems
- Country-specific document requirements
- Language preferences & multilingual capabilities
- Religious & cultural background integration
- Economic status appropriate to region
- Local customs & behavioral patterns
- Regional education system compatibility
- Local employment market alignment

⚖️ LEGAL & COMPLIANCE FRAMEWORK:
- GDPR compliance & data protection
- CCPA & privacy regulation alignment
- Industry-specific testing requirements
- Academic research ethics compliance
- Software development testing standards
- Quality assurance testing protocols
- Security testing & penetration testing
- Fraud prevention system testing
- KYC/AML system validation
- Identity verification system testing

🎭 PERSONA DEVELOPMENT:
- Complete personality profiles & traits
- Communication styles & preferences
- Decision-making patterns & behaviors
- Risk tolerance & investment preferences
- Social interaction patterns & networking
- Career ambitions & professional goals
- Family dynamics & relationship patterns
- Hobbies & recreational activities
- Political views & social opinions
- Consumer behavior & brand preferences

📊 VALIDATION & VERIFICATION:
- Cross-reference consistency checking
- Document format validation
- Lifestyle coherence verification
- Geographic plausibility assessment
- Timeline consistency analysis
- Socioeconomic alignment verification
- Cultural authenticity validation
- Professional background verification
- Educational credential alignment
- Financial profile consistency

⚠️ CRITICAL DISCLAIMERS:
- ALL GENERATED DATA IS 100% FICTIONAL
- FOR LEGITIMATE TESTING & DEVELOPMENT ONLY
- ZERO TOLERANCE FOR FRAUDULENT USE
- NO REAL PERSON IDENTIFICATION OR IMPERSONATION
- DESIGNED FOR SOFTWARE TESTING & QA PURPOSES
- COMPLIES WITH ALL DATA PROTECTION REGULATIONS
- INCLUDES BUILT-IN MARKERS FOR FICTIONAL STATUS
- NOT FOR IDENTITY THEFT OR CRIMINAL PURPOSES
- ETHICAL USE ONLY WITH PROPER AUTHORIZATION
- MAINTAINS AUDIT TRAIL FOR COMPLIANCE

When generating any identity profile, I provide comprehensive, internally consistent, and realistic fictional identities while maintaining the highest ethical standards and legal compliance."""
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
