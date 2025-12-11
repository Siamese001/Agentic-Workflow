"""Transforms low-level observability events into a simple format so health checks can spot patterns that might harm resume quality or reliability."""

from __future__ import annotations

from typing import Any, Dict, List

# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.observability import get_all_events  # INVALID: Cannot import from path with hyphens


def collect_error_events() -> List[Dict[str, object]]:
    """Collects error-like events from the global stream so health detectors can flag recurring issues before they impact resume runs."""

    events: List[Dict[str, object]] = []
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



