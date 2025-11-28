"""Telemetry helpers emitting MCP-compatible events."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from mcp import emit_event

logger = logging.getLogger("telemetry_v10_7")


def log_event(agent: str, event: str, data: Optional[Dict[str, Any]] = None) -> None:
    """Emit a telemetry event while preserving local logging."""

    payload = {
        "agent": agent,
        "event": event,
        "payload": data or {},
    }
    emit_event(payload)
    logger.debug("Telemetry emitted: %s - %s", agent, event)

__all__ = ["log_event"]
