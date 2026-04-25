"""G07 — Route Selection Gate.

Spec: select the one governed runtime path. L0 emits exactly one
deterministic RouteContract. Stop condition: if RouteContract cannot be signed
or replayed, downstream MUST NOT proceed.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import deny, register_gate
from agentic_core.L5_safety.runtime_gates.types import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

REQUIRED_RC_FIELDS = (
    "route_id",
    "confidence",
    "reason_codes",
    "freshness_class",
    "cache_policy",
    "execution_form",
    "cost_tier",
    "fallback_chain",
    "slo",
    "tenant_scope",
    "hmac_sig",
)
ROUTE_ALIAS_MAP = {
    "R1_EXACT_CACHE": DecisionAlias.ROUTE_R1_EXACT_CACHE,
    "R1_SEMANTIC_CACHE": DecisionAlias.ROUTE_R1_SEMANTIC_CACHE,
    "R3_GROUNDED_READ": DecisionAlias.ROUTE_R3_GROUNDED_READ,
    "R4_SINGLE_ACTION": DecisionAlias.ROUTE_R4_SINGLE_ACTION,
    "R3_R4_MANAGED_WORKFLOW": DecisionAlias.ROUTE_R3_R4_MANAGED_WORKFLOW,
    "R5_FALLBACK": DecisionAlias.ROUTE_R5_FALLBACK,
}


@register_gate
class RouteSelectionGate:
    GATE_ID = "G07"
    PRIMARY_LAYER = "L0"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        rc = ctx.route_contract
        missing = [f for f in REQUIRED_RC_FIELDS if not rc.get(f)]
        if missing:
            signals.append(RegressionSignal(name="route_digest_mismatch", value=1.0, severity="alert"))
            return deny(self.GATE_ID, "incomplete_route_contract", missing=missing)
        # HMAC signature must be non-empty placeholder; orchestrator verifies cryptographically.
        if not rc.get("hmac_sig"):
            return deny(self.GATE_ID, "unsigned_route_contract")
        route_id = rc["route_id"]
        alias = ROUTE_ALIAS_MAP.get(route_id)
        if alias is None:
            signals.append(
                RegressionSignal(name="wrong_route_user_correction_rate", value=1.0, severity="warn")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.REROUTE,
                reason_codes=["unknown_route_id"],
                signals=signals,
            )
        # Confidence floor — low confidence routes mark degraded but allow.
        confidence = float(rc.get("confidence", 0.0))
        if confidence < 0.5:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                alias=alias.value,
                reason_codes=["low_route_confidence"],
                signals=signals,
                metadata={"confidence": confidence},
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            alias=alias.value,
            reason_codes=["route_signed"],
            signals=signals,
            metadata={"route_id": route_id, "confidence": confidence},
        )


__all__ = ["RouteSelectionGate"]
