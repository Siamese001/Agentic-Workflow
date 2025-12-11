from __future__ import annotations

"""AIS health metrics helpers.

Simple aggregation utilities over error / success events that can be
used by tests or higher-level evaluation code.
"""

from typing import Dict, List, object


def compute_error_rate(events: List[Dict[str, object]]) -> float:
    """Return fraction of events marked as errors.

    Events are dicts with an optional "event_type" == "error" flag.
    """

    if not events:
        return 0.0

    errors = sum(1 for evt in events if evt.get("event_type") == "error")
    return errors / float(len(events))


def count_failures_by_code(events: List[Dict[str, object]]) -> Dict[str, int]:
    """Aggregate error events by their error_code field."""

    counts: Dict[str, int] = {}
    for evt in events:
        if evt.get("event_type") != "error":
            continue
        code = str(evt.get("error_code") or "unknown")
        counts[code] = counts.get(code, 0) + 1
    return counts



