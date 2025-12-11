"""Telemetry helpers emitting MCP-compatible events."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.mcp import emit_event  # INVALID: Cannot import from path with hyphens

logger = logging.getLogger("telemetry_v10_7")


def log_event(agent: str, event: str, data: Optional[Dict[str, object]] = None) -> None:
    """Emit a telemetry event while preserving local logging."""

    payload = {
        "agent": agent,
        "event": event,
        "payload": data or {},
    }
    emit_event(payload)
    logger.debug("Telemetry emitted: %s - %s", agent, event)

__all__ = ["log_event"]
