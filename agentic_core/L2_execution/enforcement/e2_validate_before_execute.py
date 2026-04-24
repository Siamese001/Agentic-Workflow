"""
E2 validate-before-execute short-circuit — W1 additive (gap plan G8).

Implements the Google Vertex AI best practice:

    "If the model proposes the invocation of a function that would send an
    order, update a database, or otherwise have significant consequences,
    validate the function call with the user before executing it."

Placement: v33 §4 phase E2 (Work Order Check). Before E3 runs, a tool
with a registered ``SafetyProfile`` whose ``requires_e2_confirmation()`` is
True raises ``ConfirmBeforeExecute``. Upstream orchestration (currently
``L3_orchestration`` / the [5] Exit Eval short-circuit path in ADR-023)
catches this exception and routes the packet to HITL without ever reaching
E3.

This keeps L2 stateless and policy-free: L2 only emits the signal. The
actual HITL routing is owned by L5 / [5] per ADR-023.

No broad exception handling, no durable commit, no HITL I/O in this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.L2_execution.types.execution_tool_contract import ToolContract
from agentic_core.L2_execution.types.l2_safety_contracts import (
    ConsequenceLevel,
    Reversibility,
    SafetyProfile,
    SideEffectClass,
    get_safety_profile,
)

__all__ = [
    "E2Verdict",
    "ConfirmBeforeExecute",
    "E2RejectedBeforeExecute",
    "evaluate_work_order",
]


@dataclass(frozen=True, slots=True)
class E2Verdict:
    """Outcome of the E2 validate-before-execute check."""

    tool_name: str
    trace_id: str
    decision: str  # one of "approved", "confirm_required", "rejected"
    profile: SafetyProfile
    reason: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "trace_id": self.trace_id,
            "decision": self.decision,
            "reason": self.reason,
            "profile": self.profile.to_dict(),
            "evidence": dict(self.evidence),
        }


class ConfirmBeforeExecute(Exception):
    """Raised at E2 when the tool requires HITL confirmation before E3.

    Upstream must catch this exception and route the packet to [5] HITL.
    Re-entry after approval re-creates the ``ToolContract`` and re-runs E2,
    which then emits ``decision="approved"`` thanks to the attached
    approval ticket in ``contract.metadata``.
    """

    def __init__(self, verdict: E2Verdict) -> None:
        super().__init__(
            f"confirm_before_execute tool={verdict.tool_name} "
            f"trace_id={verdict.trace_id} reason={verdict.reason!r}"
        )
        self.verdict = verdict


class E2RejectedBeforeExecute(Exception):
    """Raised at E2 when the tool must not execute even with HITL approval."""

    def __init__(self, verdict: E2Verdict) -> None:
        super().__init__(
            f"e2_rejected tool={verdict.tool_name} "
            f"trace_id={verdict.trace_id} reason={verdict.reason!r}"
        )
        self.verdict = verdict


_APPROVAL_META_KEY = "e2_hitl_approval_ticket"


def evaluate_work_order(
    contract: ToolContract,
    *,
    profile: SafetyProfile | None = None,
) -> E2Verdict:
    """Run the E2 validate-before-execute gate.

    Returns an ``E2Verdict`` on the happy path. Raises ``ConfirmBeforeExecute``
    if the caller should route to HITL before invoking E3. Raises
    ``E2RejectedBeforeExecute`` if the profile forbids execution outright
    (reserved for future hard policy; not triggered by default profiles).

    ``contract.metadata`` is inspected for an existing approval ticket under
    the ``e2_hitl_approval_ticket`` key. When present, the gate is satisfied
    and the verdict is ``approved`` — this is how HITL re-entry works
    without duplicating confirmation.
    """
    prof = profile or get_safety_profile(contract.tool_name)
    approval_ticket = contract.metadata.get(_APPROVAL_META_KEY)

    # Hard-rejection slot. Intentionally unreachable for the default profile;
    # reserved for future policy where SideEffectClass=MUTATE_STATE on a
    # critical target is never permitted, even with HITL approval.
    if (
        prof.consequence is ConsequenceLevel.CRITICAL
        and prof.side_effect is SideEffectClass.MUTATE_STATE
        and prof.reversibility is Reversibility.IRREVERSIBLE
        and contract.metadata.get("policy_forbid_irreversible_critical") is True
    ):
        verdict = E2Verdict(
            tool_name=contract.tool_name,
            trace_id=contract.trace_id,
            decision="rejected",
            profile=prof,
            reason="policy forbids irreversible critical mutation",
        )
        raise E2RejectedBeforeExecute(verdict)

    if prof.requires_e2_confirmation() and not approval_ticket:
        verdict = E2Verdict(
            tool_name=contract.tool_name,
            trace_id=contract.trace_id,
            decision="confirm_required",
            profile=prof,
            reason=(
                f"consequence={prof.consequence.value} "
                f"side_effect={prof.side_effect.value} "
                f"reversibility={prof.reversibility.value}"
            ),
        )
        raise ConfirmBeforeExecute(verdict)

    return E2Verdict(
        tool_name=contract.tool_name,
        trace_id=contract.trace_id,
        decision="approved",
        profile=prof,
        reason="safety profile within auto-approve envelope"
        if not approval_ticket
        else "hitl approval ticket attached",
        evidence={"approval_ticket_present": bool(approval_ticket)},
    )
