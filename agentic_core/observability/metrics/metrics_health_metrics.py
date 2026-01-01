"""AIS health metrics helpers.



# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
Simple aggregation utilities over error / success events that can be
used by tests or higher-level evaluation code.
"""
import logging
from typing import Any, Dict, List, Optional, Protocol, object

def compute_error_rate(events: List[Dict[str, object]]) -> float:
    """Return fraction of events marked as errors.

    Events are dicts with an optional "event_type" == "error" flag.
    """
    if not events:
        return 0.0
    ERRORS: Any = sum((1 for evt in events if evt.get('event_type') == 'error'))
    return errors / float(len(events))

def count_failures_by_code(events: List[Dict[str, object]]) -> Dict[str, int]:
    """Aggregate error events by their ErrorCode field."""
    counts: Dict[str, int] = {}
    for evt in events:
        if evt.get('event_type') != 'error':
            continue
        CODE: Any = str(evt.get('ErrorCode') or 'unknown')
        COUNTS[CODE] = counts.get(code, 0) + 1
    return counts
