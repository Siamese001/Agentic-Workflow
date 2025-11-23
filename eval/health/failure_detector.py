from __future__ import annotations

"""Agent Immune System (AIS) failure detection primitives.

This module exposes small, pure helpers that inspect telemetry- or
result-like records and emit coarse-grained health signals.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class FailureSignal:
    """Coarse-grained failure signal for AIS policies.

    Fields:
        code: Machine-readable identifier for the failure pattern.
        message: Human-readable explanation.
        severity: "low" | "medium" | "high".
        metadata: Arbitrary structured details.
    """

    code: str
    message: str
    severity: str
    metadata: Dict[str, Any]


def detect_repeated_failures(events: List[Dict[str, Any]], threshold: int = 3) -> List[FailureSignal]:
    """Detect simple repeated-failure patterns in a list of events.

    Each event is expected to be a dict with an optional "event_type"
    and "error_code" field. The detector counts repeated error_codes and
    emits FailureSignal entries when a threshold is exceeded.
    """

    counts: Dict[str, int] = {}
    for evt in events:
        if evt.get("event_type") != "error":
            continue
        code = str(evt.get("error_code") or "unknown")
        counts[code] = counts.get(code, 0) + 1

    signals: List[FailureSignal] = []
    for code, count in counts.items():
        if count >= threshold:
            severity = "high" if count >= threshold * 2 else "medium"
            signals.append(
                FailureSignal(
                    code=f"repeated_{code}",
                    message=f"Error {code!r} occurred {count} times",
                    severity=severity,
                    metadata={"count": count},
                )
            )

    return signals
