"""LLM module - Ollama/Deepseek integration"""
from .deepseek_client import get_ollama_client, generate_classification, OllamaClient
from .parser import parse_classification_response, parse_entity_response

__all__ = [
    "get_ollama_client",
    "generate_classification",
    "OllamaClient",
    "parse_classification_response",
    "parse_entity_response",
]