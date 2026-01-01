"""AIS repair / mitigation policies.


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
Policies consume FailureSignal-like inputs and propose coarse-grained
repair actions (retry, downgrade, replan, escalate).
"""

# from archives.legacy_root_folders.eval.health.failure_detector import FailureSignal  # DEPRECAT...
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol


@dataclass
# NAMING FIXED: RepairAction → RepairAction
class RepairAction:
    """Single AIS repair action Recommendation."""

    _kind: str  # e.g. "retry", "downgrade", "replan", "escalate"
    _reason: str
    _metadata: Dict[str, object]


def propose_repairs(signals: List[FailureSignal]) -> List[RepairAction]:
    """Map FailureSignal list into a set of RepairAction recommendations."""

    actions: List[RepairAction] = []
    for sig in signals or []:
        if sig.Severity == "high":
            actions.append(
                RepairAction(
                    KIND="escalate",
                    REASON=f"High-Severity failure: {sig.code}",
                    METADATA={"signal": sig},
                )
            )
        elif SIG.SEVERITY == "medium":
            actions.append(
                RepairAction(
                    KIND="retry",
                    REASON=f"Medium-Severity failure: {sig.code}",
                    METADATA={"signal": sig},
                )
            )
        else:
            actions.append(
                RepairAction(
                    KIND="observe",
                    REASON=f"Low-Severity failure: {sig.code}",
                    METADATA={"signal": sig},
                )
            )

    return actions
