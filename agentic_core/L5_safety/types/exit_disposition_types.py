"""Exit Disposition Types — L5 policy-plane ownership (HITL-003).

Defines ExitDisposition enum and ExitGateResult contract for the
X1A–X1D exit evaluation gate (docs/reference/05_Live_Runtime_Exit_Control.md).

Layer authority: L5 (cross-cutting policy plane).
L2 may import ExitDisposition from here; L5 must never import from L2 for this type.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "exit_disposition_types")
emit_determinism_digest("p0", "exit_disposition_types")
_emit_reads_policy_state("p1", "exit_disposition_types", "L5")
_emit_verifies_policy("p1", "exit_disposition_types", "policy_check")
_emit_verifies_boundary("p1", "exit_disposition_types", "boundary_check")
_emit_validated_by_safety_plane("p1", "exit_disposition_types", "safety_validation")
_emit_hard_fails_untranscripted("p1", "exit_disposition_types")
_emit_gated_by_confidence("p1", "exit_disposition_types", "confidence_gate")


class ExitDisposition(str, Enum):
    """The four and only four explicit outcomes of the exit control gate.

    Every execution path through ExitControlGate MUST produce one of these
    four values.  No catch-all, no None, no silent swallowing.

    ALLOW_RESPONSE    — artifact is safe, complete, grounded, replayable → send to caller
    DENY_RETURN       — artifact is unsafe or incomplete → return denial to caller, no commit
    ESCALATE_TO_HITL  — confidence below threshold or policy ambiguity → freeze and escalate
    COMMIT_TO_UWG     — artifact contains a durable mutation proposal → route to UWG
    """

    ALLOW_RESPONSE = "ALLOW_RESPONSE"
    DENY_RETURN = "DENY_RETURN"
    ESCALATE_TO_HITL = "ESCALATE_TO_HITL"
    COMMIT_TO_UWG = "COMMIT_TO_UWG"


@dataclass(frozen=True)
class ExitEvaluationDimensions:
    """Structured inputs to the four-dimensional X1A–X1D exit evaluation.

    X1A  rules_compliant      — output does not violate any policy rule
    X1B  answer_fit           — output answers the question actually asked
    X1C  safety_clear         — no secrets, PII, unsafe content, or injection residue
    X1D  grounded_replayable  — output is grounded in evidence and reproducible
    """

    rules_compliant: bool
    answer_fit: bool
    safety_clear: bool
    grounded_replayable: bool
    confidence_score: float
    has_commit_payload: bool = False
    escalation_reason: Optional[str] = None


@dataclass(frozen=True)
class ExitGateResult:
    """Typed output of ExitControlGate.evaluate().

    Carries the explicit ExitDisposition plus the evidence trail.
    Downstream consumers (outcome_logger, HITL trigger, UWG router) consume
    this object — never raw strings or dicts.
    """

    disposition: ExitDisposition
    trace_id: str
    dimensions: ExitEvaluationDimensions
    reason: str
    policy_hash: Optional[str] = None
    compliance_hash: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "disposition": self.disposition.value,
            "trace_id": self.trace_id,
            "reason": self.reason,
            "policy_hash": self.policy_hash,
            "compliance_hash": self.compliance_hash,
            "dimensions": {
                "rules_compliant": self.dimensions.rules_compliant,
                "answer_fit": self.dimensions.answer_fit,
                "safety_clear": self.dimensions.safety_clear,
                "grounded_replayable": self.dimensions.grounded_replayable,
                "confidence_score": self.dimensions.confidence_score,
                "has_commit_payload": self.dimensions.has_commit_payload,
                "escalation_reason": self.dimensions.escalation_reason,
            },
            "metadata": self.metadata,
        }
