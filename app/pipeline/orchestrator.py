from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from ..detection.regex_detector import detect_regex
from ..detection.rule_engine import evaluate_rules
from ..detection.anomaly_detector import detect_anomalies
from ..llm.deepseek_client import generate_classification
from ..llm.prompts import get_classification_prompt
from ..llm.parser import parse_classification_response
from ..scoring.risk_engine import compute_risk_score, get_severity_level
from ..decision.decision_engine import decide_action, generate_decision_reason
from ..utils.logger import logger
from ..models.response_models import AnalysisResponse, SensitiveEntity, ActionEnum


class PipelineOrchestrator:
    """Orchestrator for the analysis pipeline"""

    def __init__(self):
        """Initialize orchestrator"""
        self.logger = logger

    def run_pipeline(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the full analysis pipeline"""
        try:
            # Generate request ID
            request_id = event.get("request_id") or str(uuid.uuid4())
            text = event.get("raw_data", "")
            user_id = event.get("user_id", "default")
            context = event.get("context", {})

            self.logger.info(f"Pipeline started: request_id={request_id}, user_id={user_id}")

            # Step 1: Regex Detection
            regex_matches = detect_regex(text)
            self.logger.debug(f"Regex matches: {len(regex_matches)}")

            # Step 2: Rule Evaluation
            rule_matches = evaluate_rules(text, context)
            self.logger.debug(f"Rule matches: {len(rule_matches)}")

            # Step 3: LLM Classification
            llm_result = self._run_llm_classification(text)
            llm_score = llm_result.get("risk_score", 0.5) if llm_result else 0.5
            llm_classifications = llm_result.get("classification", []) if llm_result else []
            llm_entities = llm_result.get("entities", []) if llm_result else []

            # Step 4: Anomaly Detection
            feature_vector = self._extract_features(regex_matches, rule_matches)
            anomaly_score = detect_anomalies(feature_vector, user_id)
            self.logger.debug(f"Anomaly score: {anomaly_score:.2f}")

            # Step 5: Risk Scoring
            overall_score = compute_risk_score(regex_matches, llm_score, anomaly_score)
            severity = get_severity_level(overall_score)
            self.logger.debug(f"Risk score: {overall_score:.2f}, Severity: {severity}")

            # Step 6: Decision
            action = decide_action(overall_score)
            reason = generate_decision_reason(overall_score, regex_matches, llm_classifications)
            self.logger.debug(f"Decision: {action}")

            # Step 7: Combine classifications
            all_classifications = list(set(llm_classifications))
            if regex_matches:
                all_classifications.extend([m.get("type") for m in regex_matches])
            all_classifications = list(set(all_classifications))

            # Step 8: Build response
            response = self._build_response(
                request_id=request_id,
                classifications=all_classifications,
                risk_score=overall_score,
                severity=severity,
                action=action,
                reason=reason,
                entities=llm_entities
            )

            self.logger.info(f"Pipeline completed: request_id={request_id}, action={action}")

            return response

        except Exception as e:
            self.logger.error(f"Pipeline error: {e}", exc_info=True)
            return self._error_response(str(e))

    def _run_llm_classification(self, text: str) -> Optional[Dict[str, Any]]:
        """Run LLM classification"""
        try:
            if not text or len(text) == 0:
                return {"classification": ["Safe"], "risk_score": 0.0, "entities": []}

            prompt = get_classification_prompt(text)
            response = generate_classification(prompt)

            if response:
                parsed = parse_classification_response(response)
                if parsed:
                    return parsed
                else:
                    self.logger.warning("Failed to parse LLM response")
                    return {"classification": ["Safe"], "risk_score": 0.1, "entities": []}
            else:
                self.logger.warning("LLM returned no response")
                return {"classification": ["Safe"], "risk_score": 0.1, "entities": []}

        except Exception as e:
            self.logger.error(f"LLM classification error: {e}")
            return {"classification": ["Safe"], "risk_score": 0.1, "entities": []}

    @staticmethod
    def _extract_features(regex_matches: List[Dict], rule_matches: List[Dict]) -> Dict[str, Any]:
        """Extract features for anomaly detection"""
        return {
            "regex_match_count": len(regex_matches),
            "rule_match_count": len(rule_matches),
            "max_regex_confidence": max([m.get("confidence", 0) for m in regex_matches]) if regex_matches else 0,
            "text_length": 0,  # Will be set by detector
        }

    @staticmethod
    def _build_response(
        request_id: str,
        classifications: List[str],
        risk_score: float,
        severity: str,
        action: str,
        reason: str,
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build analysis response"""
        sensitive_entities = [
            SensitiveEntity(
                entity_type=e.get("type", "Unknown"),
                value=e.get("value"),
                confidence=float(e.get("confidence", 0.5))
            ) for e in entities
        ]

        response = AnalysisResponse(
            classification=classifications or ["Safe"],
            risk_score=risk_score,
            severity=severity,
            action=ActionEnum[action],
            reason=reason,
            sensitive_entities=sensitive_entities,
            request_id=request_id
        )

        return response.dict()

    @staticmethod
    def _error_response(error_message: str) -> Dict[str, Any]:
        """Build error response"""
        return {
            "classification": ["Safe"],
            "risk_score": 0.0,
            "severity": "LOW",
            "action": "ALLOW",
            "reason": f"Error in pipeline: {error_message}",
            "sensitive_entities": [],
            "request_id": None,
            "error": True
        }


# Singleton instance
_orchestrator = PipelineOrchestrator()


def run_analysis_pipeline(event: Dict[str, Any]) -> Dict[str, Any]:
    """Run the full analysis pipeline"""
    return _orchestrator.run_pipeline(event)
