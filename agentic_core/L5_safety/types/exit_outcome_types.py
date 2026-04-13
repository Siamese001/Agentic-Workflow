"""Exit outcome payload types — minimal bounded stubs for each live ExitDisposition.

Produced by ExitControlGate.shape_outcome() after evaluate_sealed() returns.
One type per ExitDisposition value.  One disposition per evaluation.  No dual paths.

Maps to: docs/reference/05_Live_Runtime_Exit_Control.md — [5] EXIT DISPATCH

Layer authority: L5 (cross-cutting policy plane — gate output only)
Write authority: NONE — all four types are frozen read-only stubs.
No business logic.  No durable writes.  No shadow-eval references.

Architectural invariants
------------------------
1. run_scope = 'CURRENT_RUN' (ClassVar) on all four types enforces separation from
   PromotionPacket (run_scope='FUTURE_RUN') at the type level.
2. CommitToUWGRequest carries only the state_diff stub and replay_key.
   The durable write authority belongs entirely to UWG (L4_state).  This stub is a
   request, not an authorization.  The UWG committer must validate it independently.
3. EscalateToHITLPacket carries bounded_context (sealed read-only dict) for the
   human reviewer.  The full HITL machinery lives in exit_control_hitl.py; this stub
   is only the trigger packet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from agentic_core.L5_safety.types.exit_disposition_types import ExitDisposition


@dataclass(frozen=True)
class AllowResponsePayload:
    """Outcome stub for ALLOW_RESPONSE — all four X1A-X1D dimensions passed.

    Carries the minimum contract for routing the cleared response out of the gate.
    """

    run_scope: ClassVar[str] = "CURRENT_RUN"

    eval_id: str
    trace_id: str
    artifact_id: str
    disposition: ExitDisposition = ExitDisposition.ALLOW_RESPONSE
    confidence_score: float = 0.0
    policy_hash: str | None = None
    compliance_hash: str | None = None


@dataclass(frozen=True)
class DenyReturnPayload:
    """Outcome stub for DENY_RETURN — one or more X1A-X1D dimensions failed.

    Carries the minimum contract for suppressing the response and logging the denial.
    failed_dimension mirrors the X1A/X1B/X1C/X1D label for triage.
    """

    run_scope: ClassVar[str] = "CURRENT_RUN"

    eval_id: str
    trace_id: str
    artifact_id: str
    reason: str
    disposition: ExitDisposition = ExitDisposition.DENY_RETURN
    failed_dimension: str = ""
    policy_hash: str | None = None


@dataclass(frozen=True)
class EscalateToHITLPacket:
    """Bounded stub for ESCALATE_TO_HITL — confidence below threshold or explicit reason.

    bounded_context is a sealed read-only dict carrying minimum reviewer context:
        - artifact_id
        - rubric_scores subset
        - integrity_checks subset
        - terminal_classification
    The HITL machinery (exit_control_hitl.py) owns the full escalation protocol.
    This stub is the trigger packet only.
    """

    run_scope: ClassVar[str] = "CURRENT_RUN"

    eval_id: str
    trace_id: str
    artifact_id: str
    reason: str
    disposition: ExitDisposition = ExitDisposition.ESCALATE_TO_HITL
    confidence_score: float = 0.0
    bounded_context: dict[str, Any] = field(default_factory=dict)
    policy_hash: str | None = None


@dataclass(frozen=True)
class CommitToUWGRequest:
    """Stub commit request for COMMIT_TO_UWG — authorized mutation proposal routed to UWG.

    state_diff is a copy of the sealed artifact's mutation proposal.
    replay_key is the determinism anchor required by UWG to validate the write.

    This is a REQUEST only.  The UWG committer (L4_state/enforcement/uwg_committer.py)
    owns write authority and must validate independently.  No durable write happens here.
    """

    run_scope: ClassVar[str] = "CURRENT_RUN"

    eval_id: str
    trace_id: str
    artifact_id: str
    state_diff: dict[str, Any]
    replay_key: str
    disposition: ExitDisposition = ExitDisposition.COMMIT_TO_UWG
    policy_hash: str | None = None
    compliance_hash: str | None = None


__all__ = [
    "AllowResponsePayload",
    "DenyReturnPayload",
    "EscalateToHITLPacket",
    "CommitToUWGRequest",
]
