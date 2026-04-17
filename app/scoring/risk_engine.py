from typing import Dict, List, Any
from ..core.config import get_settings
from ..utils.logger import logger

settings = get_settings()


class RiskEngine:
    """Risk scoring engine"""

    def __init__(self):
        """Initialize risk engine with weights"""
        # Weighting factors
        self.regex_weight = 0.4
        self.llm_weight = 0.5
        self.anomaly_weight = 0.1

    def compute_score(
        self,
        regex_matches: List[Dict[str, Any]],
        llm_score: float,
        anomaly_score: float = 0.0
    ) -> float:
        """Compute overall risk score"""
        try:
            # Regex-based score (max confidence of matches)
            regex_score = 0.0
            if regex_matches:
                regex_score = max(match.get("confidence", 0) for match in regex_matches)

            # Weighted combination
            overall_score = (
                self.regex_weight * regex_score +
                self.llm_weight * llm_score +
                self.anomaly_weight * anomaly_score
            )

            # Clamp to [0, 1]
            overall_score = max(0, min(1, overall_score))

            logger.debug(
                f"Risk score computation: regex={regex_score:.2f}, "
                f"llm={llm_score:.2f}, anomaly={anomaly_score:.2f}, "
                f"overall={overall_score:.2f}"
            )

            return overall_score

        except Exception as e:
            logger.error(f"Error computing risk score: {e}")
            return 0.5

    def get_severity(self, risk_score: float) -> str:
        """Get severity level based on risk score"""
        if risk_score >= settings.RISK_THRESHOLD_HIGH:
            return "CRITICAL"
        elif risk_score >= settings.RISK_THRESHOLD_MEDIUM:
            return "HIGH"
        elif risk_score >= settings.RISK_THRESHOLD_LOW:
            return "MEDIUM"
        else:
            return "LOW"

    def get_details(
        self,
        regex_matches: List[Dict[str, Any]],
        llm_score: float,
        anomaly_score: float = 0.0
    ) -> Dict[str, Any]:
        """Get detailed risk assessment"""
        regex_score = max([m.get("confidence", 0) for m in regex_matches]) if regex_matches else 0

        return {
            "overall_score": self.compute_score(regex_matches, llm_score, anomaly_score),
            "regex_contribution": regex_score * self.regex_weight,
            "llm_contribution": llm_score * self.llm_weight,
            "anomaly_contribution": anomaly_score * self.anomaly_weight,
            "primary_threat": self._get_primary_threat(regex_matches),
        }

    @staticmethod
    def _get_primary_threat(regex_matches: List[Dict[str, Any]]) -> str:
        """Get primary threat type"""
        if not regex_matches:
            return "Unknown"

        highest_match = max(regex_matches, key=lambda x: x.get("confidence", 0))
        return highest_match.get("type", "Unknown")


# Singleton instance
_risk_engine = RiskEngine()


def compute_risk_score(
    regex_matches: List[Dict[str, Any]],
    llm_score: float,
    anomaly_score: float = 0.0
) -> float:
    """Compute overall risk score"""
    return _risk_engine.compute_score(regex_matches, llm_score, anomaly_score)


def get_severity_level(risk_score: float) -> str:
    """Get severity level"""
    return _risk_engine.get_severity(risk_score)


def get_risk_details(
    regex_matches: List[Dict[str, Any]],
    llm_score: float,
    anomaly_score: float = 0.0
) -> Dict[str, Any]:
    """Get detailed risk information"""
    return _risk_engine.get_details(regex_matches, llm_score, anomaly_score)
