import statistics
from typing import List, Optional
from collections import defaultdict
from ..utils.logger import logger


class AnomalyDetector:
    """Statistical anomaly detection engine"""

    def __init__(self, window_size: int = 100):
        """Initialize anomaly detector"""
        self.window_size = window_size
        self.history = defaultdict(list)

    def detect(self, feature_vector: dict, user_id: str = "default") -> float:
        """Detect anomalies using statistical methods"""
        try:
            # For now, implement a simple baseline anomaly detection
            # In production, use more sophisticated methods
            
            anomaly_score = 0.0

            # Check for unusual patterns
            for feature_name, feature_value in feature_vector.items():
                if isinstance(feature_value, (int, float)):
                    # Add to history
                    self.history[user_id].append(feature_value)

                    # Keep only recent history
                    if len(self.history[user_id]) > self.window_size:
                        self.history[user_id] = self.history[user_id][-self.window_size:]

                    # Calculate z-score if we have enough history
                    if len(self.history[user_id]) >= 10:
                        mean = statistics.mean(self.history[user_id])
                        stdev = statistics.stdev(self.history[user_id])

                        if stdev > 0:
                            z_score = (feature_value - mean) / stdev
                            # High z-score indicates anomaly
                            if abs(z_score) > 3:
                                anomaly_score = min(0.95, abs(z_score) / 10)

            return anomaly_score

        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return 0.0

    def get_baseline(self, user_id: str = "default") -> dict:
        """Get baseline statistics for user"""
        if user_id not in self.history or not self.history[user_id]:
            return {}

        history = self.history[user_id]
        return {
            "mean": statistics.mean(history),
            "stdev": statistics.stdev(history) if len(history) > 1 else 0,
            "min": min(history),
            "max": max(history),
            "count": len(history),
        }

    def reset_user_history(self, user_id: str) -> None:
        """Reset history for a user"""
        if user_id in self.history:
            del self.history[user_id]
            logger.info(f"Reset history for user: {user_id}")


# Singleton instance
_anomaly_detector = AnomalyDetector()


def detect_anomalies(feature_vector: dict, user_id: str = "default") -> float:
    """Detect anomalies in feature vector"""
    return _anomaly_detector.detect(feature_vector, user_id)


def get_user_baseline(user_id: str = "default") -> dict:
    """Get baseline for user"""
    return _anomaly_detector.get_baseline(user_id)
