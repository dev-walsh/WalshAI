
"""
DeepSeek API Client for AI chat completions - Optimized for Speed
"""

import logging
import requests
import json
import time
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

        # Configure optimized session
        self.session = requests.Session()
        
        # Optimized retry strategy for speed
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
            backoff_factor=0.3,  # Faster backoff
            raise_on_status=False
        )
        
        # Single optimized adapter configuration
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy
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

        except requests.exceptions.ConnectionError:
            logger.error("Connection error to DeepSeek API")
            return "🌐 Connection error - please check your internet connection and try again."

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error calling DeepSeek API: {e}")
            return "🌐 Network error - please try again later."

        except Exception as e:
            logger.error(f"Unexpected error calling DeepSeek API: {e}")
            return "❌ Unexpected error occurred. Please try again."

    def test_connection(self) -> bool:
        """Test API connection and credentials"""
        try:
            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
            response = self.create_chat_completion(test_messages)
            return response is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def close(self):
        """Close the HTTP session"""
        if self.session:
            self.session.close()
