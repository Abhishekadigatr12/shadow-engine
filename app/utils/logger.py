import logging
import sys
from logging.handlers import RotatingFileHandler
from ..core.config import get_settings

settings = get_settings()


def setup_logger(name: str) -> logging.Logger:
    """Setup logger with both file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10485760,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(settings.LOG_LEVEL)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Get or create main logger
logger = setup_logger("shadow-engine")
