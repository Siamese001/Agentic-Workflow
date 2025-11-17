"""Lightweight telemetry wrapper."""
from __future__ import annotations

import json
import time
from typing import Any, Dict


def log_event(name: str, metadata: Dict[str, Any] | None = None) -> None:
    payload = {"name": name, "metadata": metadata or {}, "ts": time.time()}
    print(json.dumps(payload))


__all__ = ["log_event"]
