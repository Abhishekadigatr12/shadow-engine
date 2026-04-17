import re
from typing import List, Dict, Any, Optional
from ..utils.logger import logger
import json


class RegexDetector:
    """Regex-based detection engine for sensitive patterns"""

    # Pattern definitions
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
        "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{16}\b',
        "pan": r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
        "aadhaar": r'\b\d{4}\s?\d{4}\s?\d{4}\b|\b\d{12}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "api_key": r'(?i)(api[_-]?key|apikey)\s*[:=]\s*[\'"]?([A-Za-z0-9_-]{20,})[\'"]?',
        "password": r'(?i)(password|passwd|pwd)\s*[:=]\s*[\'"]([^\'"]+)[\'"]',
        "sql_injection": r'(?i)(union|select|insert|update|delete|drop|create|alter).*(from|where|table)',
        "private_key": r'-----BEGIN (RSA|DSA|EC|PGP|OPENSSH).*PRIVATE KEY',
        "aws_key": r'(?i)AKIA[0-9A-Z]{16}',
        "github_token": r'(?i)gh[pousr]{1}_[A-Za-z0-9_]{36,255}',
        "slack_token": r'xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24,32}',
        "webhook_url": r'hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[A-Za-z0-9]{24}',
    }

    def __init__(self):
        """Initialize detector with compiled patterns"""
        self.compiled_patterns = {}
        for name, pattern in self.PATTERNS.items():
            try:
                self.compiled_patterns[name] = re.compile(pattern)
            except re.error as e:
                logger.warning(f"Failed to compile pattern {name}: {e}")

    def detect(self, text: str) -> List[Dict[str, Any]]:
        """Detect sensitive patterns in text"""
        matches = []

        for pattern_name, compiled_pattern in self.compiled_patterns.items():
            try:
                findings = compiled_pattern.finditer(text)
                for match in findings:
                    match_dict = {
                        "type": pattern_name,
                        "matched_text": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": self._get_confidence(pattern_name),
                    }
                    matches.append(match_dict)
            except Exception as e:
                logger.error(f"Error detecting pattern {pattern_name}: {e}")

        return matches

    @staticmethod
    def _get_confidence(pattern_name: str) -> float:
        """Get confidence score for pattern"""
        high_confidence = {"credit_card", "ssn", "aadhaar", "pan", "aws_key", "private_key"}
        medium_confidence = {"api_key", "password", "github_token", "slack_token", "webhook_url"}
        low_confidence = {"sql_injection", "email", "phone"}

        if pattern_name in high_confidence:
            return 0.95
        elif pattern_name in medium_confidence:
            return 0.85
        elif pattern_name in low_confidence:
            return 0.5
        else:
            return 0.7


# Singleton instance
_detector = RegexDetector()


def detect_regex(text: str) -> List[Dict[str, Any]]:
    """Detect sensitive patterns in text"""
    return _detector.detect(text)


def get_detected_types(matches: List[Dict[str, Any]]) -> List[str]:
    """Extract unique pattern types from matches"""
    return list(set(match["type"] for match in matches))
