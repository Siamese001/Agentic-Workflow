"""L1PlanContract — mandatory typed output of L1 reasoning (B04 — GAP-002, REQ-003).

L1 reasoning MUST produce this contract.  L0 routing MUST validate it before
consuming.  grounding_required=True forces the C0 retrieval path.

Layer authority: L1 (cognition plane).
L0 imports L1PlanContract for consumption; L1 must never import from L0 for this type.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_dispatches_execution_plan,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "plan_contract_types")
emit_determinism_digest("p0", "plan_contract_types")
_emit_reads_policy_state("p1", "plan_contract_types", "L1")
_emit_verifies_policy("p1", "plan_contract_types", "plan_policy_check")
_emit_verifies_boundary("p1", "plan_contract_types", "plan_boundary_check")
_emit_hard_fails_untranscripted("p1", "plan_contract_types")
_emit_gated_by_confidence("p1", "plan_contract_types", "plan_confidence_gate")
_emit_dispatches_execution_plan("p1", "plan_contract_types", "l1_plan_dispatch")


class PlanContractViolation(ValueError):
    """Raised when L1PlanContract validation fails at the reasoning chokepoint.

    L0 must not consume L1 output that fails this check.
    """


class ReasoningMode(str, Enum):
    """How L1 determined the plan."""

    CHAIN_OF_THOUGHT = "CHAIN_OF_THOUGHT"
    REACT = "REACT"
    DIRECT = "DIRECT"
    DECOMPOSED = "DECOMPOSED"


@dataclass(frozen=True)
class L1PlanContract:
    """Mandatory typed output of L1 reasoning (REQ-003).

    All seven fields are required.  grounding_required drives C0 retrieval.
    L0 router validates this contract before dispatching.

    Fields:
        plan_id           — unique identifier for this plan instance
        request_id        — the upstream request this plan serves
        policy_hash       — hash of the policy snapshot used during reasoning
        reasoning_mode    — ReasoningMode enum value
        grounding_required — if True, L0 MUST invoke C0 retrieval before dispatch
        confidence_score  — 0.0–1.0; below threshold triggers ESCALATE_TO_HITL at exit gate
        steps             — ordered list of plan step dicts (non-empty)
    """

    plan_id: str
    request_id: str
    policy_hash: str
    reasoning_mode: ReasoningMode
    grounding_required: bool
    confidence_score: float
    steps: tuple

    _REQUIRED_FIELDS: tuple = field(
        default=(
            "plan_id",
            "request_id",
            "policy_hash",
            "reasoning_mode",
            "grounding_required",
            "confidence_score",
            "steps",
        ),
        init=False,
        repr=False,
        compare=False,
    )

    def validate(self) -> None:
        """Raise PlanContractViolation if any mandatory field is missing or invalid.

        Called by reasoning_chokepoint before returning plan to L0.
        """
        missing = []
        for f in self._REQUIRED_FIELDS:
            val = getattr(self, f, None)
            if val is None:
                missing.append(f)
        if missing:
            raise PlanContractViolation(
                f"L1PlanContract is missing mandatory fields: {missing}. "
                "All L1 reasoning paths must produce a complete plan contract."
            )
        if not isinstance(self.reasoning_mode, ReasoningMode):
            raise PlanContractViolation(
                f"reasoning_mode must be a ReasoningMode enum, got {type(self.reasoning_mode)}"
            )
        if not (0.0 <= self.confidence_score <= 1.0):
            raise PlanContractViolation(
                f"confidence_score must be in [0.0, 1.0], got {self.confidence_score}"
            )
        if isinstance(self.steps, str) or not hasattr(self.steps, "__iter__"):
            raise PlanContractViolation(
                "steps must be a tuple or list of plan step dicts, not a bare string or non-sequence."
            )
        if not self.steps:
            raise PlanContractViolation(
                "steps must be a non-empty sequence — L1 must produce at least one plan step."
            )
        if not self.plan_id.strip():
            raise PlanContractViolation("plan_id must be a non-empty string.")
        if not self.request_id.strip():
            raise PlanContractViolation("request_id must be a non-empty string.")
        if not self.policy_hash.strip():
            raise PlanContractViolation("policy_hash must be a non-empty string.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "request_id": self.request_id,
            "policy_hash": self.policy_hash,
            "reasoning_mode": self.reasoning_mode.value,
            "grounding_required": self.grounding_required,
            "confidence_score": self.confidence_score,
            "steps": list(self.steps),
        }
