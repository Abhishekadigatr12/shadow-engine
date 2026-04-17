from typing import Dict, Any


CLASSIFICATION_PROMPT = """You are a cybersecurity expert analyzing text for sensitive data leakage.

Analyze the following text and provide a JSON response with:
1. classification: List of detected data categories from [PII, Credentials, Source Code, Financial Data, Medical Data, Confidential Business Data, Safe]
2. risk_score: Float between 0.0 and 1.0
3. sensitive_entities: List of detected entities with type, value (masked), and confidence
4. reasoning: Brief explanation

Text to analyze:
{text}

Respond ONLY with valid JSON, no additional text.
"""

RISK_ASSESSMENT_PROMPT = """Based on the detected patterns, assess the risk level.

Detected patterns: {patterns}
Detection confidence: {confidence}
Context: {context}

Provide JSON with:
- overall_risk_score (0.0-1.0)
- pattern_severity (low/medium/high)
- business_impact (minimal/moderate/severe)
- recommended_action (allow/alert/mask/block)

Respond ONLY with valid JSON."""

ENTITY_EXTRACTION_PROMPT = """Extract sensitive entities from text.

Text: {text}

Return JSON with:
- entities: List of {type, value (masked), confidence}
- entity_types: List of unique types found

Respond ONLY with valid JSON."""

ADAPTIVE_LEARNING_PROMPT = """Based on user feedback, adjust detection thresholds.

User feedback: {feedback}
Previous risk score: {previous_score}
Actual classification: {actual_classification}

Recommend threshold adjustments in JSON format.
Respond ONLY with valid JSON."""


def get_classification_prompt(text: str) -> str:
    """Get classification prompt"""
    return CLASSIFICATION_PROMPT.format(text=text[:2000])  # Limit text to 2k chars


def get_risk_assessment_prompt(
    patterns: list,
    confidence: float,
    context: Dict[str, Any] = None
) -> str:
    """Get risk assessment prompt"""
    return RISK_ASSESSMENT_PROMPT.format(
        patterns=str(patterns),
        confidence=f"{confidence:.2f}",
        context=str(context or {})
    )


def get_entity_extraction_prompt(text: str) -> str:
    """Get entity extraction prompt"""
    return ENTITY_EXTRACTION_PROMPT.format(text=text[:2000])


def get_adaptive_learning_prompt(
    feedback: str,
    previous_score: float,
    actual_classification: list
) -> str:
    """Get adaptive learning prompt"""
    return ADAPTIVE_LEARNING_PROMPT.format(
        feedback=feedback,
        previous_score=f"{previous_score:.2f}",
        actual_classification=str(actual_classification)
    )
