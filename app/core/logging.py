import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Any
from app.core.config import settings


class JSONFormatter(logging.Formatter):
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

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


class DevFormatter(logging.Formatter):
    """Readable logs for development"""

    def format(self, record: logging.LogRecord) -> str:
        return f"{datetime.now().strftime('%H:%M:%S')} | {record.levelname:<8} | {record.name} | {record.getMessage()}"


def get_log_level(level_str: str) -> int:
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return levels.get(level_str.upper(), logging.INFO)


def setup_logging():
    log_level = get_log_level(settings.log_level)
    is_prod = settings.env == "production"

    logger = logging.getLogger("fastapi_app")
    logger.setLevel(log_level)

    if logger.handlers:
        for handler in logger.handlers:
            handler.setLevel(log_level)
        return logger

    # ===== FORMATTER =====
    formatter = JSONFormatter() if is_prod else DevFormatter()

    # ===== CONSOLE =====
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ===== FILE (DEV) =====
    if not is_prod:
        file_handler = RotatingFileHandler(
            "app.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=2,
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logging()
