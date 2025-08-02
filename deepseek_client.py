
"""
Enhanced DeepSeek API Client with optimized performance and error handling
"""

import logging
import requests
import json
import time
import socket
from typing import List, Dict, Optional, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Suppress SSL warnings for development (Windows compatibility)
urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

class DeepSeekAPIError(Exception):
    """Custom exception for DeepSeek API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class DeepSeekClient:
    """Enhanced DeepSeek API client with improved error handling and performance"""

    def __init__(self, api_key: str, api_url: str, model: str, timeout: int = 15, max_retries: int = 2):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.timeout = min(timeout, 20)  # Reasonable timeout limit
        self.max_retries = min(max_retries, 3)  # Reasonable retry limit
        
        # Initialize optimized session
        self._setup_session()
        
        # Performance metrics
        self.request_count = 0
        self.total_response_time = 0.0
        self.error_count = 0
    
    def _setup_session(self):
        """Configure optimized HTTP session with Windows compatibility"""
        self.session = requests.Session()
        
        # Enhanced retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
            backoff_factor=0.5,
            raise_on_status=False,
            connect=3,
            read=3
        )
        
        # Optimized adapter configuration
        adapter = HTTPAdapter(
            pool_connections=5,
            pool_maxsize=10,
            max_retries=retry_strategy,
            socket_options=[(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)]
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'WalshAI-Professional-Suite/1.0',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate'
        })
    
    def create_chat_completion(self, messages: List[Dict[str, str]], 
                             temperature: float = 0.3, 
                             max_tokens: int = 1200) -> Optional[str]:
        """Create optimized chat completion with enhanced error handling"""
        try:
            start_time = time.time()
            self.request_count += 1
            
            # Validate input
            if not messages or not isinstance(messages, list):
                raise DeepSeekAPIError("Invalid messages format")
            
            # Optimize payload for better performance
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": max(0.0, min(1.0, temperature)),  # Clamp temperature
                "max_tokens": max(100, min(2000, max_tokens)),   # Reasonable token limits
                "stream": False,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "top_p": 0.9
            }
            
            logger.debug(f"Sending request to DeepSeek API ({len(messages)} messages)")
            
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
                verify=True  # Enable SSL verification for production
            )
            
            response_time = time.time() - start_time
            self.total_response_time += response_time
            
            logger.debug(f"API request completed in {response_time:.2f}s")
            
            return self._handle_response(response)
            
        except requests.exceptions.Timeout:
            self.error_count += 1
            logger.error(f"Request timeout ({self.timeout}s)")
            return "⏰ Response timeout - the AI service is responding slowly. Please try again."
        
        except requests.exceptions.ConnectionError as e:
            self.error_count += 1
            return self._handle_connection_error(e)
        
        except requests.exceptions.RequestException as e:
            self.error_count += 1
            logger.error(f"Network error: {e}")
            return "🌐 Network error - please check your connection and try again."
        
        except DeepSeekAPIError as e:
            self.error_count += 1
            logger.error(f"DeepSeek API error: {e}")
            return f"❌ API Error: {str(e)}"
        
        except Exception as e:
            self.error_count += 1
            logger.error(f"Unexpected error: {e}")
            return "❌ Unexpected error occurred. Please try again."
    
    def _handle_response(self, response: requests.Response) -> Optional[str]:
        """Handle API response with comprehensive error checking"""
        status_code = response.status_code
        
        if status_code == 200:
            try:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    logger.debug(f"Successfully received response ({len(content)} chars)")
                    return content.strip()
                else:
                    logger.error("Invalid response format from DeepSeek API")
                    raise DeepSeekAPIError("Invalid response format", status_code, data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise DeepSeekAPIError("Invalid JSON response", status_code)
        
        elif status_code == 401:
            logger.error("Invalid DeepSeek API key")
            return "❌ API key issue - please check your DeepSeek API key configuration."
        
        elif status_code in [402, 429]:
            logger.error("Insufficient credits or rate limit exceeded")
            return None  # Triggers credits error message
        
        elif status_code == 400:
            error_msg = self._extract_error_message(response)
            logger.error(f"Bad request: {error_msg}")
            return f"❌ Request error: {error_msg}"
        
        else:
            error_msg = self._extract_error_message(response)
            logger.error(f"API error {status_code}: {error_msg}")
            raise DeepSeekAPIError(f"API error {status_code}: {error_msg}", status_code)
    
    def _handle_connection_error(self, error: Exception) -> str:
        """Handle connection errors with specific Windows-friendly messages"""
        error_str = str(error).lower()
        
        if "name or service not known" in error_str or "nodename nor servname provided" in error_str:
            return "🌐 DNS resolution error - check your internet connection and DNS settings."
        elif "connection refused" in error_str:
            return "🔒 DeepSeek API service temporarily unavailable - please try again in a few moments."
        elif "ssl" in error_str:
            return "🔒 SSL/TLS connection error - please check your network security settings."
        elif "proxy" in error_str:
            return "🌐 Proxy connection error - check your proxy settings."
        else:
            logger.error(f"Connection error: {error}")
            return "🌐 Connection error - please check your internet connection and try again."
    
    def _extract_error_message(self, response: requests.Response) -> str:
        """Extract meaningful error message from response"""
        try:
            data = response.json()
            if 'error' in data:
                if isinstance(data['error'], dict) and 'message' in data['error']:
                    return data['error']['message']
                elif isinstance(data['error'], str):
                    return data['error']
            return f"HTTP {response.status_code}"
        except:
            return f"HTTP {response.status_code}"
    
    def test_connection(self) -> bool:
        """Enhanced connection test with detailed diagnostics"""
        try:
            # Test basic connectivity
            logger.info("Testing basic network connectivity...")
            socket.create_connection(("api.deepseek.com", 443), timeout=5)
            logger.info("Basic connectivity confirmed")
            
            # Test API call
            logger.info("Testing API authentication...")
            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
            response = self.create_chat_completion(test_messages)
            
            success = (response is not None and 
                      not response.startswith('🌐') and 
                      not response.startswith('🔒') and 
                      not response.startswith('❌'))
            
            if success:
                logger.info("DeepSeek API connection test successful")
            else:
                logger.warning(f"API test failed: {response}")
            
            return success
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get performance statistics"""
        avg_response_time = (self.total_response_time / self.request_count 
                           if self.request_count > 0 else 0.0)
        error_rate = (self.error_count / self.request_count 
                     if self.request_count > 0 else 0.0)
        
        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'average_response_time': avg_response_time,
            'error_rate': error_rate
        }
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'session') and self.session:
            self.session.close()
            logger.debug("DeepSeek client session closed")
