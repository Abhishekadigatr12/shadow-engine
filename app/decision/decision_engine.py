from typing import Dict, Any
from ..core.config import get_settings
from ..utils.logger import logger
from ..utils.helpers import (
    mask_email, mask_phone, mask_password,
    mask_credit_card, mask_api_key
)

settings = get_settings()


class DecisionEngine:
    """Decision engine for determining actions"""

    def decide(self, risk_score: float) -> str:
        """Decide action based on risk score"""
        if risk_score > settings.RISK_THRESHOLD_HIGH:
            return "BLOCK"
        elif risk_score > settings.RISK_THRESHOLD_MEDIUM:
            return "MASK"
        elif risk_score > settings.RISK_THRESHOLD_LOW:
            return "ALERT"
        else:
            return "ALLOW"

    def mask_sensitive_data(
        self,
        text: str,
        detected_patterns: list
    ) -> Dict[str, Any]:
        """Mask sensitive data in text"""
        masked_text = text
        masking_map = {}

        for pattern in detected_patterns:
            pattern_type = pattern.get("type")
            matched_text = pattern.get("matched_text", "")

            if not matched_text:
                continue

            # Apply appropriate masking
            if pattern_type == "email":
                masked = mask_email(matched_text)
            elif pattern_type == "phone":
                masked = mask_phone(matched_text)
            elif pattern_type == "password":
                masked = mask_password(matched_text)
            elif pattern_type == "credit_card":
                masked = mask_credit_card(matched_text)
            elif pattern_type == "api_key":
                masked = mask_api_key(matched_text)
            else:
                masked = f"[{pattern_type.upper()}]"

            # Replace in text (careful with special characters)
            masked_text = masked_text.replace(matched_text, masked, 1)
            masking_map[matched_text] = masked

        return {
            "original_text": text,
            "masked_text": masked_text,
            "masking_map": masking_map,
            "patterns_masked": len(masking_map)
        }

    def generate_reason(
        self,
        risk_score: float,
        detected_patterns: list,
        classifications: list
    ) -> str:
        """Generate explanation for decision"""
        if risk_score > settings.RISK_THRESHOLD_HIGH:
            primary_threat = detected_patterns[0].get("type") if detected_patterns else "high-risk data"
            return f"Critical risk detected: {primary_threat} pattern identified. Immediate action required."

        elif risk_score > settings.RISK_THRESHOLD_MEDIUM:
            threat_summary = ", ".join(set(p.get("type") for p in detected_patterns)) or "sensitive data"
            return f"Medium-high risk: {threat_summary} detected. Masking sensitive information."

        elif risk_score > settings.RISK_THRESHOLD_LOW:
            classification = classifications[0] if classifications else "potential data leakage"
            return f"Low-medium risk: {classification} detected. Alert for review."

        else:
            return "Low risk content. No action required."


# Singleton instance
_decision_engine = DecisionEngine()


def decide_action(risk_score: float) -> str:
    """Decide action based on risk score"""
    return _decision_engine.decide(risk_score)


def mask_data(text: str, patterns: list) -> Dict[str, Any]:
    """Mask sensitive data"""
    return _decision_engine.mask_sensitive_data(text, patterns)


def generate_decision_reason(
    risk_score: float,
    patterns: list,
    classifications: list
) -> str:
    """Generate reason for decision"""
    return _decision_engine.generate_reason(risk_score, patterns, classifications)
