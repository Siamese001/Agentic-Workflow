"""G08 — Retrieval / Grounding Gate.

Spec: determine whether grounded evidence is required and whether retrieval
can safely support the task. Stop: if factual claim requires evidence and
evidence is empty/blocked, abstain/caveat/fallback.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import register_gate
from agentic_core.L5_safety.runtime_gates.types import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

ALLOWED_MODES = {"dense", "sparse_bm25", "graph", "metadata", "cache"}
MAX_REFINE_ATTEMPTS = 3


@register_gate
class RetrievalGroundingGate:
    GATE_ID = "G08"
    PRIMARY_LAYER = "C0"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        plan = ctx.retrieval_plan
        grounding_required = bool(plan.get("grounding_required", False))
        modes = set(plan.get("modes", []) or [])
        blocked_sources = bool(plan.get("blocked_sources", False))
        refine_attempts = int(plan.get("refine_attempts", 0))
        if not grounding_required:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ALLOW,
                alias=DecisionAlias.PASS_AS_DATA.value,
                reason_codes=["grounding_not_required"],
                signals=signals,
            )
        # Stop condition: blocked sources for required grounding -> abstain.
        if blocked_sources:
            signals.append(RegressionSignal(name="ACL_block_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ABSTAIN,
                reason_codes=["sources_blocked"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Empty retrieval -> abstain.
        if plan.get("candidate_count", 0) == 0:
            signals.append(RegressionSignal(name="retrieval_empty_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ABSTAIN,
                reason_codes=["empty_retrieval"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Refine bound.
        if refine_attempts > MAX_REFINE_ATTEMPTS:
            signals.append(RegressionSignal(name="max_refine_exceeded_count", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.SAFE_FALLBACK,
                reason_codes=["max_refine_exceeded"],
                signals=signals,
            )
        # Mode validation.
        invalid = modes - ALLOWED_MODES
        if invalid:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                reason_codes=["disallowed_retrieval_mode"],
                signals=signals,
                metadata={"invalid_modes": sorted(invalid)},
                stop_condition_violated=True,
            )
        # Weak support -> refine once.
        if float(plan.get("support_score", 1.0)) < 0.5:
            signals.append(RegressionSignal(name="weak_support_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.RETRY,
                alias=DecisionAlias.REFINE_RETRIEVAL.value,
                reason_codes=["weak_support"],
                signals=signals,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            alias=DecisionAlias.RETRIEVE.value,
            reason_codes=["retrieval_ok"],
            signals=signals,
        )


__all__ = ["RetrievalGroundingGate"]
