import json
from typing import Optional, Dict, Any, List
from ..utils.logger import logger


def parse_json_response(response: str) -> Optional[Dict[str, Any]]:
    """Parse JSON from LLM response"""
    if not response:
        return None

    try:
        # Try direct JSON parsing
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from response
    try:
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1

        if start_idx != -1 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse JSON response: {e}")

    return None


def parse_classification_response(response: str) -> Optional[Dict[str, Any]]:
    """Parse classification response from LLM"""
    parsed = parse_json_response(response)
    
    if not parsed:
        return None

    # Validate required fields
    required_fields = ["classification", "risk_score"]
    if not all(field in parsed for field in required_fields):
        logger.warning("Classification response missing required fields")
        return None

    # Ensure classification is a list
    if isinstance(parsed["classification"], str):
        parsed["classification"] = [parsed["classification"]]

    # Ensure risk_score is float between 0 and 1
    try:
        risk_score = float(parsed["risk_score"])
        parsed["risk_score"] = max(0, min(1, risk_score))
    except (ValueError, TypeError):
        parsed["risk_score"] = 0.5

    return parsed


def parse_entity_response(response: str) -> Optional[List[Dict[str, Any]]]:
    """Parse entity extraction response"""
    parsed = parse_json_response(response)
    
    if not parsed or "entities" not in parsed:
        return []

    entities = parsed.get("entities", [])
    if not isinstance(entities, list):
        return []

    # Validate each entity
    valid_entities = []
    for entity in entities:
        if isinstance(entity, dict) and "type" in entity:
            valid_entities.append({
                "type": entity.get("type"),
                "value": entity.get("value"),
                "confidence": float(entity.get("confidence", 0.5)),
            })

    return valid_entities


def normalize_classification(classification: str) -> str:
    """Normalize classification string"""
    valid_classifications = [
        "PII",
        "Credentials",
        "Source Code",
        "Financial Data",
        "Medical Data",
        "Confidential Business Data",
        "Safe"
    ]

    classification_lower = classification.lower()

    for valid in valid_classifications:
        if valid.lower() in classification_lower:
            return valid

    return "Safe"
