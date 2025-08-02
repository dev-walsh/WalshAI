
"""
Configuration management for the Telegram Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration class for bot settings"""
    
    def __init__(self):
        # Telegram Bot Configuration
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
        
        # DeepSeek API Configuration
        self.DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '').strip()
        self.DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
        self.DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        
        # Bot Configuration - Optimized for speed
        self.MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '3000'))  # Reduced for faster processing
        self.MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '6'))  # Reduced for speed
        self.REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '15'))  # Faster timeout
        self.MAX_RETRIES = int(os.getenv('MAX_RETRIES', '2'))  # Fewer retries for speed
        
        # Rate Limiting
        self.RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '20'))
        self.RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
        
        # Logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # AI Models Configuration - Professional Suite
        self.AI_MODELS = {
            'financial': {
                'name': 'Financial Investigation Expert',
                'emoji': '🔍',
                'description': 'Advanced financial investigations, AML compliance, fraud detection with professional tools',
                'tools': ['Transaction Analysis', 'AML Risk Assessment', 'Entity Investigation', 'Fund Tracing', 'Pattern Detection', 'Compliance Reporting']
            },
            'assistant': {
                'name': 'General Intelligence Expert',
                'emoji': '🤖',
                'description': 'Comprehensive AI assistant with professional analysis capabilities',
                'tools': ['Research Analysis', 'Document Creation', 'Problem Solving', 'Strategic Planning', 'Quality Assurance']
            },
            'property': {
                'name': 'Property Development Expert',
                'emoji': '🏗️',
                'description': 'International property development, investment analysis, and market intelligence',
                'tools': ['ROI Calculator', 'Market Analysis', 'Feasibility Studies', 'Cost Estimation', 'Investment Planning']
            },
            'cloner': {
                'name': 'Company Intelligence Expert',
                'emoji': '🏢',
                'description': 'Complete business intelligence, company analysis, and competitive research',
                'tools': ['Company Analysis', 'Business Model Breakdown', 'Competitive Intelligence', 'Legal Structure Analysis', 'Market Positioning']
            },
            'marketing': {
                'name': 'Marketing Intelligence Expert',
                'emoji': '📈',
                'description': 'Advanced marketing analytics, luxury campaigns, and international strategies',
                'tools': ['Campaign Strategy', 'Audience Analysis', 'Performance Analytics', 'Luxury Marketing', 'International Campaigns']
            },
            'scam_search': {
                'name': 'Scam Intelligence Expert',
                'emoji': '🚨',
                'description': 'Advanced fraud detection, scam analysis, and security assessment',
                'tools': ['Scam Detection', 'Risk Assessment', 'Fraud Analysis', 'Protection Strategies', 'Investigation Support']
            },
            'profile_gen': {
                'name': 'Profile Generation Expert',
                'emoji': '🆔',
                'description': 'Professional testing data creation with UK identity profile generation',
                'tools': ['UK Profile Generation', 'Document Creation', 'Address Generation', 'Contact Details', 'Business Profiles']
            }
        }
        
        # Professional Tool Configuration
        self.PROFESSIONAL_FEATURES = {
            'financial_suite': True,
            'property_tools': True,
            'company_intelligence': True,
            'scam_database': True,
            'profile_generator': True,
            'marketing_analytics': True,
            'advanced_analysis': True,
            'professional_reports': True
        }
        
    def validate(self):
        """Validate required configuration"""
        errors = []
        
        if not self.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
            
        if not self.DEEPSEEK_API_KEY:
            errors.append("DEEPSEEK_API_KEY is required")
            
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
