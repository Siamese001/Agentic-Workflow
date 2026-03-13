import json
import logging
import sys
from datetime import datetime, timezone

from agentic_core.config.settings_config import get_settings


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
    if settings.ENVIRONMENT == "prod":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger
