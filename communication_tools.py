
"""
Advanced Communication Tools: Mass Email, SMS, Phishing Detection
Professional-grade communication and security features
"""

import smtplib
import logging
import re
import base64
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
import json

logger = logging.getLogger(__name__)

class PhishingDetector:
    """Advanced phishing detection and analysis"""
    
    def __init__(self):
        self.suspicious_domains = [
            'bit.ly', 'tinyurl.com', 'short.link', 'rebrand.ly',
            'cutt.ly', 'ow.ly', 't.ly', 'is.gd', 'buff.ly'
        ]
        
        self.phishing_keywords = [
            'urgent', 'verify account', 'suspended', 'click here',
            'limited time', 'act now', 'congratulations', 'winner',
            'free money', 'claim now', 'security alert', 'update payment',
            'confirm identity', 'avoid suspension', 'immediate action',
            # UK-specific patterns
            'hmrc', 'tax refund', 'royal mail', 'delivery failed',
            'tv licence', 'council tax', 'parking fine', 'speeding ticket',
            'nhs', 'prescription ready', 'appointment cancelled',
            'energy bill', 'british gas', 'scottish power', 'eon'
        ]
        
        self.financial_triggers = [
            'bank account', 'credit card', 'paypal', 'bitcoin',
            'cryptocurrency', 'investment opportunity', 'tax refund',
            'inheritance', 'lottery', 'prize money', 'wire transfer',
            # UK financial institutions
            'hsbc', 'barclays', 'lloyds', 'natwest', 'halifax', 'santander',
            'nationwide', 'tesco bank', 'first direct', 'monzo', 'starling',
            'revolut', 'wise', 'sort code', 'bacs payment', 'faster payment',
            'standing order', 'direct debit', 'isa account', 'pension fund'
        ]
    
    def analyze_message(self, message: str, sender_email: str = None) -> Dict[str, Any]:
        """Comprehensive phishing analysis"""
        analysis = {
            'risk_level': 'LOW',
            'risk_score': 0,
            'detected_threats': [],
            'suspicious_elements': [],
            'recommendations': [],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        message_lower = message.lower()
        
        # Check for phishing keywords
        keyword_matches = [kw for kw in self.phishing_keywords if kw in message_lower]
        if keyword_matches:
            analysis['risk_score'] += len(keyword_matches) * 10
            analysis['detected_threats'].append('Phishing Keywords Detected')
            analysis['suspicious_elements'].extend(keyword_matches)
        
        # Check for financial triggers
        financial_matches = [ft for ft in self.financial_triggers if ft in message_lower]
        if financial_matches:
            analysis['risk_score'] += len(financial_matches) * 15
            analysis['detected_threats'].append('Financial Social Engineering')
            analysis['suspicious_elements'].extend(financial_matches)
        
        # Check for URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
        if urls:
            analysis['suspicious_elements'].append(f"URLs Found: {len(urls)}")
            for url in urls:
                domain = self.extract_domain(url)
                if domain in self.suspicious_domains:
                    analysis['risk_score'] += 20
                    analysis['detected_threats'].append('Suspicious URL Shortener')
        
        # Check for urgency indicators
        urgency_words = ['immediate', 'urgent', 'asap', 'hurry', 'expires', 'deadline']
        urgency_count = sum(1 for word in urgency_words if word in message_lower)
        if urgency_count > 0:
            analysis['risk_score'] += urgency_count * 5
            analysis['detected_threats'].append('High Urgency Language')
        
        # Email analysis if provided
        if sender_email:
            email_analysis = self.analyze_sender_email(sender_email)
            analysis['risk_score'] += email_analysis['risk_score']
            analysis['detected_threats'].extend(email_analysis['threats'])
        
        # Determine risk level
        if analysis['risk_score'] >= 50:
            analysis['risk_level'] = 'HIGH'
            analysis['recommendations'] = [
                'DO NOT CLICK any links or download attachments',
                'DO NOT provide personal or financial information',
                'Report this message as phishing to your email provider',
                'Verify sender through alternative communication method'
            ]
        elif analysis['risk_score'] >= 25:
            analysis['risk_level'] = 'MEDIUM'
            analysis['recommendations'] = [
                'Exercise extreme caution with this message',
                'Verify sender identity before taking action',
                'Do not provide sensitive information',
                'Check URLs carefully before clicking'
            ]
        else:
            analysis['recommendations'] = [
                'Message appears relatively safe',
                'Still exercise normal email caution',
                'Verify important requests independently'
            ]
        
        return analysis
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return url
    
    def analyze_sender_email(self, email: str) -> Dict[str, Any]:
        """Analyze sender email for suspicious patterns"""
        analysis = {'risk_score': 0, 'threats': []}
        
        email_lower = email.lower()
        
        # Check for common spoofing patterns
        if any(bank in email_lower for bank in ['bank', 'paypal', 'amazon', 'microsoft', 'apple']):
            if not any(domain in email_lower for domain in ['.com', '.co.uk', '.org']):
                analysis['risk_score'] += 30
                analysis['threats'].append('Potential Brand Spoofing')
        
        # Check for suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.info', '.biz']
        if any(tld in email_lower for tld in suspicious_tlds):
            analysis['risk_score'] += 15
            analysis['threats'].append('Suspicious Domain Extension')
        
        # Check for number substitutions
        if re.search(r'[0-9]', email.replace('@', '').split('.')[0]):
            analysis['risk_score'] += 10
            analysis['threats'].append('Numbers in Username')
        
        return analysis

class MassEmailer:
    """Professional mass email capabilities with SMTP support"""
    
    def __init__(self):
        self.smtp_configs = {
            'gmail': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True
            },
            'outlook': {
                'server': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': True
            },
            'yahoo': {
                'server': 'smtp.mail.yahoo.com',
                'port': 587,
                'use_tls': True
            }
        }
    
    def send_mass_email(self, smtp_config: Dict, sender_email: str, sender_password: str,
                       recipients: List[str], subject: str, body: str, 
                       is_html: bool = False, attachments: List[str] = None) -> Dict[str, Any]:
        """Send mass emails with professional formatting"""
        
        results = {
            'total_sent': 0,
            'failed_sends': [],
            'successful_sends': [],
            'errors': [],
            'started_at': datetime.now().isoformat()
        }
        
        try:
            # Setup SMTP connection
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            
            if smtp_config.get('use_tls'):
                server.starttls()
            
            server.login(sender_email, sender_password)
            
            for recipient in recipients:
                try:
                    # Create message
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    
                    # Add body
                    if is_html:
                        msg.attach(MIMEText(body, 'html'))
                    else:
                        msg.attach(MIMEText(body, 'plain'))
                    
                    # Add attachments if provided
                    if attachments:
                        for file_path in attachments:
                            try:
                                with open(file_path, 'rb') as attachment:
                                    part = MIMEBase('application', 'octet-stream')
                                    part.set_payload(attachment.read())
                                    encoders.encode_base64(part)
                                    part.add_header(
                                        'Content-Disposition',
                                        f'attachment; filename= {file_path.split("/")[-1]}'
                                    )
                                    msg.attach(part)
                            except Exception as e:
                                results['errors'].append(f'Attachment error for {file_path}: {str(e)}')
                    
                    # Send email
                    server.send_message(msg)
                    results['successful_sends'].append(recipient)
                    results['total_sent'] += 1
                    
                except Exception as e:
                    error_msg = f'Failed to send to {recipient}: {str(e)}'
                    results['failed_sends'].append(recipient)
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
            
            server.quit()
            
        except Exception as e:
            error_msg = f'SMTP connection error: {str(e)}'
            results['errors'].append(error_msg)
            logger.error(error_msg)
        
        results['completed_at'] = datetime.now().isoformat()
        return results
    
    def create_professional_template(self, template_type: str, data: Dict[str, str]) -> str:
        """Create professional email templates"""
        
        templates = {
            'business_announcement': """
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">{title}</h2>
                    <p>Dear {recipient_name},</p>
                    <p>{message}</p>
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                        <strong>{highlight}</strong>
                    </div>
                    <p>Best regards,<br>{sender_name}<br>{company}</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="font-size: 12px; color: #666;">
                        This email was sent from {company}. If you no longer wish to receive these emails, 
                        please contact us.
                    </p>
                </div>
            </body>
            </html>
            """,
            
            'newsletter': """
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="background-color: #007bff; color: white; padding: 30px; text-align: center;">
                        <h1 style="margin: 0;">{newsletter_title}</h1>
                        <p style="margin: 10px 0 0 0;">{date}</p>
                    </div>
                    <div style="padding: 30px;">
                        <h2 style="color: #2c3e50;">{article_title}</h2>
                        <p>{article_content}</p>
                        <a href="{read_more_link}" style="display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0;">Read More</a>
                    </div>
                    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px;">
                        <p>© 2025 {company}. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        }
        
        template = templates.get(template_type, templates['business_announcement'])
        return template.format(**data)

class SMSGateway:
    """SMS sending capabilities through email-to-SMS gateways"""
    
    def __init__(self):
        self.carrier_gateways = {
            'verizon': '@vtext.com',
            'att': '@txt.att.net',
            'tmobile': '@tmomail.net',
            'sprint': '@messaging.sprintpcs.com',
            'boost': '@smsmyboostmobile.com',
            'cricket': '@sms.cricketwireless.net',
            'uscellular': '@email.uscc.net',
            'vodafone_uk': '@sms.vodafone.net',
            'ee_uk': '@mms.ee.co.uk', 
            'three_uk': '@3.co.uk',
            'o2_uk': '@mmail.co.uk'
        }
    
    def send_sms_via_email(self, smtp_config: Dict, sender_email: str, sender_password: str,
                          phone_number: str, carrier: str, message: str) -> Dict[str, Any]:
        """Send SMS through email-to-SMS gateway"""
        
        result = {
            'success': False,
            'error': None,
            'sent_at': datetime.now().isoformat()
        }
        
        try:
            if carrier not in self.carrier_gateways:
                result['error'] = f'Unsupported carrier: {carrier}'
                return result
            
            # Create SMS email address
            sms_email = phone_number + self.carrier_gateways[carrier]
            
            # Setup SMTP
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            if smtp_config.get('use_tls'):
                server.starttls()
            server.login(sender_email, sender_password)
            
            # Create message (SMS messages should be plain text and under 160 chars)
            msg = MIMEText(message[:160])
            msg['From'] = sender_email
            msg['To'] = sms_email
            msg['Subject'] = ''  # Empty subject for SMS
            
            # Send SMS
            server.send_message(msg)
            server.quit()
            
            result['success'] = True
            result['sms_email'] = sms_email
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f'SMS send error: {e}')
        
        return result
    
    def send_bulk_sms(self, smtp_config: Dict, sender_email: str, sender_password: str,
                     recipients: List[Dict], message: str) -> Dict[str, Any]:
        """Send bulk SMS messages"""
        
        results = {
            'total_sent': 0,
            'failed_sends': [],
            'successful_sends': [],
            'errors': []
        }
        
        for recipient in recipients:
            phone = recipient.get('phone')
            carrier = recipient.get('carrier')
            name = recipient.get('name', phone)
            
            if not phone or not carrier:
                results['errors'].append(f'Missing phone/carrier for {name}')
                continue
            
            # Personalize message if name provided
            personalized_message = message.replace('{name}', name) if '{name}' in message else message
            
            sms_result = self.send_sms_via_email(
                smtp_config, sender_email, sender_password,
                phone, carrier, personalized_message
            )
            
            if sms_result['success']:
                results['successful_sends'].append(name)
                results['total_sent'] += 1
            else:
                results['failed_sends'].append(name)
                results['errors'].append(f'{name}: {sms_result["error"]}')
        
        return results

class CommunicationSuite:
    """Integrated communication tools suite"""
    
    def __init__(self):
        self.phishing_detector = PhishingDetector()
        self.mass_emailer = MassEmailer()
        self.sms_gateway = SMSGateway()
        
        self.communication_logs = []
    
    def log_communication(self, comm_type: str, details: Dict[str, Any]):
        """Log communication activities"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': comm_type,
            'details': details
        }
        self.communication_logs.append(log_entry)
        logger.info(f'Communication logged: {comm_type}')
    
    def analyze_phishing_comprehensive(self, message: str, sender_email: str = None, 
                                     additional_headers: Dict = None) -> Dict[str, Any]:
        """Comprehensive phishing analysis with enhanced detection"""
        
        analysis = self.phishing_detector.analyze_message(message, sender_email)
        
        # Add header analysis if provided
        if additional_headers:
            header_analysis = self.analyze_email_headers(additional_headers)
            analysis['header_analysis'] = header_analysis
            analysis['risk_score'] += header_analysis.get('risk_score', 0)
        
        # Update risk level based on total score
        if analysis['risk_score'] >= 70:
            analysis['risk_level'] = 'CRITICAL'
        elif analysis['risk_score'] >= 50:
            analysis['risk_level'] = 'HIGH'
        elif analysis['risk_score'] >= 25:
            analysis['risk_level'] = 'MEDIUM'
        
        # Log analysis
        self.log_communication('phishing_analysis', {
            'risk_level': analysis['risk_level'],
            'risk_score': analysis['risk_score'],
            'threats_detected': len(analysis['detected_threats'])
        })
        
        return analysis
    
    def analyze_email_headers(self, headers: Dict) -> Dict[str, Any]:
        """Analyze email headers for spoofing and authenticity"""
        analysis = {'risk_score': 0, 'findings': []}
        
        # Check SPF, DKIM, DMARC
        if headers.get('Authentication-Results'):
            auth_results = headers['Authentication-Results'].lower()
            if 'spf=fail' in auth_results:
                analysis['risk_score'] += 20
                analysis['findings'].append('SPF Authentication Failed')
            if 'dkim=fail' in auth_results:
                analysis['risk_score'] += 15
                analysis['findings'].append('DKIM Authentication Failed')
            if 'dmarc=fail' in auth_results:
                analysis['risk_score'] += 25
                analysis['findings'].append('DMARC Authentication Failed')
        
        # Check for suspicious received headers
        received_headers = headers.get('Received', [])
        if isinstance(received_headers, str):
            received_headers = [received_headers]
        
        for received in received_headers:
            if any(suspicious in received.lower() for suspicious in ['[unknown]', 'localhost', '127.0.0.1']):
                analysis['risk_score'] += 10
                analysis['findings'].append('Suspicious Received Header')
        
        return analysis
