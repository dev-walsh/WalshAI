
"""
Web Dashboard for Telegram Bot Management
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
    """Web dashboard for monitoring bot activity"""
    
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
            'investigation_queries': 0
        })
        self.system_stats = {
            'bot_started': datetime.now(),
            'total_requests': 0,
            'errors': 0,
            'rate_limited': 0
        }
        
        self.setup_routes()
    
    def log_message(self, user_id: int, username: str, message: str, response: str, message_type: str = 'text'):
        """Log a message interaction"""
        timestamp = datetime.now()
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'user_id': user_id,
            'username': username,
            'message': message,
            'response': response,
            'type': message_type,
            'is_investigation': self.is_investigation_query(message)
        }
        
        self.message_logs.append(log_entry)
        
        # Update user stats
        user_stat = self.user_stats[user_id]
        user_stat['total_messages'] += 1
        user_stat['last_seen'] = timestamp
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
    
    def is_investigation_query(self, message: str) -> bool:
        """Check if message is related to financial investigation"""
        investigation_keywords = [
            'fraud', 'financial', 'money laundering', 'suspicious transaction',
            'bank', 'account', 'investigate', 'pattern', 'anomaly', 'compliance',
            'aml', 'kyc', 'transaction', 'payment', 'transfer', 'asset'
        ]
        return any(keyword in message.lower() for keyword in investigation_keywords)
    
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
            
            return jsonify({
                'uptime_seconds': int(uptime.total_seconds()),
                'uptime_formatted': str(uptime).split('.')[0],
                'total_requests': self.system_stats['total_requests'],
                'errors': self.system_stats['errors'],
                'rate_limited': self.system_stats['rate_limited'],
                'active_users': len(self.bot_handlers.conversations),
                'total_users': len(self.user_stats)
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
            return jsonify(investigations[-100:])  # Last 100 investigation queries
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the dashboard server"""
        self.app.run(host=host, port=port, debug=debug, threaded=True)
