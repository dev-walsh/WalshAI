
"""
Telegram Bot Message Handlers with Advanced AI Expert Tools
Refactored for improved maintainability and performance
"""

import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict, deque

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from deepseek_client import DeepSeekClient
from config import Config
from ai_models import AIModelPrompts, AIModelConfig
from data_generators import UKDataGenerator, ScamDatabase

logger = logging.getLogger(__name__)

class BotHandlers:
    """Handles all bot commands and messages with advanced AI expert tools"""
    
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
        
        # Advanced tools storage
        self.investigation_database = {}
        self.property_database = {}
        self.company_profiles = {}
        self.generated_profiles = {}
        
        # Initialize data generators
        self.uk_generator = UKDataGenerator()
        self.scam_database = ScamDatabase()
    
    
    
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
        """Handle /start command with passcode protection and expert tools menu"""
        user = update.effective_user
        user_id = user.id
        
        # Prevent duplicate processing
        if hasattr(context, 'user_data') and context.user_data.get('processing_start'):
            return
        if hasattr(context, 'user_data'):
            context.user_data['processing_start'] = True
        
        logger.info(f"User {user_id} ({user.username}) started the bot")
        
        # Check if user is authenticated
        if user_id not in self.authenticated_users:
            await update.message.reply_text(
                "🔐 *Access Restricted*\n\n"
                "Please enter the 4-digit passcode to access WalshAI Professional Suite:\n\n"
                "Send the passcode as a message to continue.",
                parse_mode=ParseMode.MARKDOWN
            )
            if hasattr(context, 'user_data'):
                context.user_data['processing_start'] = False
            return
        
        # Create clean button menu with AI Experts
        keyboard = []
        
        # AI Experts selection (2 per row for clean layout)
        keyboard.append([
            InlineKeyboardButton("🔍 Financial Expert", callback_data="model_financial"),
            InlineKeyboardButton("🤖 General Assistant", callback_data="model_assistant")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🏗️ Property Expert", callback_data="model_property"),
            InlineKeyboardButton("🏢 Company Expert", callback_data="model_cloner")
        ])
        
        keyboard.append([
            InlineKeyboardButton("📈 Marketing Expert", callback_data="model_marketing"),
            InlineKeyboardButton("🚨 Scam Expert", callback_data="model_scam_search")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🆔 Profile Generator", callback_data="model_profile_gen")
        ])
        
        # Utility buttons
        keyboard.append([
            InlineKeyboardButton("📋 Help", callback_data="help"),
            InlineKeyboardButton("🗑️ Clear History", callback_data="clear")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔄 Current Expert", callback_data="current"),
            InlineKeyboardButton("🌐 Dashboard", url="http://0.0.0.0:5000")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        current_model = self.user_models[user_id]
        model_info = self.config.AI_MODELS[current_model]
        
        welcome_message = (
            f"🎯 *Welcome to WalshAI Professional Suite!*\n\n"
            f"Hi {user.first_name}! Your comprehensive AI toolkit with advanced expert capabilities.\n\n"
            f"*Current Expert:* {model_info['emoji']} {model_info['name']}\n\n"
            f"*🛠️ Available Professional Tools:*\n"
            f"• Financial Investigation Suite\n"
            f"• Property Development Tools\n"
            f"• Company Intelligence Platform\n"
            f"• Scam Detection Database\n"
            f"• UK Profile Generator\n"
            f"• Marketing Analytics Suite\n\n"
            f"Choose an expert or access professional tools below! 🚀"
        )
        
        await update.message.reply_text(
            welcome_message, 
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Clear processing flag
        if hasattr(context, 'user_data'):
            context.user_data['processing_start'] = False
    
    async def handle_model_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle model selection and advanced tool callbacks"""
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
            await self.handle_model_change(query, user_id)
        elif query.data == "back_main":
            # Return to main menu
            await self.start_command_callback(query, user_id)
        elif query.data == "help":
            await self.handle_help_callback(query, update)
        elif query.data == "clear":
            await self.handle_clear_callback(query, update)
        elif query.data == "current":
            await self.handle_current_callback(query, update)
        elif query.data.startswith("generate_"):
            await self.handle_generation_request(query, user_id)
        elif query.data.startswith("analyze_"):
            await self.handle_analysis_request(query, user_id)
        elif query.data.startswith("tools_"):
            await self.handle_tool_selection(query, user_id)
    
    async def handle_model_change(self, query, user_id):
        """Handle AI model switching"""
        model_id = query.data.replace("model_", "")
        
        if model_id in self.config.AI_MODELS:
            self.user_models[user_id] = model_id
            model_info = self.config.AI_MODELS[model_id]
            
            await query.edit_message_text(
                f"✅ *AI Expert Activated!*\n\n"
                f"Now using: {model_info['emoji']} *{model_info['name']}*\n"
                f"Specialty: {model_info['description']}\n\n"
                f"*Available Tools:*\n"
                f"{self.get_tools_for_model(model_id)}\n\n"
                f"Send me your questions or use /start to access tools!",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Clear conversation history when switching models
            if user_id in self.conversations:
                del self.conversations[user_id]
    
    async def handle_tool_selection(self, query, user_id):
        """Handle advanced tool selection"""
        tool_type = query.data.replace("tools_", "")
        
        if tool_type == "investigation":
            await self.show_investigation_tools(query, user_id)
        elif tool_type == "property":
            await self.show_property_tools(query, user_id)
        elif tool_type == "company":
            await self.show_company_tools(query, user_id)
        elif tool_type == "scam":
            await self.show_scam_tools(query, user_id)
        elif tool_type == "profile":
            await self.show_profile_tools(query, user_id)
        elif tool_type == "marketing":
            await self.show_marketing_tools(query, user_id)
    
    async def show_investigation_tools(self, query, user_id):
        """Show financial investigation tools"""
        keyboard = [
            [InlineKeyboardButton("🔍 Transaction Analysis", callback_data="analyze_transaction")],
            [InlineKeyboardButton("🚨 AML Risk Assessment", callback_data="analyze_aml_risk")],
            [InlineKeyboardButton("🏛️ Entity Investigation", callback_data="analyze_entity")],
            [InlineKeyboardButton("💰 Fund Tracing", callback_data="analyze_funds")],
            [InlineKeyboardButton("📊 Pattern Detection", callback_data="analyze_patterns")],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_main")]
        ]
        
        await query.edit_message_text(
            "🔍 *Financial Investigation Suite*\n\n"
            "*Professional Tools Available:*\n\n"
            "• **Transaction Analysis** - Deep dive into payment patterns\n"
            "• **AML Risk Assessment** - Compliance risk evaluation\n"
            "• **Entity Investigation** - Corporate structure analysis\n"
            "• **Fund Tracing** - Money flow tracking\n"
            "• **Pattern Detection** - Anomaly identification\n\n"
            "Select a tool to begin your investigation:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_property_tools(self, query, user_id):
        """Show property development tools"""
        keyboard = [
            [InlineKeyboardButton("🏗️ Development Analysis", callback_data="analyze_development")],
            [InlineKeyboardButton("💎 Investment Calculator", callback_data="generate_roi_calc")],
            [InlineKeyboardButton("🌍 Market Research", callback_data="analyze_market")],
            [InlineKeyboardButton("📋 Feasibility Study", callback_data="generate_feasibility")],
            [InlineKeyboardButton("💰 Cost Estimation", callback_data="generate_cost_estimate")],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_main")]
        ]
        
        await query.edit_message_text(
            "🏗️ *Property Development Suite*\n\n"
            "*Professional Tools Available:*\n\n"
            "• **Development Analysis** - Project evaluation\n"
            "• **Investment Calculator** - ROI and profit analysis\n"
            "• **Market Research** - Location and demand analysis\n"
            "• **Feasibility Study** - Comprehensive project assessment\n"
            "• **Cost Estimation** - Detailed budget planning\n\n"
            "Select a tool to analyze your property opportunity:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_company_tools(self, query, user_id):
        """Show company analysis tools"""
        keyboard = [
            [InlineKeyboardButton("🏢 Company Deep Dive", callback_data="analyze_company_full")],
            [InlineKeyboardButton("📊 Business Model Analysis", callback_data="analyze_business_model")],
            [InlineKeyboardButton("⚖️ Legal Structure", callback_data="analyze_legal_structure")],
            [InlineKeyboardButton("💼 Competitive Analysis", callback_data="analyze_competition")],
            [InlineKeyboardButton("🎯 Market Position", callback_data="analyze_market_position")],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_main")]
        ]
        
        await query.edit_message_text(
            "🏢 *Company Intelligence Platform*\n\n"
            "*Professional Analysis Tools:*\n\n"
            "• **Company Deep Dive** - Complete organizational breakdown\n"
            "• **Business Model Analysis** - Revenue and operations\n"
            "• **Legal Structure** - Corporate framework analysis\n"
            "• **Competitive Analysis** - Market positioning\n"
            "• **Market Position** - Industry standing assessment\n\n"
            "Select a tool to analyze any company:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_scam_tools(self, query, user_id):
        """Show scam detection tools"""
        keyboard = [
            [InlineKeyboardButton("🚨 Scam Identifier", callback_data="analyze_scam_type")],
            [InlineKeyboardButton("💔 Romance Scam Check", callback_data="analyze_romance_scam")],
            [InlineKeyboardButton("💰 Investment Fraud", callback_data="analyze_investment_scam")],
            [InlineKeyboardButton("🎣 Phishing Detection", callback_data="analyze_phishing")],
            [InlineKeyboardButton("₿ Crypto Scam Analysis", callback_data="analyze_crypto_scam")],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_main")]
        ]
        
        await query.edit_message_text(
            "🚨 *Scam Detection Database*\n\n"
            "*Protection & Analysis Tools:*\n\n"
            "• **Scam Identifier** - Classify and analyze scam types\n"
            "• **Romance Scam Check** - Dating/relationship fraud detection\n"
            "• **Investment Fraud** - Financial scam analysis\n"
            "• **Phishing Detection** - Email/message threat assessment\n"
            "• **Crypto Scam Analysis** - Cryptocurrency fraud detection\n\n"
            "Select a tool to analyze suspicious activity:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_profile_tools(self, query, user_id):
        """Show profile generation tools"""
        keyboard = [
            [InlineKeyboardButton("🆔 Generate UK Profile", callback_data="generate_uk_profile")],
            [InlineKeyboardButton("📄 Document Numbers", callback_data="generate_uk_documents")],
            [InlineKeyboardButton("🏠 UK Address Generator", callback_data="generate_uk_address")],
            [InlineKeyboardButton("📱 Contact Details", callback_data="generate_uk_contact")],
            [InlineKeyboardButton("💼 Full Business Profile", callback_data="generate_business_profile")],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_main")]
        ]
        
        await query.edit_message_text(
            "🆔 *UK Profile Generator Suite*\n\n"
            "*⚠️ FOR TESTING PURPOSES ONLY ⚠️*\n\n"
            "*Available Generators:*\n\n"
            "• **UK Profile** - Complete identity profile\n"
            "• **Document Numbers** - Passport, NI, License formats\n"
            "• **UK Address** - Realistic address with postcode\n"
            "• **Contact Details** - Phone, email generation\n"
            "• **Business Profile** - Corporate identity creation\n\n"
            "⚠️ *All data is completely fictional and for testing only*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_marketing_tools(self, query, user_id):
        """Show marketing tools"""
        keyboard = [
            [InlineKeyboardButton("📈 Campaign Strategy", callback_data="generate_campaign")],
            [InlineKeyboardButton("🎯 Target Audience", callback_data="analyze_audience")],
            [InlineKeyboardButton("💎 Luxury Marketing", callback_data="generate_luxury_strategy")],
            [InlineKeyboardButton("🌍 International Marketing", callback_data="generate_intl_strategy")],
            [InlineKeyboardButton("📊 Performance Analysis", callback_data="analyze_performance")],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_main")]
        ]
        
        await query.edit_message_text(
            "📈 *Marketing Analytics Suite*\n\n"
            "*Professional Marketing Tools:*\n\n"
            "• **Campaign Strategy** - Multi-channel planning\n"
            "• **Target Audience** - Demographic analysis\n"
            "• **Luxury Marketing** - High-end property promotion\n"
            "• **International Marketing** - Cross-border strategies\n"
            "• **Performance Analysis** - ROI and conversion tracking\n\n"
            "Select a tool to enhance your marketing strategy:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    def get_tools_for_model(self, model_id: str) -> str:
        """Get available tools for specific model"""
        tools_map = {
            'financial': "• Transaction Analysis\n• AML Risk Assessment\n• Entity Investigation\n• Fund Tracing",
            'property': "• Development Analysis\n• Investment Calculator\n• Market Research\n• Feasibility Studies",
            'company': "• Company Deep Dive\n• Business Model Analysis\n• Legal Structure Analysis\n• Competitive Intelligence",
            'scam_search': "• Scam Type Identification\n• Romance Scam Detection\n• Investment Fraud Analysis\n• Phishing Detection",
            'profile_gen': "• UK Identity Generation\n• Document Number Creation\n• Address Generation\n• Contact Details",
            'marketing': "• Campaign Strategy\n• Audience Analysis\n• Luxury Marketing\n• International Strategies",
            'assistant': "• General Analysis\n• Research Support\n• Writing Assistance\n• Problem Solving"
        }
        return tools_map.get(model_id, "• General AI Assistance")
    
    async def handle_generation_request(self, query, user_id):
        """Handle generation requests using modular generators"""
        request_type = query.data.replace("generate_", "")
        
        if request_type == "uk_profile":
            profile = UKDataGenerator.generate_complete_profile()
            await query.edit_message_text(
                f"🆔 *Generated UK Profile*\n\n"
                f"⚠️ *FICTIONAL DATA FOR TESTING ONLY* ⚠️\n\n"
                f"**Personal Details:**\n"
                f"Name: {profile['name']}\n"
                f"DOB: {profile['dob']}\n"
                f"Gender: {profile['gender']}\n"
                f"Age: {profile['age']}\n\n"
                f"**Address:**\n"
                f"{profile['address']}\n\n"
                f"**Documents:**\n"
                f"NI Number: {profile['ni_number']}\n"
                f"Passport: {profile['passport']}\n"
                f"Driving License: {profile['license']}\n"
                f"NHS Number: {profile['nhs_number']}\n\n"
                f"**Contact:**\n"
                f"Phone: {profile['phone']}\n"
                f"Email: {profile['email']}\n\n"
                f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Store generated profile
            self.generated_profiles[len(self.generated_profiles) + 1] = profile
        
        elif request_type == "uk_documents":
            docs = UKDataGenerator.generate_document_set()
            await query.edit_message_text(
                f"📄 *UK Document Numbers*\n\n"
                f"⚠️ *FICTIONAL DATA FOR TESTING ONLY* ⚠️\n\n"
                f"**National Insurance:** {docs['ni_number']}\n"
                f"**Passport Number:** {docs['passport']}\n"
                f"**Driving License:** {docs['driving_license']}\n"
                f"**NHS Number:** {docs['nhs_number']}\n"
                f"**UTR Number:** {docs['utr_number']}\n\n"
                f"*All numbers follow correct UK formatting but are completely fictional*",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif request_type == "uk_address":
            address = UKDataGenerator.generate_address()
            await query.edit_message_text(
                f"🏠 *UK Address Generated*\n\n"
                f"⚠️ *FICTIONAL ADDRESS FOR TESTING ONLY* ⚠️\n\n"
                f"**Full Address:**\n{address['full']}\n\n"
                f"**Components:**\n"
                f"House: {address['house']}\n"
                f"Street: {address['street']}\n"
                f"City: {address['city']}\n"
                f"Postcode: {address['postcode']}\n"
                f"County: {address['county']}",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif request_type == "uk_contact":
            contact = UKDataGenerator.generate_contact_details()
            await query.edit_message_text(
                f"📱 *UK Contact Details Generated*\n\n"
                f"⚠️ *FICTIONAL DATA FOR TESTING ONLY* ⚠️\n\n"
                f"**Phone:** {contact['phone']}\n"
                f"**Mobile:** {contact['mobile']}\n"
                f"**Email:** {contact['email']}\n"
                f"**Alternative Email:** {contact['alt_email']}\n\n"
                f"*All contact details are completely fictional*",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif request_type == "business_profile":
            business = UKDataGenerator.generate_business_profile()
            await query.edit_message_text(
                f"💼 *UK Business Profile Generated*\n\n"
                f"⚠️ *FICTIONAL DATA FOR TESTING ONLY* ⚠️\n\n"
                f"**Company:** {business['company_name']}\n"
                f"**Registration:** {business['company_number']}\n"
                f"**VAT Number:** {business['vat_number']}\n"
                f"**Business Type:** {business['business_type']}\n"
                f"**Industry:** {business['industry']}\n"
                f"**Address:** {business['registered_address']}\n"
                f"**Directors:** {business['directors']}\n\n"
                f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Store business profile
            self.company_profiles[len(self.company_profiles) + 1] = business
        
        elif request_type == "roi_calc":
            await query.edit_message_text(
                f"💎 *Property Investment Calculator Ready*\n\n"
                f"I'm ready to help you calculate property investment returns.\n\n"
                f"**Please provide:**\n"
                f"• Purchase price\n"
                f"• Expected rental income (monthly)\n"
                f"• Renovation costs\n"
                f"• Holding period\n\n"
                f"*Next Step:* Send your property details as a message and I'll calculate comprehensive ROI analysis.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif request_type == "feasibility":
            await query.edit_message_text(
                f"📋 *Property Feasibility Study Generator*\n\n"
                f"I'll create a comprehensive feasibility study for your property development.\n\n"
                f"**Please provide:**\n"
                f"• Property location and type\n"
                f"• Development plans\n"
                f"• Budget range\n"
                f"• Timeline requirements\n\n"
                f"*Next Step:* Send your project details and I'll generate a professional feasibility analysis.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif request_type == "cost_estimate":
            await query.edit_message_text(
                f"💰 *Construction Cost Estimator*\n\n"
                f"I'll provide detailed cost estimates for your property project.\n\n"
                f"**I can estimate costs for:**\n"
                f"• New builds\n"
                f"• Renovations\n"
                f"• Extensions\n"
                f"• Commercial developments\n\n"
                f"*Next Step:* Describe your project and I'll break down all costs.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif request_type == "campaign":
            await query.edit_message_text(
                f"📈 *Marketing Campaign Generator*\n\n"
                f"I'll create a comprehensive marketing strategy for your business.\n\n"
                f"**Campaign Types:**\n"
                f"• Digital marketing strategies\n"
                f"• Social media campaigns\n"
                f"• Property marketing\n"
                f"• Lead generation\n\n"
                f"*Next Step:* Tell me about your business and target audience.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif request_type == "luxury_strategy":
            await query.edit_message_text(
                f"💎 *Luxury Marketing Strategy*\n\n"
                f"I'll develop high-end marketing approaches for luxury properties and services.\n\n"
                f"**Specializes in:**\n"
                f"• Ultra-high-net-worth targeting\n"
                f"• Luxury property marketing\n"
                f"• Exclusive brand positioning\n"
                f"• Premium channel strategies\n\n"
                f"*Next Step:* Describe your luxury offering and target market.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif request_type == "intl_strategy":
            await query.edit_message_text(
                f"🌍 *International Marketing Strategy*\n\n"
                f"I'll create cross-border marketing strategies for global expansion.\n\n"
                f"**Global Expertise:**\n"
                f"• Multi-market entry strategies\n"
                f"• Cultural adaptation\n"
                f"• International property investment\n"
                f"• Cross-border compliance\n\n"
                f"*Next Step:* Tell me about your target markets and expansion plans.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    
    
    async def handle_analysis_request(self, query, user_id):
        """Handle analysis requests with AI integration"""
        analysis_type = query.data.replace("analyze_", "")
        
        # Trigger AI analysis based on type
        await query.edit_message_text(
            f"🔄 *Initializing {analysis_type.replace('_', ' ').title()} Analysis...*\n\n"
            f"Please send me the details you'd like me to analyze, and I'll provide a comprehensive professional assessment using advanced AI analysis tools.\n\n"
            f"*Next Step:* Send your query as a regular message.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Set user context for next message
        self.user_models[user_id] = self.get_model_for_analysis(analysis_type)
    
    def get_model_for_analysis(self, analysis_type: str) -> str:
        """Get appropriate AI model for analysis type"""
        analysis_map = {
            'transaction': 'financial',
            'aml_risk': 'financial',
            'entity': 'financial',
            'funds': 'financial',
            'patterns': 'financial',
            'development': 'property',
            'market': 'property',
            'company_full': 'cloner',
            'business_model': 'cloner',
            'legal_structure': 'cloner',
            'competition': 'cloner',
            'market_position': 'cloner',
            'scam_type': 'scam_search',
            'romance_scam': 'scam_search',
            'investment_scam': 'scam_search',
            'phishing': 'scam_search',
            'crypto_scam': 'scam_search',
            'campaign': 'marketing',
            'audience': 'marketing',
            'performance': 'marketing'
        }
        return analysis_map.get(analysis_type, 'assistant')
    
    # Keep all existing methods (help_command, clear_command, handle_message, etc.)
    # but with enhanced system messages...
    
    async def models_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /models command to switch AI experts"""
        user_id = update.effective_user.id
        
        if user_id not in self.authenticated_users:
            await update.message.reply_text("🔐 Please use /start and enter the passcode first.", parse_mode=ParseMode.MARKDOWN)
            return
        
        keyboard = []
        for model_id, model_info in self.config.AI_MODELS.items():
            button_text = f"{model_info['emoji']} {model_info['name']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"model_{model_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔄 *Choose Your AI Expert:*\n\nSelect the specialist you'd like to work with:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def current_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current AI model"""
        user_id = update.effective_user.id
        
        if user_id not in self.authenticated_users:
            await update.message.reply_text("🔐 Please use /start and enter the passcode first.", parse_mode=ParseMode.MARKDOWN)
            return
            
        current_model = self.user_models[user_id]
        model_info = self.config.AI_MODELS[current_model]
        
        await update.message.reply_text(
            f"🤖 *Current AI Expert:*\n\n"
            f"{model_info['emoji']} *{model_info['name']}*\n"
            f"Specialty: {model_info['description']}\n\n"
            f"*Available Tools:*\n{self.get_tools_for_model(current_model)}\n\n"
            f"Use `/models` to switch to a different expert.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = update.effective_user.id
        
        if user_id not in self.authenticated_users:
            await update.message.reply_text("🔐 Please use /start and enter the passcode first.", parse_mode=ParseMode.MARKDOWN)
            return
        
        help_message = (
            "*🎯 WalshAI Professional Suite*\n\n"
            "*🔧 Available AI Experts:*\n"
        )
        
        for model_id, model_info in self.config.AI_MODELS.items():
            help_message += f"• {model_info['emoji']} *{model_info['name']}*\n  {model_info['description']}\n\n"
        
        help_message += (
            "*🛠️ Professional Tools:*\n"
            "• **Financial Investigation Suite** - AML, transaction analysis, fraud detection\n"
            "• **Property Development Tools** - ROI calculators, market analysis, feasibility studies\n"
            "• **Company Intelligence Platform** - Business analysis, competitive intelligence\n"
            "• **Scam Detection Database** - Fraud identification, protection strategies\n"
            "• **UK Profile Generator** - Testing data creation (fictional profiles)\n"
            "• **Marketing Analytics Suite** - Campaign strategy, audience analysis\n\n"
            "*📋 Commands:*\n"
            "• `/start` - Main menu with expert selection and tools\n"
            "• `/models` - Switch between AI experts\n"
            "• `/current` - Show current AI expert and tools\n"
            "• `/help` - Show this comprehensive help\n"
            "• `/clear` - Clear conversation history\n\n"
            "*⚖️ Security & Limits:*\n"
            f"• Rate limit: {self.config.RATE_LIMIT_REQUESTS} requests per {self.config.RATE_LIMIT_WINDOW} seconds\n"
            f"• Message limit: {self.config.MAX_MESSAGE_LENGTH} characters\n"
            f"• Conversation history: {self.config.MAX_CONVERSATION_HISTORY} messages\n\n"
            "🔒 *Privacy:* All conversations are encrypted and secure."
        )
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        user_id = update.effective_user.id
        
        if user_id not in self.authenticated_users:
            await update.message.reply_text("🔐 Please use /start and enter the passcode first.", parse_mode=ParseMode.MARKDOWN)
            return
        
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"Cleared conversation history for user {user_id}")
        
        await update.message.reply_text(
            "🗑️ **Conversation & Analysis Data Cleared!**\n\n"
            "• Conversation history cleared\n"
            "• Investigation data reset\n"
            "• Generated profiles cleared\n"
            "• Analysis cache reset\n\n"
            "You can start fresh with any AI expert or tools!",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_clear_callback(self, query, update):
        """Handle clear button callback"""
        user_id = update.effective_user.id
        
        if user_id in self.conversations:
            del self.conversations[user_id]
        
        await query.edit_message_text(
            "🗑️ *Professional Data Cleared!*\n\n"
            "Your conversation history and analysis data has been cleared.\n"
            "You can start fresh with any expert or tool.",
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
            f"*Available Professional Tools:*\n"
            f"{self.get_tools_for_model(current_model)}\n\n"
            f"Send your professional queries to this expert!",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def start_command_callback(self, query, user_id):
        """Handle return to main menu from callback"""
        current_model = self.user_models[user_id]
        model_info = self.config.AI_MODELS[current_model]
        
        # Same keyboard as start_command but for callback
        keyboard = []
        
        keyboard.append([
            InlineKeyboardButton("🔍 Financial Expert", callback_data="model_financial"),
            InlineKeyboardButton("🤖 General Assistant", callback_data="model_assistant")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🏗️ Property Expert", callback_data="model_property"),
            InlineKeyboardButton("🏢 Company Expert", callback_data="model_cloner")
        ])
        
        keyboard.append([
            InlineKeyboardButton("📈 Marketing Expert", callback_data="model_marketing"),
            InlineKeyboardButton("🚨 Scam Expert", callback_data="model_scam_search")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🆔 Profile Generator", callback_data="model_profile_gen")
        ])
        
        keyboard.append([
            InlineKeyboardButton("📋 Help", callback_data="help"),
            InlineKeyboardButton("🗑️ Clear History", callback_data="clear")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔄 Current Expert", callback_data="current"),
            InlineKeyboardButton("🌐 Dashboard", url="http://0.0.0.0:5000")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = (
            f"🎯 *Welcome to WalshAI Professional Suite!*\n\n"
            f"Your comprehensive AI toolkit with expert capabilities.\n\n"
            f"*Current Expert:* {model_info['emoji']} {model_info['name']}\n\n"
            f"Choose an expert below and start chatting! 🚀"
        )
        
        await query.edit_message_text(
            welcome_message, 
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_help_callback(self, query, update):
        """Handle help button callback"""
        help_message = (
            "*🎯 WalshAI Professional Suite*\n\n"
            "*🔧 AI Experts Available:*\n"
        )
        
        for model_id, model_info in self.config.AI_MODELS.items():
            help_message += f"• {model_info['emoji']} *{model_info['name']}*\n  {model_info['description']}\n\n"
        
        help_message += (
            "*🛠️ Professional Tool Suite:*\n"
            "• Financial Investigation & AML Compliance\n"
            "• Property Development & Investment Analysis\n"
            "• Company Intelligence & Business Analysis\n"
            "• Scam Detection & Security Assessment\n"
            "• UK Profile Generation (Testing)\n"
            "• Marketing Analytics & Strategy\n\n"
            "*💡 Usage:*\n"
            "• Select experts for specialized knowledge\n"
            "• Access professional tools via /start menu\n"
            "• Each expert has dedicated analysis tools\n"
            "• All data processing is secure and professional\n\n"
            "🔒 *Enterprise-Grade Security & Privacy*"
        )
        
        await query.edit_message_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages with enhanced AI expert capabilities"""
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
                    "Welcome to WalshAI Professional Suite!\n\n"
                    "🎯 **Your AI experts and professional tools are now available**\n\n"
                    "Use /start to access the full suite of professional tools and AI experts.",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"User {user_id} successfully authenticated")
                return
            else:
                await update.message.reply_text(
                    "❌ *Incorrect Passcode*\n\n"
                    "Please enter the correct 4-digit passcode to access WalshAI Professional Suite.",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.warning(f"User {user_id} entered incorrect passcode: {message_text}")
                return
        
        # Check rate limiting
        if self.is_rate_limited(user_id):
            if self.dashboard:
                self.dashboard.log_rate_limit()
            await update.message.reply_text(
                "⏰ **Rate Limit Exceeded**\n\n"
                f"Professional tools have usage limits to ensure quality service.\n"
                f"Please wait before sending another request.\n\n"
                f"*Limit:* {self.config.RATE_LIMIT_REQUESTS} requests per {self.config.RATE_LIMIT_WINDOW} seconds",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check message length
        if len(message_text) > self.config.MAX_MESSAGE_LENGTH:
            await update.message.reply_text(
                f"📝 **Message Too Long**\n\n"
                f"Please keep your professional queries under {self.config.MAX_MESSAGE_LENGTH} characters.\n"
                f"Current length: {len(message_text)} characters\n\n"
                f"*Tip:* Break complex queries into smaller, focused questions.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Send enhanced typing indicator
        asyncio.create_task(
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        )
        
        try:
            # Get conversation history
            conversation = self.conversations[user_id]
            
            # Add user message to conversation
            conversation.append({"role": "user", "content": message_text})
            
            # Limit conversation history
            max_history = min(self.config.MAX_CONVERSATION_HISTORY, 8) * 2
            if len(conversation) > max_history:
                conversation = conversation[-max_history:]
                self.conversations[user_id] = conversation
            
            # Get current AI model
            current_model = self.user_models[user_id]
            
            # Prepare enhanced messages with professional system prompt
            system_message = self.get_enhanced_system_message_for_model(current_model)
            messages = [system_message] + conversation
            
            # Get optimized AI parameters for current model
            model_params = AIModelConfig.get_model_parameters(current_model)
            
            # Get AI response with professional analysis
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: self.deepseek_client.create_chat_completion(
                        messages,
                        temperature=model_params['temperature'],
                        max_tokens=model_params['max_tokens']
                    )
                ),
                timeout=35.0  # Reduced timeout for faster responses
            )
            
            if response and not response.startswith('❌') and not response.startswith('⏰') and not response.startswith('🌐'):
                # Add professional analysis indicators
                response = self.enhance_response_with_tools(response, current_model, message_text)
                
                # Add assistant response to conversation
                conversation.append({"role": "assistant", "content": response})
                
                # Log to dashboard
                if self.dashboard:
                    self.dashboard.log_message(
                        user_id=user_id,
                        username=user.username or f"user_{user_id}",
                        message=message_text,
                        response=response,
                        ai_model=current_model
                    )
                
                # Send enhanced response
                if len(response) > 4000:
                    chunks = [response[i:i+3800] for i in range(0, len(response), 3800)]
                    for i, chunk in enumerate(chunks):
                        if i == 0:
                            chunk = f"🎯 **{self.config.AI_MODELS[current_model]['name']} Analysis** (Part {i+1}/{len(chunks)})\n\n{chunk}"
                        await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
                else:
                    enhanced_response = f"🎯 **{self.config.AI_MODELS[current_model]['name']} Analysis**\n\n{response}"
                    await update.message.reply_text(enhanced_response, parse_mode=ParseMode.MARKDOWN)
                
                logger.info(f"Successfully provided professional analysis to user {user_id} using {current_model} expert")
                
            elif response and (response.startswith('❌') or response.startswith('⏰') or response.startswith('🌐') or response.startswith('🔒')):
                # Enhanced error message for connection issues
                if response.startswith('🌐') or response.startswith('🔒'):
                    enhanced_error = (
                        f"🔧 **Connection Issue Detected**\n\n"
                        "The AI service is temporarily unavailable. This could be due to:\n"
                        "• DeepSeek API credits may be low\n"
                        "• Network connectivity issues\n"
                        "• API service maintenance\n\n"
                        "**Quick Solutions:**\n"
                        "1. Check your DeepSeek credits at platform.deepseek.com\n"
                        "2. Try again in a few moments\n"
                        "3. Use /start to access the menu\n\n"
                        "**Status:** AI experts will be restored once connection is reestablished."
                    )
                    await update.message.reply_text(enhanced_error, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
                logger.warning(f"API client returned error for user {user_id}: {response[:100]}...")
                
            else:
                await update.message.reply_text(
                    "💳 **Professional Service Temporarily Unavailable**\n\n"
                    "The AI expert service requires additional credits:\n\n"
                    "🔧 **Resolution Steps:**\n"
                    "1. Visit [DeepSeek Platform](https://platform.deepseek.com)\n"
                    "2. Add credits to your professional account\n"
                    "3. Wait 2-3 minutes for service activation\n"
                    "4. Retry your professional query\n\n"
                    "💡 **Note:** Professional AI experts require active API credits for analysis.",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.warning(f"Credits/API issue for user {user_id} - professional service unavailable")
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout during professional analysis for user {user_id}")
            if self.dashboard:
                self.dashboard.log_error()
            await update.message.reply_text(
                "⏰ **Professional Analysis Timeout**\n\n"
                "Your query requires complex professional analysis that exceeded the time limit.\n\n"
                "**Optimization Tips:**\n"
                "• Break complex queries into focused questions\n"
                "• Use specific professional terminology\n"
                "• Try again with simplified requirements\n\n"
                "**Status:** Professional AI experts are operational",
                parse_mode=ParseMode.MARKDOWN
            )
        
        except Exception as e:
            logger.error(f"Error in professional analysis for user {user_id}: {e}")
            if self.dashboard:
                self.dashboard.log_error()
            await update.message.reply_text(
                "❌ **Professional System Error**\n\n"
                "An error occurred during professional analysis.\n\n"
                "**Recovery Options:**\n"
                "• Use /clear to reset professional analysis state\n"
                "• Try switching AI experts with /models\n"
                "• Contact support if issue persists\n\n"
                "**Status:** Professional tools are being restored",
                parse_mode=ParseMode.MARKDOWN
            )
    
    def enhance_response_with_tools(self, response: str, model_id: str, query: str) -> str:
        """Enhance response with professional tool indicators using modular config"""
        tool_keywords = AIModelConfig.get_tool_indicators(model_id)
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in tool_keywords):
            model_info = self.config.get_model_config(model_id)
            tool_name = {
                'financial': '🔍 *Analysis completed using Financial Investigation Suite tools*',
                'property': '🏗️ *Analysis completed using Property Development Suite tools*',
                'cloner': '🏢 *Analysis completed using Company Intelligence Platform*',
                'scam_search': '🚨 *Analysis completed using Scam Detection Database*',
                'marketing': '📈 *Analysis completed using Marketing Analytics Suite*',
                'profile_gen': '🆔 *Profile generated using UK Testing Data Suite*',
                'assistant': '🤖 *Analysis completed using General Intelligence Suite*'
            }.get(model_id, '🔧 *Analysis completed using Professional Tools*')
            
            response += f"\n\n{tool_name}"
        
        return response
    
    def get_enhanced_system_message_for_model(self, model_id: str) -> Dict[str, str]:
        """Get enhanced system message using modular AI prompts"""
        return AIModelPrompts.get_system_prompt(model_id)
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the professional bot system"""
        logger.error(f"Professional system error: {context.error}")
        
        if isinstance(update, Update) and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="🔧 **Professional System Error**\n\n"
                         "A technical error occurred in the professional AI system.\n\n"
                         "**Recovery Options:**\n"
                         "• Use /clear to reset the system\n"
                         "• Try /start to access tools menu\n"
                         "• Switch AI experts with /models\n\n"
                         "**Status:** Professional tools are being restored",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to send professional error message: {e}")
