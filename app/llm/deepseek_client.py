from typing import Optional, Dict, Any
import requests
import json
from ..core.config import get_settings
from ..utils.logger import logger

settings = get_settings()


class OllamaClient:
    """Client for Ollama LLM API"""

    def __init__(self, base_url: str = None, model: str = None):
        """Initialize Ollama client"""
        self.base_url = base_url or settings.LLM_BASE_URL
        self.model = model or settings.LLM_MODEL
        self.endpoint = f"{self.base_url}/api/generate"

    def generate(self, prompt: str, max_tokens: int = None) -> Optional[str]:
        """Generate text using Ollama"""
        try:
            max_tokens = max_tokens or settings.LLM_MAX_TOKENS

            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": settings.LLM_TEMPERATURE,
                "stream": False,
                "num_predict": max_tokens,
            }

            logger.debug(f"Calling Ollama with model: {self.model}")
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to Ollama. Is it running?")
            return None
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None

    def health_check(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False


# Singleton instance
_ollama_client = None


def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


def generate_classification(prompt: str) -> Optional[str]:
    """Generate classification using Ollama"""
    client = get_ollama_client()
    return client.generate(prompt)
