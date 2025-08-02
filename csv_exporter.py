
"""
CSV Export functionality for chat data and analytics
Provides portable data export for web dashboard
"""

import csv
import os
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class CSVExporter:
    """Handles CSV export functionality for all bot data"""
    
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        self.ensure_export_directory()
    
    def ensure_export_directory(self):
        """Create export directory if it doesn't exist"""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
            logger.info(f"Created export directory: {self.export_dir}")
    
    def export_messages_to_csv(self, message_logs: List[Dict]) -> str:
        """Export message logs to CSV format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"messages_export_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'user_id', 'username', 'message', 'response',
                    'ai_model', 'response_time', 'message_length', 'response_length',
                    'is_investigation', 'is_property', 'is_company_clone', 
                    'is_scam', 'is_profile', 'type'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for message in message_logs:
                    # Clean data for CSV export
                    cleaned_message = {
                        'timestamp': message.get('timestamp', ''),
                        'user_id': message.get('user_id', ''),
                        'username': message.get('username', ''),
                        'message': str(message.get('message', '')).replace('\n', ' ').replace('\r', ' '),
                        'response': str(message.get('response', '')).replace('\n', ' ').replace('\r', ' '),
                        'ai_model': message.get('ai_model', ''),
                        'response_time': message.get('response_time', 0),
                        'message_length': message.get('message_length', 0),
                        'response_length': message.get('response_length', 0),
                        'is_investigation': message.get('is_investigation', False),
                        'is_property': message.get('is_property', False),
                        'is_company_clone': message.get('is_company_clone', False),
                        'is_scam': message.get('is_scam', False),
                        'is_profile': message.get('is_profile', False),
                        'type': message.get('type', 'text')
                    }
                    writer.writerow(cleaned_message)
            
            logger.info(f"Messages exported to CSV: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting messages to CSV: {e}")
            return None
    
    def export_users_to_csv(self, user_stats: Dict) -> str:
        """Export user statistics to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"users_export_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'user_id', 'total_messages', 'first_seen', 'last_seen',
                    'investigation_queries', 'current_model', 'model_usage',
                    'commands_used', 'session_count', 'avg_response_time'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for user_id, stats in user_stats.items():
                    user_data = {
                        'user_id': user_id,
                        'total_messages': stats.get('total_messages', 0),
                        'first_seen': stats.get('first_seen', ''),
                        'last_seen': stats.get('last_seen', ''),
                        'investigation_queries': stats.get('investigation_queries', 0),
                        'current_model': stats.get('current_model', ''),
                        'model_usage': json.dumps(dict(stats.get('model_usage', {}))),
                        'commands_used': json.dumps(dict(stats.get('commands_used', {}))),
                        'session_count': stats.get('session_count', 0),
                        'avg_response_time': stats.get('avg_response_time', 0.0)
                    }
                    writer.writerow(user_data)
            
            logger.info(f"Users exported to CSV: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting users to CSV: {e}")
            return None
    
    def export_investigations_to_csv(self, investigations: List[Dict]) -> str:
        """Export investigation data to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"investigations_export_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'type', 'status', 'created', 'summary',
                    'user_id', 'ai_model', 'response_time'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for investigation in investigations:
                    writer.writerow(investigation)
            
            logger.info(f"Investigations exported to CSV: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting investigations to CSV: {e}")
            return None
    
    def export_companies_to_csv(self, companies: List[Dict]) -> str:
        """Export company data to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"companies_export_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'name', 'type', 'industry', 'created',
                    'company_number', 'status', 'registered_address'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for company in companies:
                    writer.writerow(company)
            
            logger.info(f"Companies exported to CSV: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting companies to CSV: {e}")
            return None
    
    def export_scams_to_csv(self, scams: List[Dict]) -> str:
        """Export scam analysis data to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scams_export_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'type', 'message', 'timestamp', 'user_id',
                    'risk_level', 'ai_model', 'analysis_result'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for scam in scams:
                    cleaned_scam = {
                        'id': scam.get('id', ''),
                        'type': scam.get('type', ''),
                        'message': str(scam.get('message', '')).replace('\n', ' ').replace('\r', ' '),
                        'timestamp': scam.get('timestamp', ''),
                        'user_id': scam.get('user_id', ''),
                        'risk_level': scam.get('risk_level', ''),
                        'ai_model': scam.get('ai_model', ''),
                        'analysis_result': scam.get('analysis_result', '')
                    }
                    writer.writerow(cleaned_scam)
            
            logger.info(f"Scams exported to CSV: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting scams to CSV: {e}")
            return None
    
    def export_profiles_to_csv(self, profiles: List[Dict]) -> str:
        """Export generated profiles to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"profiles_export_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'name', 'type', 'created', 'postcode',
                    'age', 'city', 'full_data'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for profile in profiles:
                    profile_data = {
                        'id': profile.get('id', ''),
                        'name': profile.get('name', ''),
                        'type': profile.get('type', ''),
                        'created': profile.get('created', ''),
                        'postcode': profile.get('postcode', ''),
                        'age': profile.get('age', ''),
                        'city': profile.get('city', ''),
                        'full_data': json.dumps(profile) if profile else ''
                    }
                    writer.writerow(profile_data)
            
            logger.info(f"Profiles exported to CSV: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting profiles to CSV: {e}")
            return None
    
    def get_export_files(self) -> List[Dict[str, str]]:
        """Get list of available export files"""
        export_files = []
        
        try:
            for filename in os.listdir(self.export_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(self.export_dir, filename)
                    file_stats = os.stat(filepath)
                    
                    export_files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': file_stats.st_size,
                        'created': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                    })
            
            # Sort by creation time, newest first
            export_files.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting export files: {e}")
        
        return export_files
