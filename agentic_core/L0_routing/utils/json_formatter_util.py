# Structured JSON Logging Setup
# Strategy: Centralized formatter to ensure observability
# Zero-Ambiguity Standard: Renamed from JSONFormatter.py to json_formatter_util.py
# Category: UTILITY (Logging infrastructure helper)

import json
import logging
import sys
from datetime import datetime, timezone

from agentic_core.config.settings_config import get_settings


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON objects for machine parsing.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "app": get_settings().APP_NAME,
            "env": get_settings().ENVIRONMENT,
        }
        # Include exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logging():
    """
    Initialize application-wide logging.
    Call this once at application startup.
    """
    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)

    # Use JSON for prod, Standard for dev (optional, forcing JSON for consistency here)
    if settings.ENVIRONMENT == "prod":
        handler.setFormatter(JSONFormatter())
    else:
        # Simple readable format for dev
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))

    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    # Prevent duplicate handlers
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
