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

        @self.app.route('/api/investigations')
        def api_investigations():
            """Get financial investigations data"""
            try:
                investigations = []
                if hasattr(self.bot_handlers, 'investigation_database'):
                    for inv_id, inv_data in self.bot_handlers.investigation_database.items():
                        investigations.append({
                            'id': inv_id,
                            'type': inv_data.get('type', 'General'),
                            'status': inv_data.get('status', 'Active'),
                            'created': inv_data.get('created', datetime.now().isoformat()),
                            'summary': inv_data.get('summary', 'Investigation in progress')
                        })
                
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
                for message in self.message_logs:
                    if message.get('is_scam'):
                        scams.append({
                            'id': len(scams) + 1,
                            'type': 'Detected Scam',
                            'message': message.get('message', '')[:200],
                            'timestamp': message.get('timestamp'),
                            'user_id': message.get('user_id'),
                            'risk_level': 'High'
                        })
                
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
                if hasattr(self.bot_handlers, 'generated_profiles'):
                    for prof_id, prof_data in self.bot_handlers.generated_profiles.items():
                        profiles.append({
                            'id': prof_id,
                            'name': prof_data.get('name', 'Unknown'),
                            'type': 'UK Profile',
                            'created': datetime.now().isoformat(),
                            'postcode': prof_data.get('address', {}).get('postcode', 'N/A') if isinstance(prof_data.get('address'), dict) else 'N/A'
                        })
                
                return jsonify({
                    'profiles': profiles,
                    'total': len(profiles)
                })
            except Exception as e:
                logger.error(f"Profiles API error: {e}")
                return jsonify({'profiles': [], 'total': 0})

        @self.app.route('/api/clone-company', methods=['POST'])
        def api_clone_company():
            """Handle company cloning requests with AI analysis"""
            try:
                data = request.get_json()
                company_name = data.get('company_name', data.get('company', 'Unknown Company'))
                
                if not company_name or company_name.strip() == '':
                    return jsonify({'success': False, 'error': 'Company name is required'}), 400
                
                # Generate AI analysis using the company expert
                if hasattr(self.bot_handlers, 'deepseek_client'):
                    analysis_prompt = [
                        {
                            "role": "system",
                            "content": "You are a Company Intelligence Expert. Analyze the given company and provide a comprehensive business model breakdown including structure, implementation plan, costs, timeline, legal considerations, and recommendations."
                        },
                        {
                            "role": "user",
                            "content": f"Analyze {company_name} and provide a complete business model analysis including: 1) Business Model, 2) Organizational Structure, 3) Implementation Plan, 4) Estimated Costs, 5) Timeline, 6) Legal Considerations, 7) Recommendations for replicating this business model."
                        }
                    ]
                    
                    ai_response = self.bot_handlers.deepseek_client.create_chat_completion(
                        analysis_prompt,
                        temperature=0.7,
                        max_tokens=1500
                    )
                    
                    if ai_response and not ai_response.startswith('❌') and not ai_response.startswith('🌐'):
                        # Parse the AI response into structured data
                        analysis_data = self._parse_company_analysis(ai_response, company_name)
                    else:
                        # Fallback analysis if AI fails
                        analysis_data = self._generate_fallback_analysis(company_name)
                else:
                    # Fallback if no AI client
                    analysis_data = self._generate_fallback_analysis(company_name)
                
                # Store the analysis in company profiles
                if hasattr(self.bot_handlers, 'company_profiles'):
                    clone_id = len(self.bot_handlers.company_profiles) + 1
                    self.bot_handlers.company_profiles[clone_id] = {
                        'company_name': company_name,
                        'business_type': analysis_data['business_model'][:100],
                        'industry': analysis_data.get('industry', 'Multiple Sectors'),
                        'created': datetime.now().isoformat(),
                        'status': 'Completed',
                        'full_analysis': analysis_data
                    }
                
                return jsonify({
                    'success': True,
                    'company_name': company_name,
                    **analysis_data
                })
                
            except Exception as e:
                logger.error(f"Clone company API error: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'company_name': company_name if 'company_name' in locals() else 'Unknown',
                    'business_model': 'Analysis failed - please try again',
                    'structure': 'Unable to analyze at this time',
                    'implementation_plan': 'Please retry the analysis',
                    'estimated_costs': 'N/A - Analysis Error',
                    'timeline': 'N/A - Analysis Error',
                    'legal_considerations': 'Consult legal professionals',
                    'recommendations': 'Please try the analysis again'
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
                if hasattr(self.bot_handlers, 'conversations'):
                    for user_id, conversation in self.bot_handlers.conversations.items():
                        username = f"user_{user_id}"
                        for i, msg in enumerate(conversation):
                            # Get AI model used (simplified lookup)
                            model_used = self.bot_handlers.user_models.get(user_id, 'assistant')
                            model_info = self.bot_handlers.config.AI_MODELS.get(model_used, {})

                            messages.append({
                                'id': f"{user_id}_{i}",
                                'user_id': user_id,
                                'username': username,
                                'content': msg.get('content', '')[:200] + ('...' if len(msg.get('content', '')) > 200 else ''),
                                'role': msg.get('role', 'user'),
                                'timestamp': datetime.now().strftime('%H:%M:%S'),
                                'ai_model': model_info.get('name', 'Unknown'),
                                'model_emoji': model_info.get('emoji', '🤖')
                            })

                # Sort by most recent and limit
                messages.sort(key=lambda x: x['timestamp'], reverse=True)
                return jsonify(messages[:50])
            except Exception as e:
                logger.error(f"Error getting messages: {e}")
                return jsonify([])

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
    
    def _parse_company_analysis(self, ai_response: str, company_name: str) -> Dict[str, str]:
        """Parse AI response into structured company analysis data"""
        try:
            # Split response into sections
            sections = {
                'business_model': 'Comprehensive business analysis',
                'structure': 'Organizational structure details',
                'implementation_plan': 'Step-by-step implementation guide',
                'estimated_costs': 'Investment and operational cost breakdown',
                'timeline': 'Project timeline and milestones',
                'legal_considerations': 'Legal and regulatory requirements',
                'recommendations': 'Strategic recommendations'
            }
            
            # Try to extract structured information from AI response
            response_lower = ai_response.lower()
            
            # Look for section headers and extract content
            for key in sections.keys():
                section_start = response_lower.find(key.replace('_', ' '))
                if section_start == -1:
                    section_start = response_lower.find(key)
                
                if section_start != -1:
                    # Find the end of this section (next section or end of text)
                    section_end = len(ai_response)
                    for other_key in sections.keys():
                        if other_key != key:
                            other_start = response_lower.find(other_key.replace('_', ' '), section_start + 1)
                            if other_start != -1 and other_start < section_end:
                                section_end = other_start
                    
                    # Extract the content
                    content = ai_response[section_start:section_end].strip()
                    # Clean up the content
                    content = content.split('\n')[1:] if '\n' in content else [content]
                    content = ' '.join([line.strip() for line in content if line.strip()])
                    
                    if content and len(content) > 20:
                        sections[key] = content[:500]  # Limit length
            
            # If parsing fails, split the response roughly
            if all(len(v) < 50 for v in sections.values()):
                paragraphs = [p.strip() for p in ai_response.split('\n\n') if p.strip()]
                if len(paragraphs) >= 6:
                    sections = {
                        'business_model': paragraphs[0][:500] if len(paragraphs) > 0 else f"{company_name} operates in multiple business sectors with diversified revenue streams.",
                        'structure': paragraphs[1][:500] if len(paragraphs) > 1 else f"{company_name} employs a hierarchical organizational structure with specialized departments.",
                        'implementation_plan': paragraphs[2][:500] if len(paragraphs) > 2 else "Phase 1: Market research and planning, Phase 2: Infrastructure setup, Phase 3: Launch and optimization.",
                        'estimated_costs': paragraphs[3][:500] if len(paragraphs) > 3 else "Initial investment: £50K-£200K, Monthly operations: £10K-£50K, depending on scale.",
                        'timeline': paragraphs[4][:500] if len(paragraphs) > 4 else "Planning: 1-3 months, Setup: 3-6 months, Launch: 6-12 months, Optimization: Ongoing.",
                        'legal_considerations': paragraphs[5][:500] if len(paragraphs) > 5 else "Company registration, licensing requirements, compliance regulations, intellectual property protection.",
                        'recommendations': paragraphs[6][:500] if len(paragraphs) > 6 else "Focus on core competencies, invest in technology, build strong partnerships, prioritize customer experience."
                    }
            
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing company analysis: {e}")
            return self._generate_fallback_analysis(company_name)
    
    def _generate_fallback_analysis(self, company_name: str) -> Dict[str, str]:
        """Generate fallback analysis when AI is unavailable"""
        return {
            'business_model': f"{company_name} operates a multi-faceted business model focusing on core services, customer acquisition, and revenue optimization through diversified channels including direct sales, partnerships, and digital platforms.",
            'structure': f"The organizational structure includes executive leadership, operational departments (marketing, sales, finance, technology), and support functions. {company_name} employs both centralized decision-making and decentralized execution.",
            'implementation_plan': "Phase 1 (Months 1-3): Market research, business registration, initial team hiring. Phase 2 (Months 4-6): Infrastructure setup, system development, pilot testing. Phase 3 (Months 7-12): Full launch, marketing campaigns, customer acquisition, scaling operations.",
            'estimated_costs': "Initial Setup: £75,000-£150,000 (registration, legal, initial inventory/systems). Monthly Operations: £15,000-£40,000 (staff, rent, marketing, utilities). Growth Investment: £50,000+ (scaling, technology, expansion).",
            'timeline': "Planning & Setup: 3-6 months, Market Entry: 6-9 months, Growth Phase: 9-18 months, Maturity & Optimization: 18+ months. Full implementation typically requires 12-24 months.",
            'legal_considerations': "Company registration (Companies House), business licensing, VAT registration, employment law compliance, data protection (GDPR), industry-specific regulations, intellectual property protection, contract management.",
            'recommendations': f"1) Conduct thorough market analysis before replicating {company_name}'s model. 2) Focus on unique value propositions. 3) Invest in technology and automation. 4) Build strong customer relationships. 5) Ensure regulatory compliance from day one. 6) Plan for scalability."
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