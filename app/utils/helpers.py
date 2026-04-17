import uuid
import re
import json
from typing import Any, Dict, Optional, List


def generate_request_id() -> str:
    """Generate unique request ID"""
    return str(uuid.uuid4())


def mask_email(email: str) -> str:
    """Mask email address"""
    if not email or '@' not in email:
        return "***"
    parts = email.split('@')
    if len(parts[0]) <= 2:
        return f"*{parts[0][-1]}@{parts[1]}"
    return f"{parts[0][0]}***{parts[0][-1]}@{parts[1]}"


def mask_phone(phone: str) -> str:
    """Mask phone number"""
    if not phone or len(phone) < 4:
        return "***"
    return f"***-***-{phone[-4:]}"


def mask_password(password: str) -> str:
    """Mask password"""
    return f"***{len(password)}chars***"


def mask_credit_card(cc: str) -> str:
    """Mask credit card number"""
    if not cc or len(cc) < 4:
        return "***"
    return f"****-****-****-{cc[-4:]}"


def mask_api_key(key: str) -> str:
    """Mask API key"""
    if not key or len(key) < 4:
        return "***"
    return f"{key[:4]}...{key[-4:]}"


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from text"""
    try:
        # Try to find JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def extract_classification_from_text(text: str) -> Optional[List[str]]:
    """Extract classification from LLM response"""
    classifications = []
    
    keywords = {
        "PII": ["personal", "identifiable", "pii"],
        "Credentials": ["credential", "password", "api key", "token", "secret"],
        "Source Code": ["code", "source", "github", "repository"],
        "Financial Data": ["credit card", "bank", "financial", "account", "pan"],
        "Medical Data": ["medical", "health", "patient", "diagnosis"],
        "Confidential Business Data": ["confidential", "proprietary", "secret", "trade"],
    }
    
    text_lower = text.lower()
    for classification, keywords_list in keywords.items():
        for keyword in keywords_list:
            if keyword in text_lower:
                classifications.append(classification)
                break
    
    return classifications if classifications else None


def normalize_text(text: str) -> str:
    """Normalize text for processing"""
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text
