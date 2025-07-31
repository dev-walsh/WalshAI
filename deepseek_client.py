"""
DeepSeek API Client for AI chat completions
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
    """Client for interacting with DeepSeek AI API"""
    
    def __init__(self, api_key: str, api_url: str, model: str, timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'telegram-bot/1.0'
        })
    
    def create_chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """
        Create a chat completion using DeepSeek API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text or None if failed
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            logger.info(f"Sending request to DeepSeek API with {len(messages)} messages")
            
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    logger.info("Successfully received response from DeepSeek API")
                    return content.strip()
                else:
                    logger.error("Invalid response format from DeepSeek API")
                    return None
            
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded, waiting before retry")
                time.sleep(5)
                return None
            
            elif response.status_code == 401:
                logger.error("Invalid API key for DeepSeek API")
                return None
            
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Timeout while calling DeepSeek API")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while calling DeepSeek API: {e}")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse DeepSeek API response: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error while calling DeepSeek API: {e}")
            return None
    
    def get_system_message(self) -> Dict[str, str]:
        """Get the system message for the AI assistant"""
        return {
            "role": "system",
            "content": "You are a helpful AI assistant created by DeepSeek. You provide informative, accurate, and helpful responses to user questions. Keep your responses concise but comprehensive."
        }
    
    def close(self):
        """Close the HTTP session"""
        if self.session:
            self.session.close()
