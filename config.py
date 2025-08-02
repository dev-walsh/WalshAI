
"""
Configuration management for the Telegram Bot with enhanced validation
"""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    """Enhanced configuration class with validation and type safety"""
    
    def __init__(self):
        # Core API Configuration
        self.TELEGRAM_BOT_TOKEN = self._get_env_var('TELEGRAM_BOT_TOKEN', required=True)
        self.DEEPSEEK_API_KEY = self._get_env_var('DEEPSEEK_API_KEY', required=True)
        self.DEEPSEEK_API_URL = self._get_env_var(
            'DEEPSEEK_API_URL', 
            'https://api.deepseek.com/v1/chat/completions'
        )
        self.DEEPSEEK_MODEL = self._get_env_var('DEEPSEEK_MODEL', 'deepseek-chat')
        
        # Companies House API Configuration
        self.COMPANIES_HOUSE_API_KEY = self._get_env_var('COMPANIES_HOUSE_API_KEY', '')
        
        # Performance Configuration
        self.MAX_MESSAGE_LENGTH = self._get_env_int('MAX_MESSAGE_LENGTH', 3000)
        self.MAX_CONVERSATION_HISTORY = self._get_env_int('MAX_CONVERSATION_HISTORY', 6)
        self.REQUEST_TIMEOUT = self._get_env_int('REQUEST_TIMEOUT', 60)
        self.MAX_RETRIES = self._get_env_int('MAX_RETRIES', 2)
        
        # Rate Limiting Configuration
        self.RATE_LIMIT_REQUESTS = self._get_env_int('RATE_LIMIT_REQUESTS', 20)
        self.RATE_LIMIT_WINDOW = self._get_env_int('RATE_LIMIT_WINDOW', 60)
        
        # Security Configuration
        self.REQUIRED_PASSCODE = self._get_env_var('REQUIRED_PASSCODE', '5015')
        
        # Logging Configuration
        self.LOG_LEVEL = self._get_env_var('LOG_LEVEL', 'INFO')
        
        # Web Dashboard Configuration
        self.DASHBOARD_HOST = self._get_env_var('DASHBOARD_HOST', '0.0.0.0')
        self.DASHBOARD_PORT = self._get_env_int('DASHBOARD_PORT', 5000)
        
        # AI Models Configuration
        self._configure_ai_models()
        
        # Professional Features Configuration
        self._configure_professional_features()
        
        # Validate configuration
        self.validate()
    
    def _get_env_var(self, key: str, default: str = '', required: bool = False) -> str:
        """Get environment variable with validation"""
        value = os.getenv(key, default).strip()
        if required and not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _get_env_int(self, key: str, default: int) -> int:
        """Get integer environment variable with validation"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default
    
    def _configure_ai_models(self):
        """Configure AI models with enhanced descriptions"""
        self.AI_MODELS = {
            'financial': {
                'name': 'Financial Investigation Expert',
                'emoji': '🔍',
                'description': 'Advanced financial investigations, AML compliance, fraud detection',
                'tools': ['Transaction Analysis', 'AML Risk Assessment', 'Entity Investigation', 'Fund Tracing', 'Pattern Detection']
            },
            'assistant': {
                'name': 'General Intelligence Expert',
                'emoji': '🤖',
                'description': 'Comprehensive AI assistant with professional analysis capabilities',
                'tools': ['Research Analysis', 'Document Creation', 'Problem Solving', 'Strategic Planning']
            },
            'property': {
                'name': 'Property Development Expert',
                'emoji': '🏗️',
                'description': 'International property development, investment analysis, market intelligence',
                'tools': ['ROI Calculator', 'Market Analysis', 'Feasibility Studies', 'Cost Estimation']
            },
            'cloner': {
                'name': 'Company Intelligence Expert',
                'emoji': '🏢',
                'description': 'Complete business intelligence, company analysis, competitive research',
                'tools': ['Company Analysis', 'Business Model Breakdown', 'Competitive Intelligence', 'Legal Structure']
            },
            'marketing': {
                'name': 'Marketing Intelligence Expert',
                'emoji': '📈',
                'description': 'Advanced marketing analytics, luxury campaigns, international strategies',
                'tools': ['Campaign Strategy', 'Audience Analysis', 'Performance Analytics', 'Luxury Marketing']
            },
            'scam_search': {
                'name': 'Scam Intelligence Expert',
                'emoji': '🚨',
                'description': 'Advanced fraud detection, scam analysis, security assessment',
                'tools': ['Scam Detection', 'Risk Assessment', 'Fraud Analysis', 'Protection Strategies']
            },
            'profile_gen': {
                'name': 'Profile Generation Expert',
                'emoji': '🆔',
                'description': 'Professional testing data creation with UK identity profiles',
                'tools': ['UK Profile Generation', 'Document Creation', 'Address Generation', 'Contact Details']
            }
        }
    
    def _configure_professional_features(self):
        """Configure professional feature flags"""
        self.PROFESSIONAL_FEATURES = {
            'financial_suite': True,
            'property_tools': True,
            'company_intelligence': True,
            'scam_database': True,
            'profile_generator': True,
            'marketing_analytics': True,
            'advanced_analysis': True,
            'professional_reports': True,
            'web_dashboard': True
        }
    
    def validate(self) -> bool:
        """Validate configuration with detailed error reporting"""
        errors = []
        
        if not self.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
            
        if not self.DEEPSEEK_API_KEY:
            errors.append("DEEPSEEK_API_KEY is required")
        
        # Validate numeric ranges
        if self.MAX_MESSAGE_LENGTH < 100:
            errors.append("MAX_MESSAGE_LENGTH must be at least 100")
        
        if self.MAX_CONVERSATION_HISTORY < 1:
            errors.append("MAX_CONVERSATION_HISTORY must be at least 1")
        
        if self.REQUEST_TIMEOUT < 5:
            errors.append("REQUEST_TIMEOUT must be at least 5 seconds")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        logger.info("Configuration validation successful")
        return True
    
    def get_model_config(self, model_id: str) -> Dict[str, Any]:
        """Get configuration for a specific AI model"""
        return self.AI_MODELS.get(model_id, self.AI_MODELS['assistant'])
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a professional feature is enabled"""
        return self.PROFESSIONAL_FEATURES.get(feature, False)
