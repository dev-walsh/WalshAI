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

        # Configure session with optimizations for speed
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
            'User-Agent': 'telegram-bot/1.0',
            'Connection': 'keep-alive'
        })

        # Optimized connection pooling for faster requests
        adapter = HTTPAdapter(
            pool_connections=20,
            pool_maxsize=50,
            max_retries=Retry(
                total=max_retries,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

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
            timeout = min(self.timeout, 15)  # Cap at 15 seconds for faster responses

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,  # Lower for faster, more focused responses
                "max_tokens": 1500,  # Reduced for faster generation
                "stream": False,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }

            logger.info(f"Sending request to AI API with {len(messages)} messages")

            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=timeout
            )

            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    logger.info("Successfully received response from AI API")
                    return content.strip()
                else:
                    logger.error("Invalid response format from AI API")
                    return None

            elif response.status_code == 429:
                logger.warning("Rate limit exceeded, waiting before retry")
                time.sleep(5)
                return None

            elif response.status_code == 401:
                logger.error("Invalid API key for AI API")
                return None

            else:
                logger.error(f"AI API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error("Timeout while calling AI API")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while calling AI API: {e}")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI API response: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error while calling AI API: {e}")
            return None

    def get_system_message(self) -> Dict[str, str]:
        """Get the system message for the AI assistant"""
        return {
            "role": "system",
            "content": "You are WalshAI, a helpful and intelligent AI assistant. You provide informative, accurate, and helpful responses to user questions. Keep your responses concise but comprehensive. You are friendly, professional, and always aim to be helpful."
        }

    def close(self):
        """Close the HTTP session"""
        if self.session:
            self.session.close()