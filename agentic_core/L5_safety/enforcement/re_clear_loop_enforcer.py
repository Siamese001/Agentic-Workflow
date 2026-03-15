"""L5 Path D Re-Clear Loop — mandatory re-evaluation after violation remediation.

Spec: L5 Safety, Path D — after a violation is flagged and a remediation is applied,
the enforcement gate MUST re-evaluate the original constraint before marking the
violation as cleared. This prevents silent self-approval of partial fixes.

Re-clear loop contract:
  1. A violation is detected → ReClearTicket is created (status=PENDING).
  2. Remediation is applied externally.
  3. re_evaluate() is called with the remediation evidence.
  4. If the constraint passes, ticket transitions to CLEARED.
  5. If the constraint still fails, ticket transitions to BLOCKED (no silent pass).
  6. A ticket in BLOCKED state MUST NOT be auto-resolved; it requires explicit escalation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


class ReClearViolation(RuntimeError):
    """Raised when the re-clear loop contract is violated."""


class ReClearStatus(str, Enum):
    PENDING = "PENDING"
    CLEARED = "CLEARED"
    BLOCKED = "BLOCKED"
    ESCALATED = "ESCALATED"


@dataclass
class ReClearTicket:
    """Tracks a single L5 violation through the Path D re-clear lifecycle.

    Spec: L5 Safety Path D — immutable once CLEARED or BLOCKED.
    Fields:
        ticket_id: Stable unique identifier (non-empty).
        constraint_id: The L5 constraint that was violated.
        violation_summary: Human-readable description of the violation.
        status: Current lifecycle status.
        remediation_evidence: Evidence dict populated by re_evaluate().
        escalation_note: Required when status=ESCALATED.
    """

    ticket_id: str
    constraint_id: str
    violation_summary: str
    status: ReClearStatus = ReClearStatus.PENDING
    remediation_evidence: dict[str, Any] = field(default_factory=dict)
    escalation_note: str = ""

    def __post_init__(self) -> None:
        if not self.ticket_id or not self.ticket_id.strip():
            raise ReClearViolation("ReClearTicket.ticket_id must be non-empty")
        if not self.constraint_id or not self.constraint_id.strip():
            raise ReClearViolation("ReClearTicket.constraint_id must be non-empty")
        if not self.violation_summary or not self.violation_summary.strip():
            raise ReClearViolation("ReClearTicket.violation_summary must be non-empty")

    def _assert_mutable(self) -> None:
        if self.status in (ReClearStatus.CLEARED, ReClearStatus.BLOCKED):
            raise ReClearViolation(
                f"ReClearTicket '{self.ticket_id}' is terminal (status={self.status.value}). Cleared/Blocked tickets are immutable. Create a new ticket for re-remediation."
            )

    def re_evaluate(
        self, constraint_fn: Callable[[], bool], evidence: dict[str, Any] | None = None
    ) -> ReClearTicket:
        """Re-evaluate the original constraint after remediation.

        Args:
            constraint_fn: Returns True if the constraint is now satisfied, False if still violated.
            evidence: Optional evidence dict to record with the outcome.

        Returns:
            A new ReClearTicket with updated status (CLEARED or BLOCKED).

        Raises:
            ReClearViolation: If the ticket is already terminal.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ReClearTicket.re_evaluate")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:ReClearTicket.re_evaluate".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self._assert_mutable()
        passed = constraint_fn()
        new_status = ReClearStatus.CLEARED if passed else ReClearStatus.BLOCKED
        new_evidence = {**(evidence or {}), "re_evaluate_passed": passed}
        return ReClearTicket(
            ticket_id=self.ticket_id,
            constraint_id=self.constraint_id,
            violation_summary=self.violation_summary,
            status=new_status,
            remediation_evidence=new_evidence,
            escalation_note=self.escalation_note,
        )

    def escalate(self, note: str) -> ReClearTicket:
        """Escalate a BLOCKED ticket with a mandatory note.

        Only BLOCKED tickets may be escalated.
        Raises ReClearViolation if ticket is not BLOCKED.
        """
        if self.status != ReClearStatus.BLOCKED:
            raise ReClearViolation(
                f"Only BLOCKED tickets may be escalated. Ticket '{self.ticket_id}' is {self.status.value}."
            )
        if not note or not note.strip():
            raise ReClearViolation(
                "escalate() requires a non-empty note explaining the escalation rationale."
            )
        return ReClearTicket(
            ticket_id=self.ticket_id,
            constraint_id=self.constraint_id,
            violation_summary=self.violation_summary,
            status=ReClearStatus.ESCALATED,
            remediation_evidence=self.remediation_evidence,
            escalation_note=note,
        )


def open_ticket(ticket_id: str, constraint_id: str, violation_summary: str) -> ReClearTicket:
    """Open a new Path D re-clear ticket for a detected violation."""
    return ReClearTicket(
        ticket_id=ticket_id, constraint_id=constraint_id, violation_summary=violation_summary
    )


__all__ = ["ReClearStatus", "ReClearTicket", "ReClearViolation", "open_ticket"]
