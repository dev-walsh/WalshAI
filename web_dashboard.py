"""
Enhanced Web Dashboard for Telegram Bot Management with AI Model Support
Optimized for Windows compatibility and improved performance
"""

import logging
import json
import os
import threading
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
from collections import defaultdict, deque
from typing import Dict, List, Any
from csv_exporter import CSVExporter
from communication_tools import CommunicationSuite

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
        
        # Initialize CSV exporter and communication tools
        self.csv_exporter = CSVExporter()
        self.communication_suite = CommunicationSuite()

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

        @self.app.route('/api/investigations')
        def api_investigations():
            """Get financial investigations data"""
            try:
                investigations = []
                
                # Generate investigations from message logs with investigation queries
                investigation_messages = [m for m in self.message_logs if m.get('is_investigation')]
                
                for i, msg in enumerate(investigation_messages[-20:]):  # Last 20 investigations
                    investigations.append({
                        'id': f"inv_{i+1}",
                        'type': 'Financial Investigation',
                        'status': 'Completed',
                        'created': msg.get('timestamp', datetime.now().isoformat()),
                        'summary': f"Investigation query: {msg.get('message', '')[:100]}...",
                        'user_id': msg.get('user_id'),
                        'ai_model': msg.get('ai_model', 'financial'),
                        'response_time': msg.get('response_time', 0)
                    })
                
                # If no real investigations, add some sample data to show the feature works
                if not investigations:
                    investigations = [
                        {
                            'id': 'sample_1',
                            'type': 'AML Compliance Check',
                            'status': 'Ready',
                            'created': datetime.now().isoformat(),
                            'summary': 'System ready for financial investigations. Send investigation queries to generate real data.'
                        }
                    ]
                
                return jsonify({
                    'investigations': investigations,
                    'total': len(investigations)
                })
            except Exception as e:
                logger.error(f"Investigations API error: {e}")
                return jsonify({'investigations': [], 'total': 0})

        @self.app.route('/api/company-clones')
        def api_company_clones():
            """Get company analysis data"""
            try:
                companies = []
                if hasattr(self.bot_handlers, 'company_profiles'):
                    for comp_id, comp_data in self.bot_handlers.company_profiles.items():
                        companies.append({
                            'id': comp_id,
                            'name': comp_data.get('company_name', 'Unknown Company'),
                            'type': comp_data.get('business_type', 'Unknown'),
                            'industry': comp_data.get('industry', 'Unknown'),
                            'created': comp_data.get('created', datetime.now().isoformat())
                        })
                
                return jsonify({
                    'companies': companies,
                    'total': len(companies)
                })
            except Exception as e:
                logger.error(f"Company clones API error: {e}")
                return jsonify({'companies': [], 'total': 0})

        @self.app.route('/api/scams')
        def api_scams():
            """Get scam analysis data"""
            try:
                scams = []
                scam_messages = [m for m in self.message_logs if m.get('is_scam')]
                
                for i, message in enumerate(scam_messages):
                    scams.append({
                        'id': f"scam_{i+1}",
                        'type': 'Scam Analysis',
                        'message': message.get('message', '')[:200],
                        'timestamp': message.get('timestamp'),
                        'user_id': message.get('user_id'),
                        'risk_level': 'High',
                        'ai_model': message.get('ai_model', 'scam_search')
                    })
                
                # Add sample if no real scam analyses
                if not scams:
                    scams = [{
                        'id': 'sample_1',
                        'type': 'Scam Detection System',
                        'message': 'System ready for scam analysis. Send suspicious content to generate real data.',
                        'timestamp': datetime.now().isoformat(),
                        'user_id': 0,
                        'risk_level': 'Info'
                    }]
                
                return jsonify({
                    'scams': scams,
                    'total': len(scams)
                })
            except Exception as e:
                logger.error(f"Scams API error: {e}")
                return jsonify({'scams': [], 'total': 0})

        @self.app.route('/api/profiles')
        def api_profiles():
            """Get generated profiles data"""
            try:
                profiles = []
                profile_messages = [m for m in self.message_logs if m.get('is_profile')]
                
                # Get profiles from bot handlers if available
                if hasattr(self.bot_handlers, 'generated_profiles'):
                    for prof_id, prof_data in self.bot_handlers.generated_profiles.items():
                        profiles.append({
                            'id': prof_id,
                            'name': prof_data.get('name', 'Unknown'),
                            'type': 'UK Profile',
                            'created': prof_data.get('generated_at', datetime.now().isoformat()),
                            'postcode': prof_data.get('postcode', 'N/A'),
                            'age': prof_data.get('age', 'N/A'),
                            'city': prof_data.get('city', 'N/A')
                        })
                
                # If no stored profiles, show sample data
                if not profiles:
                    profiles = [{
                        'id': 'sample_1',
                        'name': 'Profile Generator Ready',
                        'type': 'UK Profile System',
                        'created': datetime.now().isoformat(),
                        'postcode': 'System Ready',
                        'age': 'N/A',
                        'city': 'Use profile generation commands to create real data'
                    }]
                
                return jsonify({
                    'profiles': profiles,
                    'total': len(profiles)
                })
            except Exception as e:
                logger.error(f"Profiles API error: {e}")
                return jsonify({'profiles': [], 'total': 0})

        @self.app.route('/api/clone-company', methods=['POST'])
        def api_clone_company():
            """Handle company information lookup with real Companies House data"""
            try:
                from companies_house_api import CompaniesHouseAPI
                
                data = request.get_json()
                company_name = data.get('company_name', data.get('company', 'Unknown Company'))
                
                if not company_name or company_name.strip() == '':
                    return jsonify({'success': False, 'error': 'Company name is required'}), 400
                
                # Use real Companies House API
                companies_house = CompaniesHouseAPI()
                company_info = companies_house.lookup_company_comprehensive(company_name)
                
                # Store the real company info
                if company_info.get('success') and hasattr(self.bot_handlers, 'company_profiles'):
                    clone_id = len(self.bot_handlers.company_profiles) + 1
                    self.bot_handlers.company_profiles[clone_id] = {
                        'company_name': company_info.get('company_name', company_name),
                        'company_number': company_info.get('company_number', ''),
                        'business_type': company_info.get('company_type', 'Unknown'),
                        'industry': company_info.get('industry', 'Unknown'),
                        'created': datetime.now().isoformat(),
                        'status': company_info.get('company_status', 'Unknown'),
                        'full_info': company_info
                    }
                
                return jsonify(company_info)
                
            except ImportError:
                logger.error("Companies House API module not available")
                return jsonify({
                    'success': False,
                    'error': 'Companies House API integration not available',
                    'company_name': company_name
                }), 500
            except Exception as e:
                logger.error(f"Company lookup API error: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'company_name': company_name if 'company_name' in locals() else 'Unknown'
                }), 500

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

        @self.app.route('/api/export/<data_type>')
        def api_export_data(data_type):
            """Export data to CSV format"""
            try:
                export_file = None
                
                if data_type == 'messages':
                    export_file = self.csv_exporter.export_messages_to_csv(list(self.message_logs))
                elif data_type == 'users':
                    export_file = self.csv_exporter.export_users_to_csv(dict(self.user_stats))
                elif data_type == 'investigations':
                    investigations = self._get_investigations_data()
                    export_file = self.csv_exporter.export_investigations_to_csv(investigations)
                elif data_type == 'companies':
                    companies = self._get_companies_data()
                    export_file = self.csv_exporter.export_companies_to_csv(companies)
                elif data_type == 'scams':
                    scams = self._get_scams_data()
                    export_file = self.csv_exporter.export_scams_to_csv(scams)
                elif data_type == 'profiles':
                    profiles = self._get_profiles_data()
                    export_file = self.csv_exporter.export_profiles_to_csv(profiles)
                else:
                    return jsonify({'error': 'Invalid data type'}), 400
                
                if export_file and os.path.exists(export_file):
                    return send_file(
                        export_file,
                        as_attachment=True,
                        download_name=os.path.basename(export_file),
                        mimetype='text/csv'
                    )
                else:
                    return jsonify({'error': 'Export failed'}), 500
                    
            except Exception as e:
                logger.error(f"Export error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/export-files')
        def api_export_files():
            """Get list of available export files"""
            try:
                files = self.csv_exporter.get_export_files()
                return jsonify({'files': files})
            except Exception as e:
                logger.error(f"Export files error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/download-export/<filename>')
        def api_download_export(filename):
            """Download a specific export file"""
            try:
                file_path = os.path.join(self.csv_exporter.export_dir, filename)
                if os.path.exists(file_path) and filename.endswith('.csv'):
                    return send_file(
                        file_path,
                        as_attachment=True,
                        download_name=filename,
                        mimetype='text/csv'
                    )
                else:
                    return jsonify({'error': 'File not found'}), 404
            except Exception as e:
                logger.error(f"Download error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/phishing-analysis', methods=['POST'])
        def api_phishing_analysis():
            """Analyze message for phishing threats"""
            try:
                data = request.get_json()
                message = data.get('message', '')
                sender_email = data.get('sender_email', '')
                headers = data.get('headers', {})
                
                if not message:
                    return jsonify({'error': 'Message is required'}), 400
                
                analysis = self.communication_suite.analyze_phishing_comprehensive(
                    message, sender_email, headers
                )
                
                return jsonify(analysis)
                
            except Exception as e:
                logger.error(f"Phishing analysis error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/mass-email', methods=['POST'])
        def api_mass_email():
            """Send mass email campaign"""
            try:
                data = request.get_json()
                
                required_fields = ['smtp_config', 'sender_email', 'sender_password', 'recipients', 'subject', 'body']
                if not all(field in data for field in required_fields):
                    return jsonify({'error': 'Missing required fields'}), 400
                
                results = self.communication_suite.mass_emailer.send_mass_email(
                    smtp_config=data['smtp_config'],
                    sender_email=data['sender_email'],
                    sender_password=data['sender_password'],
                    recipients=data['recipients'],
                    subject=data['subject'],
                    body=data['body'],
                    is_html=data.get('is_html', False),
                    attachments=data.get('attachments', [])
                )
                
                return jsonify(results)
                
            except Exception as e:
                logger.error(f"Mass email error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/sms-gateway', methods=['POST'])
        def api_sms_gateway():
            """Send SMS through email gateway"""
            try:
                data = request.get_json()
                
                required_fields = ['smtp_config', 'sender_email', 'sender_password', 'phone_number', 'carrier', 'message']
                if not all(field in data for field in required_fields):
                    return jsonify({'error': 'Missing required fields'}), 400
                
                result = self.communication_suite.sms_gateway.send_sms_via_email(
                    smtp_config=data['smtp_config'],
                    sender_email=data['sender_email'],
                    sender_password=data['sender_password'],
                    phone_number=data['phone_number'],
                    carrier=data['carrier'],
                    message=data['message']
                )
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"SMS gateway error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/bulk-sms', methods=['POST'])
        def api_bulk_sms():
            """Send bulk SMS messages"""
            try:
                data = request.get_json()
                
                required_fields = ['smtp_config', 'sender_email', 'sender_password', 'recipients', 'message']
                if not all(field in data for field in required_fields):
                    return jsonify({'error': 'Missing required fields'}), 400
                
                results = self.communication_suite.sms_gateway.send_bulk_sms(
                    smtp_config=data['smtp_config'],
                    sender_email=data['sender_email'],
                    sender_password=data['sender_password'],
                    recipients=data['recipients'],
                    message=data['message']
                )
                
                return jsonify(results)
                
            except Exception as e:
                logger.error(f"Bulk SMS error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/communication-logs')
        def api_communication_logs():
            """Get communication activity logs"""
            try:
                logs = self.communication_suite.communication_logs[-100:]  # Last 100 logs
                return jsonify({'logs': logs, 'total': len(logs)})
            except Exception as e:
                logger.error(f"Communication logs error: {e}")
                return jsonify({'error': str(e)}), 500

        # Error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint not found'}), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {error}")
            return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/messages')
        def get_messages():
            """Get conversation messages with enhanced formatting"""
            try:
                messages = []
                # Use message_logs from dashboard instead of bot_handlers conversations
                for i, log_entry in enumerate(list(self.message_logs)[-50:]):
                    messages.append({
                        'id': f"msg_{i}",
                        'user_id': log_entry.get('user_id', 0),
                        'username': log_entry.get('username', 'Unknown'),
                        'message': log_entry.get('message', '')[:200] + ('...' if len(log_entry.get('message', '')) > 200 else ''),
                        'response': log_entry.get('response', '')[:200] + ('...' if len(log_entry.get('response', '')) > 200 else ''),
                        'role': 'user',
                        'timestamp': log_entry.get('timestamp', datetime.now().isoformat()),
                        'ai_model': log_entry.get('ai_model', 'Unknown'),
                        'model_emoji': '🤖',
                        'response_time': log_entry.get('response_time', 0)
                    })

                # Sort by most recent
                messages.sort(key=lambda x: x['timestamp'], reverse=True)
                return jsonify(messages)
            except Exception as e:
                logger.error(f"Error getting messages: {e}")
                return jsonify({'error': str(e), 'messages': []})

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
    
    def _get_investigations_data(self) -> List[Dict]:
        """Get investigations data for export"""
        investigations = []
        investigation_messages = [m for m in self.message_logs if m.get('is_investigation')]
        
        for i, msg in enumerate(investigation_messages):
            investigations.append({
                'id': f"inv_{i+1}",
                'type': 'Financial Investigation',
                'status': 'Completed',
                'created': msg.get('timestamp', datetime.now().isoformat()),
                'summary': f"Investigation query: {msg.get('message', '')[:100]}...",
                'user_id': msg.get('user_id'),
                'ai_model': msg.get('ai_model', 'financial'),
                'response_time': msg.get('response_time', 0)
            })
        return investigations
    
    def _get_companies_data(self) -> List[Dict]:
        """Get company data for export"""
        companies = []
        if hasattr(self.bot_handlers, 'company_profiles'):
            for comp_id, comp_data in self.bot_handlers.company_profiles.items():
                companies.append({
                    'id': comp_id,
                    'name': comp_data.get('company_name', 'Unknown Company'),
                    'type': comp_data.get('business_type', 'Unknown'),
                    'industry': comp_data.get('industry', 'Unknown'),
                    'created': comp_data.get('created', datetime.now().isoformat()),
                    'company_number': comp_data.get('company_number', ''),
                    'status': comp_data.get('status', 'Unknown'),
                    'registered_address': comp_data.get('registered_address', '')
                })
        return companies
    
    def _get_scams_data(self) -> List[Dict]:
        """Get scam analysis data for export"""
        scams = []
        scam_messages = [m for m in self.message_logs if m.get('is_scam')]
        
        for i, message in enumerate(scam_messages):
            scams.append({
                'id': f"scam_{i+1}",
                'type': 'Scam Analysis',
                'message': message.get('message', '')[:200],
                'timestamp': message.get('timestamp'),
                'user_id': message.get('user_id'),
                'risk_level': 'High',
                'ai_model': message.get('ai_model', 'scam_search'),
                'analysis_result': message.get('response', '')[:200]
            })
        return scams
    
    def _get_profiles_data(self) -> List[Dict]:
        """Get profile data for export"""
        profiles = []
        if hasattr(self.bot_handlers, 'generated_profiles'):
            for prof_id, prof_data in self.bot_handlers.generated_profiles.items():
                profiles.append({
                    'id': prof_id,
                    'name': prof_data.get('name', 'Unknown'),
                    'type': 'UK Profile',
                    'created': prof_data.get('generated_at', datetime.now().isoformat()),
                    'postcode': prof_data.get('postcode', 'N/A'),
                    'age': prof_data.get('age', 'N/A'),
                    'city': prof_data.get('city', 'N/A')
                })
        return profiles
    
    def _generate_realistic_business_info(self, company_name: str) -> Dict[str, str]:
        """Generate realistic business information for a company"""
        try:
            from data_generators import UKDataGenerator
            
            # Generate business profile
            business_profile = UKDataGenerator.generate_business_profile()
            contact_details = UKDataGenerator.generate_contact_details()
            
            # Use the actual company name but generate realistic supporting data
            company_number = f"{random.randint(10000000, 99999999):08d}"
            vat_number = f"GB{random.randint(100000000, 999999999)}"
            
            # Generate realistic banking details
            sort_codes = ['20-00-00', '40-47-84', '60-83-01', '11-01-00', '30-96-26', '40-05-30']
            sort_code = random.choice(sort_codes)
            account_number = f"{random.randint(10000000, 99999999):08d}"
            
            # Generate business address
            address_data = UKDataGenerator.generate_address()
            
            return {
                'company_name': company_name,
                'company_number': company_number,
                'vat_number': vat_number,
                'business_type': business_profile['business_type'],
                'industry': business_profile['industry'],
                'incorporation_date': business_profile['incorporation_date'],
                'registered_address': address_data['full'],
                'trading_address': address_data['full'],
                'directors': business_profile['directors'],
                'contact_email': contact_details['email'],
                'contact_phone': contact_details['phone'],
                'mobile': contact_details['mobile'],
                'website': f"www.{company_name.lower().replace(' ', '').replace('&', 'and')}.co.uk",
                'sort_code': sort_code,
                'account_number': account_number,
                'status': 'Active',
                'sic_code': f"{random.randint(10000, 99999)}",
                'employee_count': random.randint(1, 500),
                'annual_return_date': UKDataGenerator.generate_random_date(2023, 2024)
            }
            
        except Exception as e:
            logger.error(f"Error generating business info: {e}")
            return {
                'company_name': company_name,
                'company_number': f"{random.randint(10000000, 99999999):08d}",
                'business_type': 'Private Limited Company',
                'industry': 'Business Services',
                'registered_address': '123 Business Street, London, EC1A 1BB',
                'directors': 'John Smith',
                'contact_email': 'info@company.co.uk',
                'contact_phone': '020 7946 0958',
                'status': 'Active'
            }

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