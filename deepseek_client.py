"""
DeepSeek API Client for AI chat completions - Optimized for Speed
"""

import logging
import requests
import json
import time
import socket
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """Optimized client for interacting with DeepSeek AI API"""

    def __init__(self, api_key: str, api_url: str, model: str, timeout: int = 15, max_retries: int = 2):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.timeout = min(timeout, 15)  # Cap at 15 seconds max
        self.max_retries = min(max_retries, 2)  # Reduce retries for speed

        # Configure optimized session with better connection handling
        self.session = requests.Session()

        # Enhanced retry strategy with connection error handling
        retry_strategy = Retry(
            total=3,  # Increased for connection issues
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
            backoff_factor=0.5,
            raise_on_status=False,
            # Add connection error retries
            connect=3,
            read=3
        )

        # Enhanced adapter configuration for better connectivity
        adapter = HTTPAdapter(
            pool_connections=5,
            pool_maxsize=10,
            max_retries=retry_strategy,
            socket_options=[
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10),
                (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 6),
            ]
        )

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Optimized headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'telegram-bot-optimized/1.0',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate'
        })

    def create_chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 1200) -> Optional[str]:
        """
        Create a chat completion with optimized settings for speed
        """
        try:
            # Optimized payload for faster responses
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,  # Lower for consistency and speed
                "max_tokens": 1200,  # Reduced for faster generation
                "stream": False,
                "frequency_penalty": 0.0,  # Remove penalties for speed
                "presence_penalty": 0.0,
                "top_p": 0.9  # Add top_p for better quality with speed
            }

            logger.info(f"Sending optimized request to DeepSeek API ({len(messages)} messages)")
            start_time = time.time()

            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )

            request_time = time.time() - start_time
            logger.info(f"API request completed in {request_time:.2f}s")

            # Handle different response codes
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        content = data['choices'][0]['message']['content']
                        logger.info(f"Successfully received response ({len(content)} chars)")
                        return content.strip()
                    else:
                        logger.error("Invalid response format from DeepSeek API")
                        return None
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse DeepSeek response: {e}")
                    return None

            elif response.status_code == 401:
                logger.error("❌ Invalid DeepSeek API key - check your API key")
                return "❌ API key issue - please check your DeepSeek API key configuration."

            elif response.status_code == 402 or response.status_code == 429:
                # Handle insufficient credits specifically
                logger.error("💳 Insufficient DeepSeek credits or rate limit exceeded")
                return None  # This will trigger the credits error message

            elif response.status_code == 400:
                logger.error(f"Bad request to DeepSeek API: {response.text}")
                return "❌ Request error - message may be too long or contain invalid content."

            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout ({self.timeout}s) - DeepSeek API too slow")
            return "⏰ Response timeout - the AI service is responding slowly. Please try again."

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to DeepSeek API: {e}")
            # Try to determine if it's a DNS/network issue
            if "Name or service not known" in str(e) or "nodename nor servname provided" in str(e):
                return "🌐 DNS resolution error - check your internet connection and DNS settings."
            elif "Connection refused" in str(e):
                return "🔒 DeepSeek API service temporarily unavailable - please try again in a few moments."
            else:
                return "🌐 Connection error - please check your internet connection and try again."

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error calling DeepSeek API: {e}")
            if "SSL" in str(e).upper():
                return "🔒 SSL/TLS connection error - please check your network security settings."
            else:
                return "🌐 Network error - please try again later."

        except Exception as e:
            logger.error(f"Unexpected error calling DeepSeek API: {e}")
            return "❌ Unexpected error occurred. Please try again."

    def test_connection(self) -> bool:
        """Test API connection and credentials with enhanced diagnostics"""
        try:
            # First test basic connectivity
            import socket
            try:
                socket.create_connection(("api.deepseek.com", 443), timeout=5)
                logger.info("Basic network connectivity to DeepSeek API confirmed")
            except Exception as e:
                logger.warning(f"Basic connectivity test failed: {e}")
                return False
            
            # Test API call
            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
            response = self.create_chat_completion(test_messages)
            return response is not None and not response.startswith('🌐') and not response.startswith('🔒')
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def close(self):
        """Close the HTTP session"""
        if self.session:
            self.session.close()