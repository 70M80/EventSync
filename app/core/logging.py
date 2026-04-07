import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Any
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        extra_data = getattr(record, "extra_data", None)
        if extra_data:
            log_data.update(extra_data)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Safe JSON serialization with fallback
        try:
            return json.dumps(log_data, default=str)
        except (TypeError, ValueError):
            # Fallback for non-serializable content
            log_data["message"] = str(log_data["message"])
            return json.dumps(log_data, default=str)


def get_log_level(level_str: str) -> int:
    """Convert string log level to logging module constant"""
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return levels.get(level_str.upper(), logging.INFO)


def setup_logging():
    # Get log level from settings
    log_level = get_log_level(settings.log_level)

    # Create logger
    logger = logging.getLogger("fastapi_app")
    logger.setLevel(log_level)

    # Prevent duplicate handlers if already configured
    if logger.handlers:
        for handler in logger.handlers:
            handler.setLevel(log_level)
        return logger

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(JSONFormatter())

    # Create file handler for production logs
    file_handler = RotatingFileHandler(
        "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,  # 10MB files, keep 5 backups
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(JSONFormatter())

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Initialize the logger
logger = setup_logging()
