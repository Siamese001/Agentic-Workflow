"""AIS health metrics helpers.

Simple aggregation utilities over error / success events that can be
used by tests or higher-level evaluation code.
"""


def compute_error_rate(events: list[dict[str, object]]) -> float:
    """Return fraction of events marked as errors.

    Events are dicts with an optional "event_type" == "error" flag.
    """

    if not events:
        return 0.0

    errors = sum(1 for evt in events if evt.get("event_type") == "error")
    return errors / float(len(events))


def count_failures_by_code(events: list[dict[str, object]]) -> dict[str, int]:
    """Aggregate error events by their error_code field."""

    counts: dict[str, int] = {}
    for evt in events:
        if evt.get("event_type") != "error":
            continue
        code = str(evt.get("error_code") or "unknown")
        counts[code] = counts.get(code, 0) + 1
    return counts
