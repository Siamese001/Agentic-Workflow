from __future__ import annotations

"""Transforms low-level observability events into a simple format so health checks can spot patterns that might harm resume quality or reliability."""

from typing import Any, Dict, List

from observability import get_all_events


def collect_error_events() -> List[Dict[str, Any]]:
    """Collects error-like events from the global stream so health detectors can flag recurring issues before they impact resume runs."""

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
