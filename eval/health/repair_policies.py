from __future__ import annotations

"""AIS repair / mitigation policies.

Policies consume FailureSignal-like inputs and propose coarse-grained
repair actions (retry, downgrade, replan, escalate).
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from .failure_detector import FailureSignal


@dataclass
class RepairAction:
    """Single AIS repair action recommendation."""

    kind: str  # e.g. "retry", "downgrade", "replan", "escalate"
    reason: str
    metadata: Dict[str, Any]


def propose_repairs(signals: List[FailureSignal]) -> List[RepairAction]:
    """Map FailureSignal list into a set of RepairAction recommendations."""

    actions: List[RepairAction] = []
    for sig in signals or []:
        if sig.severity == "high":
            actions.append(
                RepairAction(
                    kind="escalate",
                    reason=f"High-severity failure: {sig.code}",
                    metadata={"signal": sig},
                )
            )
        elif sig.severity == "medium":
            actions.append(
                RepairAction(
                    kind="retry",
                    reason=f"Medium-severity failure: {sig.code}",
                    metadata={"signal": sig},
                )
            )
        else:
            actions.append(
                RepairAction(
                    kind="observe",
                    reason=f"Low-severity failure: {sig.code}",
                    metadata={"signal": sig},
                )
            )

    return actions
