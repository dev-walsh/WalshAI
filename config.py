
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
        
        # Bot Configuration
        self.MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '4000'))
        self.MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '10'))
        self.REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
        
        # Rate Limiting
        self.RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '20'))
        self.RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
        
        # Logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # AI Models Configuration
        self.AI_MODELS = {
            'financial': {
                'name': 'Financial Investigator',
                'emoji': '🔍',
                'description': 'Specialized in financial investigations, fraud detection, and compliance'
            },
            'assistant': {
                'name': 'General Assistant',
                'emoji': '🤖',
                'description': 'General purpose AI assistant for everyday tasks'
            },
            'property': {
                'name': 'Property Development Expert',
                'emoji': '🏗️',
                'description': 'Specialized in foreign property development, investment, and sales'
            },
            'cloner': {
                'name': 'Company Cloner',
                'emoji': '🏢',
                'description': 'Creates comprehensive company profiles and business structure analysis'
            },
            'marketing': {
                'name': 'Marketing Specialist',
                'emoji': '📈',
                'description': 'Expert in property marketing, sales strategies, and investment promotion'
            },
            'scam_search': {
                'name': 'Scam Investigator',
                'emoji': '🚨',
                'description': 'Specialized in identifying and explaining various scam methodologies'
            },
            'profile_gen': {
                'name': 'Profile Generator',
                'emoji': '🆔',
                'description': 'Generates realistic UK identity profiles for testing purposes'
            }
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
