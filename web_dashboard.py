
"""
Enhanced Web Dashboard for Telegram Bot Management with AI Model Support
Optimized for Windows compatibility and improved performance
"""

import logging
import json
import os
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, send_from_directory
from collections import defaultdict, deque
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class BotDashboard:
    """Enhanced web dashboard with improved performance and Windows compatibility"""
    
    def __init__(self, bot_handlers):
        self.bot_handlers = bot_handlers
        self.app = Flask(__name__, 
                        static_folder='templates/static',
                        template_folder='templates')
        
        # Enhanced security for Windows environments
        self.app.secret_key = os.urandom(24)
        self.app.config['JSON_SORT_KEYS'] = False
        self.app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
        
        # Analytics data with optimized storage
        self.message_logs = deque(maxlen=2000)  # Increased capacity
        self.user_stats = defaultdict(lambda: {
            'total_messages': 0,
            'first_seen': None,
            'last_seen': None,
            'commands_used': defaultdict(int),
            'investigation_queries': 0,
            'current_model': 'financial',
            'model_usage': defaultdict(int),
            'session_count': 0,
            'avg_response_time': 0.0
        })
        
        self.system_stats = {
            'bot_started': datetime.now(),
            'total_requests': 0,
            'errors': 0,
            'rate_limited': 0,
            'model_switches': 0,
            'uptime_seconds': 0,
            'memory_usage': 0.0,
            'performance_score': 100.0
        }
        
        # Performance monitoring
        self.performance_metrics = {
            'avg_response_time': 0.0,
            'total_response_time': 0.0,
            'response_count': 0,
            'error_rate': 0.0,
            'requests_per_minute': 0.0
        }
        
        self.setup_routes()
        logger.info("Enhanced dashboard initialized for Windows environment")
    
    def log_message(self, user_id: int, username: str, message: str, response: str, 
                   ai_model: str = 'financial', message_type: str = 'text', 
                   response_time: float = 0.0):
        """Enhanced message logging with performance metrics"""
        timestamp = datetime.now()
        
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'user_id': user_id,
            'username': username or f"user_{user_id}",
            'message': message[:500],  # Truncate for performance
            'response': response[:1000],  # Truncate for performance
            'type': message_type,
            'ai_model': ai_model,
            'response_time': response_time,
            'message_length': len(message),
            'response_length': len(response),
            'is_investigation': self._is_investigation_query(message),
            'is_property': self._is_property_query(message),
            'is_company_clone': self._is_company_clone_query(message),
            'is_scam': self._is_scam_query(message),
            'is_profile': self._is_profile_query(message)
        }
        
        self.message_logs.append(log_entry)
        
        # Update user stats with enhanced metrics
        user_stat = self.user_stats[user_id]
        user_stat['total_messages'] += 1
        user_stat['last_seen'] = timestamp
        user_stat['current_model'] = ai_model
        user_stat['model_usage'][ai_model] += 1
        
        if user_stat['first_seen'] is None:
            user_stat['first_seen'] = timestamp
        
        # Update performance metrics
        if response_time > 0:
            self._update_performance_metrics(response_time)
        
        # Command tracking
        if message.startswith('/'):
            command = message.split()[0]
            user_stat['commands_used'][command] += 1
        
        # Query type tracking
        if log_entry['is_investigation']:
            user_stat['investigation_queries'] += 1
        
        self.system_stats['total_requests'] += 1
        
        logger.debug(f"Message logged for user {user_id} with model {ai_model}")
    
    def _update_performance_metrics(self, response_time: float):
        """Update performance metrics efficiently"""
        self.performance_metrics['total_response_time'] += response_time
        self.performance_metrics['response_count'] += 1
        self.performance_metrics['avg_response_time'] = (
            self.performance_metrics['total_response_time'] / 
            self.performance_metrics['response_count']
        )
    
    def _is_investigation_query(self, message: str) -> bool:
        """Optimized investigation query detection"""
        keywords = ['fraud', 'financial', 'money laundering', 'suspicious', 
                   'bank', 'account', 'investigate', 'aml', 'kyc', 'transaction']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)
    
    def _is_property_query(self, message: str) -> bool:
        """Optimized property query detection"""
        keywords = ['property', 'real estate', 'apartment', 'villa', 
                   'construction', 'development', 'investment', 'building', 'roi']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)
    
    def _is_company_clone_query(self, message: str) -> bool:
        """Optimized company query detection"""
        keywords = ['company', 'business model', 'clone', 'structure', 
                   'organization', 'replicate', 'analyze company']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)
    
    def _is_scam_query(self, message: str) -> bool:
        """Optimized scam query detection"""
        keywords = ['scam', 'fraud', 'phishing', 'romance scam', 
                   'investment scam', 'crypto scam', 'suspicious email']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)
    
    def _is_profile_query(self, message: str) -> bool:
        """Optimized profile query detection"""
        keywords = ['profile', 'identity', 'generate', 'fake details', 
                   'test data', 'passport', 'uk id']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)
    
    def log_error(self):
        """Log system error with performance impact"""
        self.system_stats['errors'] += 1
        self.performance_metrics['error_rate'] = (
            self.system_stats['errors'] / 
            max(self.system_stats['total_requests'], 1)
        )
    
    def log_rate_limit(self):
        """Log rate limit occurrence"""
        self.system_stats['rate_limited'] += 1
    
    def log_model_switch(self):
        """Log model switch with analytics"""
        self.system_stats['model_switches'] += 1
    
    def setup_routes(self):
        """Setup Flask routes with enhanced error handling"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            try:
                return render_template('dashboard.html')
            except Exception as e:
                logger.error(f"Dashboard template error: {e}")
                return jsonify({'error': 'Dashboard template not found'}), 500
        
        @self.app.route('/api/stats')
        def api_stats():
            """Enhanced system statistics with performance metrics"""
            try:
                uptime = datetime.now() - self.system_stats['bot_started']
                
                # Calculate model usage statistics
                model_usage = defaultdict(int)
                for user_stat in self.user_stats.values():
                    for model, count in user_stat['model_usage'].items():
                        model_usage[model] += count
                
                # Calculate performance score
                performance_score = self._calculate_performance_score()
                
                stats = {
                    'uptime_seconds': int(uptime.total_seconds()),
                    'uptime_formatted': str(uptime).split('.')[0],
                    'total_requests': self.system_stats['total_requests'],
                    'errors': self.system_stats['errors'],
                    'rate_limited': self.system_stats['rate_limited'],
                    'model_switches': self.system_stats['model_switches'],
                    'active_users': len(getattr(self.bot_handlers, 'conversations', {})),
                    'total_users': len(self.user_stats),
                    'model_usage': dict(model_usage),
                    'performance_metrics': {
                        'avg_response_time': round(self.performance_metrics['avg_response_time'], 2),
                        'error_rate': round(self.performance_metrics['error_rate'] * 100, 2),
                        'performance_score': round(performance_score, 1),
                        'requests_per_minute': self._calculate_requests_per_minute()
                    },
                    'memory_usage': self._get_memory_usage(),
                    'deepseek_stats': self._get_deepseek_stats()
                }
                
                return jsonify(stats)
                
            except Exception as e:
                logger.error(f"Stats API error: {e}")
                return jsonify({'error': 'Failed to generate stats'}), 500
        
        @self.app.route('/api/messages')
        def api_messages():
            """Get recent messages with pagination"""
            try:
                limit = min(request.args.get('limit', 50, type=int), 200)
                offset = request.args.get('offset', 0, type=int)
                
                messages = list(self.message_logs)
                total = len(messages)
                
                # Apply pagination
                start_idx = max(0, total - limit - offset)
                end_idx = max(0, total - offset)
                paginated_messages = messages[start_idx:end_idx]
                
                return jsonify({
                    'messages': paginated_messages,
                    'total': total,
                    'limit': limit,
                    'offset': offset,
                    'has_more': start_idx > 0
                })
                
            except Exception as e:
                logger.error(f"Messages API error: {e}")
                return jsonify({'error': 'Failed to retrieve messages'}), 500
        
        @self.app.route('/api/users')
        def api_users():
            """Enhanced user statistics"""
            try:
                users = []
                for user_id, stats in self.user_stats.items():
                    user_data = {
                        'user_id': user_id,
                        'total_messages': stats['total_messages'],
                        'first_seen': stats['first_seen'].isoformat() if stats['first_seen'] else None,
                        'last_seen': stats['last_seen'].isoformat() if stats['last_seen'] else None,
                        'investigation_queries': stats['investigation_queries'],
                        'current_model': stats['current_model'],
                        'model_usage': dict(stats['model_usage']),
                        'commands_used': dict(stats['commands_used']),
                        'session_count': stats.get('session_count', 0),
                        'avg_response_time': stats.get('avg_response_time', 0.0)
                    }
                    users.append(user_data)
                
                # Sort by last seen
                users.sort(key=lambda x: x['last_seen'] or '', reverse=True)
                
                return jsonify({
                    'users': users,
                    'total_users': len(users),
                    'active_users': sum(1 for u in users if u['last_seen'] and 
                                      datetime.fromisoformat(u['last_seen']) > 
                                      datetime.now() - timedelta(hours=1))
                })
                
            except Exception as e:
                logger.error(f"Users API error: {e}")
                return jsonify({'error': 'Failed to retrieve user data'}), 500
        
        @self.app.route('/api/query-types')
        def api_query_types():
            """Get query type analytics"""
            try:
                query_stats = {
                    'investigations': len([m for m in self.message_logs if m.get('is_investigation')]),
                    'property': len([m for m in self.message_logs if m.get('is_property')]),
                    'company_clones': len([m for m in self.message_logs if m.get('is_company_clone')]),
                    'scams': len([m for m in self.message_logs if m.get('is_scam')]),
                    'profiles': len([m for m in self.message_logs if m.get('is_profile')])
                }
                
                return jsonify(query_stats)
                
            except Exception as e:
                logger.error(f"Query types API error: {e}")
                return jsonify({'error': 'Failed to retrieve query analytics'}), 500
        
        @self.app.route('/api/models')
        def api_models():
            """Get AI model configuration"""
            try:
                models = getattr(self.bot_handlers.config, 'AI_MODELS', {})
                return jsonify(models)
            except Exception as e:
                logger.error(f"Models API error: {e}")
                return jsonify({'error': 'Failed to retrieve model data'}), 500
        
        @self.app.route('/api/health')
        def api_health():
            """System health check endpoint"""
            try:
                health_status = {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'components': {
                        'telegram_bot': 'operational',
                        'deepseek_api': 'operational' if self._test_deepseek_connection() else 'degraded',
                        'dashboard': 'operational',
                        'database': 'operational'  # In-memory storage
                    },
                    'performance': {
                        'response_time': round(self.performance_metrics['avg_response_time'], 2),
                        'error_rate': round(self.performance_metrics['error_rate'] * 100, 2),
                        'uptime': int((datetime.now() - self.system_stats['bot_started']).total_seconds())
                    }
                }
                
                return jsonify(health_status)
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
        
        # Error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {error}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _calculate_performance_score(self) -> float:
        """Calculate system performance score"""
        try:
            base_score = 100.0
            
            # Penalize high error rates
            error_penalty = min(self.performance_metrics['error_rate'] * 50, 30)
            
            # Penalize slow response times
            response_time_penalty = min(max(self.performance_metrics['avg_response_time'] - 2.0, 0) * 10, 40)
            
            # Calculate final score
            score = max(base_score - error_penalty - response_time_penalty, 0)
            return score
            
        except Exception:
            return 100.0
    
    def _calculate_requests_per_minute(self) -> float:
        """Calculate requests per minute"""
        try:
            uptime_minutes = (datetime.now() - self.system_stats['bot_started']).total_seconds() / 60
            if uptime_minutes > 0:
                return round(self.system_stats['total_requests'] / uptime_minutes, 2)
            return 0.0
        except Exception:
            return 0.0
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics (Windows compatible)"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                'vms_mb': round(memory_info.vms / 1024 / 1024, 2),
                'percent': round(process.memory_percent(), 2)
            }
        except ImportError:
            # Fallback for systems without psutil
            return {'rss_mb': 0.0, 'vms_mb': 0.0, 'percent': 0.0}
        except Exception as e:
            logger.warning(f"Memory usage calculation failed: {e}")
            return {'rss_mb': 0.0, 'vms_mb': 0.0, 'percent': 0.0}
    
    def _get_deepseek_stats(self) -> Dict:
        """Get DeepSeek API performance statistics"""
        try:
            if hasattr(self.bot_handlers, 'deepseek_client'):
                return self.bot_handlers.deepseek_client.get_performance_stats()
            return {'total_requests': 0, 'total_errors': 0, 'average_response_time': 0.0}
        except Exception:
            return {'total_requests': 0, 'total_errors': 0, 'average_response_time': 0.0}
    
    def _test_deepseek_connection(self) -> bool:
        """Test DeepSeek API connection"""
        try:
            if hasattr(self.bot_handlers, 'deepseek_client'):
                return self.bot_handlers.deepseek_client.test_connection()
            return False
        except Exception:
            return False
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the enhanced dashboard server"""
        try:
            logger.info(f"Starting enhanced dashboard on {host}:{port}")
            
            # Windows-specific optimizations
            if os.name == 'nt':  # Windows
                threading_options = {'threaded': True, 'processes': 1}
            else:
                threading_options = {'threaded': True}
            
            self.app.run(
                host=host, 
                port=port, 
                debug=debug, 
                use_reloader=False,  # Disable reloader for stability
                **threading_options
            )
            
        except Exception as e:
            logger.error(f"Failed to start dashboard: {e}")
            raise
