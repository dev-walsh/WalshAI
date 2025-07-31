
"""
Web Dashboard for Telegram Bot Management with AI Model Support
"""

import logging
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from threading import Thread
import time
from collections import defaultdict, deque
from typing import Dict, List, Any
import os

logger = logging.getLogger(__name__)

class BotDashboard:
    """Web dashboard for monitoring bot activity with AI model management"""
    
    def __init__(self, bot_handlers):
        self.bot_handlers = bot_handlers
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
        
        # Analytics data
        self.message_logs = deque(maxlen=1000)  # Store last 1000 messages
        self.user_stats = defaultdict(lambda: {
            'total_messages': 0,
            'first_seen': None,
            'last_seen': None,
            'commands_used': defaultdict(int),
            'investigation_queries': 0,
            'current_model': 'financial',
            'model_usage': defaultdict(int)
        })
        self.system_stats = {
            'bot_started': datetime.now(),
            'total_requests': 0,
            'errors': 0,
            'rate_limited': 0,
            'model_switches': 0
        }
        
        self.setup_routes()
    
    def log_message(self, user_id: int, username: str, message: str, response: str, ai_model: str = 'financial', message_type: str = 'text'):
        """Log a message interaction with AI model info"""
        timestamp = datetime.now()
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'user_id': user_id,
            'username': username,
            'message': message,
            'response': response,
            'type': message_type,
            'ai_model': ai_model,
            'is_investigation': self.is_investigation_query(message),
            'is_property': self.is_property_query(message),
            'is_company_clone': self.is_company_clone_query(message),
            'is_scam': self.is_scam_query(message),
            'is_profile': self.is_profile_query(message)
        }
        
        self.message_logs.append(log_entry)
        
        # Update user stats
        user_stat = self.user_stats[user_id]
        user_stat['total_messages'] += 1
        user_stat['last_seen'] = timestamp
        user_stat['current_model'] = ai_model
        user_stat['model_usage'][ai_model] += 1
        
        if user_stat['first_seen'] is None:
            user_stat['first_seen'] = timestamp
        
        if message.startswith('/'):
            command = message.split()[0]
            user_stat['commands_used'][command] += 1
        
        if log_entry['is_investigation']:
            user_stat['investigation_queries'] += 1
        
        self.system_stats['total_requests'] += 1
    
    def log_error(self):
        """Log an error occurrence"""
        self.system_stats['errors'] += 1
    
    def log_rate_limit(self):
        """Log a rate limit occurrence"""
        self.system_stats['rate_limited'] += 1
    
    def log_model_switch(self):
        """Log a model switch occurrence"""
        self.system_stats['model_switches'] += 1
    
    def is_investigation_query(self, message: str) -> bool:
        """Check if message is related to financial investigation"""
        investigation_keywords = [
            'fraud', 'financial', 'money laundering', 'suspicious transaction',
            'bank', 'account', 'investigate', 'pattern', 'anomaly', 'compliance',
            'aml', 'kyc', 'transaction', 'payment', 'transfer', 'asset'
        ]
        return any(keyword in message.lower() for keyword in investigation_keywords)
    
    def is_property_query(self, message: str) -> bool:
        """Check if message is related to property development"""
        property_keywords = [
            'property', 'real estate', 'apartment', 'villa', 'construction',
            'development', 'investment', 'building', 'foreign property', 'roi'
        ]
        return any(keyword in message.lower() for keyword in property_keywords)
    
    def is_company_clone_query(self, message: str) -> bool:
        """Check if message is related to company cloning"""
        clone_keywords = [
            'company', 'business model', 'clone', 'structure', 'organization',
            'replicate', 'copy', 'analyze company', 'business analysis'
        ]
        return any(keyword in message.lower() for keyword in clone_keywords)
    
    def is_scam_query(self, message: str) -> bool:
        """Check if message is related to scam search"""
        scam_keywords = [
            'scam', 'fraud', 'phishing', 'romance scam', 'investment scam',
            'crypto scam', 'email scam', 'tech support scam', 'advance fee',
            'suspicious email', 'fake website', 'social engineering'
        ]
        return any(keyword in message.lower() for keyword in scam_keywords)
    
    def is_profile_query(self, message: str) -> bool:
        """Check if message is related to profile generation"""
        profile_keywords = [
            'profile', 'identity', 'generate', 'fake details', 'test data',
            'passport', 'national insurance', 'driving licence', 'uk id'
        ]
        return any(keyword in message.lower() for keyword in profile_keywords)
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/stats')
        def api_stats():
            """Get system statistics"""
            uptime = datetime.now() - self.system_stats['bot_started']
            
            # Model usage statistics
            model_usage = defaultdict(int)
            for user_stat in self.user_stats.values():
                for model, count in user_stat['model_usage'].items():
                    model_usage[model] += count
            
            return jsonify({
                'uptime_seconds': int(uptime.total_seconds()),
                'uptime_formatted': str(uptime).split('.')[0],
                'total_requests': self.system_stats['total_requests'],
                'errors': self.system_stats['errors'],
                'rate_limited': self.system_stats['rate_limited'],
                'model_switches': self.system_stats['model_switches'],
                'active_users': len(self.bot_handlers.conversations),
                'total_users': len(self.user_stats),
                'model_usage': dict(model_usage)
            })
        
        @self.app.route('/api/messages')
        def api_messages():
            """Get recent messages"""
            limit = request.args.get('limit', 50, type=int)
            messages = list(self.message_logs)[-limit:]
            return jsonify(messages)
        
        @self.app.route('/api/users')
        def api_users():
            """Get user statistics"""
            users = []
            for user_id, stats in self.user_stats.items():
                users.append({
                    'user_id': user_id,
                    'total_messages': stats['total_messages'],
                    'first_seen': stats['first_seen'].isoformat() if stats['first_seen'] else None,
                    'last_seen': stats['last_seen'].isoformat() if stats['last_seen'] else None,
                    'investigation_queries': stats['investigation_queries'],
                    'current_model': stats['current_model'],
                    'model_usage': dict(stats['model_usage']),
                    'commands_used': dict(stats['commands_used'])
                })
            return jsonify(users)
        
        @self.app.route('/api/investigations')
        def api_investigations():
            """Get investigation-related queries"""
            investigations = [
                msg for msg in self.message_logs 
                if msg['is_investigation']
            ]
            return jsonify(investigations[-100:])
        
        @self.app.route('/api/property')
        def api_property():
            """Get property development queries"""
            property_queries = [
                msg for msg in self.message_logs 
                if msg['is_property']
            ]
            return jsonify(property_queries[-100:])
        
        @self.app.route('/api/company-clones')
        def api_company_clones():
            """Get company cloning queries"""
            clone_queries = [
                msg for msg in self.message_logs 
                if msg['is_company_clone']
            ]
            return jsonify(clone_queries[-100:])
        
        @self.app.route('/api/scams')
        def api_scams():
            """Get scam search queries"""
            scam_queries = [
                msg for msg in self.message_logs 
                if msg['is_scam']
            ]
            return jsonify(scam_queries[-100:])
        
        @self.app.route('/api/profiles')
        def api_profiles():
            """Get profile generation queries"""
            profile_queries = [
                msg for msg in self.message_logs 
                if msg['is_profile']
            ]
            return jsonify(profile_queries[-100:])
        
        @self.app.route('/api/models')
        def api_models():
            """Get AI model information"""
            return jsonify(self.bot_handlers.config.AI_MODELS)
        
        @self.app.route('/api/user-models')
        def api_user_models():
            """Get current user model selections"""
            user_models = {}
            for user_id, model_id in self.bot_handlers.user_models.items():
                user_models[str(user_id)] = {
                    'model_id': model_id,
                    'model_name': self.bot_handlers.config.AI_MODELS[model_id]['name'],
                    'model_emoji': self.bot_handlers.config.AI_MODELS[model_id]['emoji']
                }
            return jsonify(user_models)
        
        @self.app.route('/api/clone-company', methods=['POST'])
        def api_clone_company():
            """API endpoint for company cloning analysis"""
            data = request.get_json()
            company_name = data.get('company_name', '').strip()
            
            if not company_name:
                return jsonify({'error': 'Company name is required'}), 400
            
            # This would integrate with the company cloner AI model
            # For now, return a structured response template
            clone_analysis = {
                'company_name': company_name,
                'analysis_timestamp': datetime.now().isoformat(),
                'business_model': f'Analysis for {company_name} business model',
                'structure': f'Organizational structure breakdown for {company_name}',
                'implementation_plan': f'Implementation roadmap for replicating {company_name}',
                'estimated_costs': f'Cost analysis for {company_name} clone',
                'timeline': f'Timeline estimate for {company_name} replication',
                'legal_considerations': f'Legal requirements for {company_name} type business',
                'recommendations': f'Strategic recommendations for {company_name} clone'
            }
            
            return jsonify(clone_analysis)
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the dashboard server"""
        self.app.run(host=host, port=port, debug=debug, threaded=True)
