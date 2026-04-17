import os
from functools import lru_cache
from typing import Optional


class Settings:
    """Application configuration"""

    # API Configuration
    API_TITLE: str = "Shadow Engine - Cybersecurity Decision Engine"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # LLM Configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek:13b")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))

    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./shadow_engine.db"
    )
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"

    # Security
    API_KEY: str = os.getenv("API_KEY", "shadow-dev-key-12345")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "shadow-secret-key-do-not-use-in-production")
    ALGORITHM: str = "HS256"

    # Risk Thresholds
    RISK_THRESHOLD_LOW: float = 0.3
    RISK_THRESHOLD_MEDIUM: float = 0.6
    RISK_THRESHOLD_HIGH: float = 0.85

    # Detection Patterns
    PATTERNS_FILE: str = os.getenv("PATTERNS_FILE", "patterns.yaml")
    ENABLE_REGEX_DETECTION: bool = True
    ENABLE_ANOMALY_DETECTION: bool = True
    ENABLE_LLM_DETECTION: bool = True

    # Learning Configuration
    ENABLE_LEARNING: bool = True
    FEEDBACK_STORE_PATH: str = os.getenv("FEEDBACK_STORE_PATH", "./data/feedback")
    THRESHOLD_ADJUSTMENT_ENABLED: bool = True

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "shadow_engine.log")


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()
