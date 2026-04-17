from typing import List, Dict, Any
import yaml
from pathlib import Path
from ..utils.logger import logger


class RuleEngine:
    """Rule-based detection engine"""

    def __init__(self, rules_file: str = "rules.yaml"):
        """Initialize rule engine"""
        self.rules = []
        self.load_rules(rules_file)

    def load_rules(self, rules_file: str) -> None:
        """Load rules from YAML file"""
        try:
            rules_path = Path(rules_file)
            if rules_path.exists():
                with open(rules_path, 'r') as f:
                    self.rules = yaml.safe_load(f) or []
                logger.info(f"Loaded {len(self.rules)} rules from {rules_file}")
            else:
                logger.warning(f"Rules file not found: {rules_file}")
                self.rules = []
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            self.rules = []

    def evaluate(self, text: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Evaluate text against rules"""
        matches = []
        context = context or {}

        for rule in self.rules:
            try:
                if self._evaluate_rule(text, rule, context):
                    matches.append({
                        "rule_id": rule.get("id"),
                        "rule_name": rule.get("name"),
                        "severity": rule.get("severity", "medium"),
                        "confidence": rule.get("confidence", 0.7),
                        "description": rule.get("description"),
                    })
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.get('id')}: {e}")

        return matches

    @staticmethod
    def _evaluate_rule(text: str, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a single rule"""
        conditions = rule.get("conditions", [])

        for condition in conditions:
            condition_type = condition.get("type")
            condition_value = condition.get("value")

            if condition_type == "contains":
                if condition_value not in text:
                    return False

            elif condition_type == "regex":
                import re
                if not re.search(condition_value, text):
                    return False

            elif condition_type == "length_exceeds":
                if len(text) <= condition_value:
                    return False

            elif condition_type == "context_key":
                key = condition.get("key")
                expected_value = condition_value
                if context.get(key) != expected_value:
                    return False

        return True


# Initialize default rule engine
_rule_engine = None


def get_rule_engine(rules_file: str = "rules.yaml") -> RuleEngine:
    """Get or create rule engine instance"""
    global _rule_engine
    if _rule_engine is None:
        _rule_engine = RuleEngine(rules_file)
    return _rule_engine


def evaluate_rules(text: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Evaluate text against configured rules"""
    engine = get_rule_engine()
    return engine.evaluate(text, context)
