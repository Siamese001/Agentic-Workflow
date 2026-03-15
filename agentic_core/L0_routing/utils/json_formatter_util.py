import json
import logging
import sys
from datetime import datetime, timezone

from agentic_core.config.settings_config import get_settings

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,
    emit_replay_key,
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "json_formatter_util", "p0_governance")
_emit_snapshots_state("p0", "json_formatter_util", "state_snapshot")


class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON objects for machine parsing.
    """

    def format(self, record: logging.LogRecord) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "JSONFormatter.format")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

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
