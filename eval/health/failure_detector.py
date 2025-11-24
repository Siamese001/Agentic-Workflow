from __future__ import annotations

"""Implements simple failure-detection helpers that turn raw telemetry into health signals so recurring problems can be fixed before they degrade resume quality."""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class FailureSignal:
    """Represents a coarse failure signal used by health policies to judge how serious repeated issues are for resume runs."""

    code: str
    message: str
    severity: str
    metadata: Dict[str, Any]


def detect_repeated_failures(events: List[Dict[str, Any]], threshold: int = 3) -> List[FailureSignal]:
    """Finds repeated error patterns in events so teams can spot unstable behavior that might lead to inconsistent or failed resume outputs."""

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
