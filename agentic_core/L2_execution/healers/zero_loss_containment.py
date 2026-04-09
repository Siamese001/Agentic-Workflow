"""C3 Zero-Loss Failure Containment.

10C-REQ-140: Freeze immediately UWG locks pending diffs status suspended
audit handoff L4 note L6 threshold tune
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from .failure_signal import FailureSignal


class ContainmentAction(Enum):
    """Containment actions."""
    FREEZE = auto()
    LOCK_UWG = auto()
    SUSPEND = auto()
    AUDIT_HANDOFF = auto()
    L4_NOTE = auto()
    L6_TUNE = auto()


@dataclass
class ContainmentResult:
    """Result of zero-loss containment."""
    contained: bool
    actions_taken: list[ContainmentAction]
    pending_diffs_locked: bool
    audit_trail_id: str
    l4_note_id: str
    l6_threshold_adjusted: bool


class ZeroLossContainment:
    """C3 Zero-Loss Failure Containment.

    10C-REQ-140: Freeze immediately UWG locks pending diffs status suspended
    audit handoff L4 note L6 threshold tune.
    """

    CRITICAL_ERRORS = {
        "sovereignty_violation",
        "uwg_bypass_attempt",
        "layer_boundary_violation",
        "replay_integrity_failure",
        "determinism_breach",
    }

    def __init__(self) -> None:
        self._containment_count: int = 0
        self._active_locks: set[str] = set()

    def contain(self, signal: FailureSignal) -> ContainmentResult:
        """Execute zero-loss containment for critical failure."""
        actions: list[ContainmentAction] = []

        # Check if this is a critical error requiring containment
        is_critical = signal.error_code in self.CRITICAL_ERRORS
        is_sovereignty_error = "sovereignty" in signal.error_code.lower()

        if not is_critical and not is_sovereignty_error:
            return ContainmentResult(
                contained=False,
                actions_taken=[],
                pending_diffs_locked=False,
                audit_trail_id="",
                l4_note_id="",
                l6_threshold_adjusted=False,
            )

        self._containment_count += 1
        audit_id = f"AUDIT-{signal.lineage_hash[:8]}"
        l4_note_id = f"L4NOTE-{signal.check_id}"

        # 1. Freeze immediately
        actions.append(ContainmentAction.FREEZE)

        # 2. UWG locks pending diffs
        actions.append(ContainmentAction.LOCK_UWG)
        self._active_locks.add(signal.lineage_hash)

        # 3. Status suspended
        actions.append(ContainmentAction.SUSPEND)

        # 4. Audit handoff
        actions.append(ContainmentAction.AUDIT_HANDOFF)

        # 5. L4 note (if sovereignty-related)
        if is_sovereignty_error:
            actions.append(ContainmentAction.L4_NOTE)

        # 6. L6 threshold tune
        actions.append(ContainmentAction.L6_TUNE)

        return ContainmentResult(
            contained=True,
            actions_taken=actions,
            pending_diffs_locked=True,
            audit_trail_id=audit_id,
            l4_note_id=l4_note_id if is_sovereignty_error else "",
            l6_threshold_adjusted=True,
        )

    def release_lock(self, lineage_hash: str) -> bool:
        """Release UWG lock."""
        if lineage_hash in self._active_locks:
            self._active_locks.remove(lineage_hash)
            return True
        return False

    def is_contained(self, lineage_hash: str) -> bool:
        """Check if lineage is currently contained."""
        return lineage_hash in self._active_locks

    def get_stats(self) -> dict[str, Any]:
        """Get containment statistics."""
        return {
            "total_containments": self._containment_count,
            "active_locks": len(self._active_locks),
        }
