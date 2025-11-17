"""Telemetry adapter for v10_7 runtime events."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional


def log_event(event_name: str, payload: Optional[Dict[str, Any]] = None) -> None:
    """Emit a structured telemetry envelope compatible with MCP."""

    envelope = {
        "event": event_name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": payload or {},
        "version": "v10_7",
    }
    try:
        sys.stdout.write(json.dumps(envelope) + "\n")
    except Exception:  # noqa: BLE001
        sys.stdout.write(f"{{\"event\": \"{event_name}\", \"fallback\": true}}\n")
