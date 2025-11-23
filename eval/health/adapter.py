from __future__ import annotations

"""AIS telemetry adapter.

This module bridges observability events into the simple dict-based
format expected by eval.health failure detectors and metrics.
"""

from typing import Any, Dict, List

from observability import get_all_events


def collect_error_events() -> List[Dict[str, Any]]:
    """Collect error-like events from the global observability stream.

    The returned list is a lightweight projection with the keys used by
    eval.health failure detectors and metrics:
        • event_type
        • error_code
        • message
    """

    events: List[Dict[str, Any]] = []
    for evt in get_all_events():
        attrs = getattr(evt, "attributes", {}) or {}
        if attrs.get("event_type") != "error":
            continue
        events.append(
            {
                "event_type": "error",
                "error_code": attrs.get("error_code"),
                "message": attrs.get("message"),
            }
        )
    return events
