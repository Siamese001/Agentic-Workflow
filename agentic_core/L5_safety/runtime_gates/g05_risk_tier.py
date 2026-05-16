"""G05 — Risk Tier Gate.

Spec: set autonomy level based on risk, reversibility, blast radius, user explicitness.
Allowed decisions: ALLOW | SHRINK_SCOPE | ESCALATE_HITL | DENY | SAFE_FALLBACK.
Stop condition: high-impact irreversible action MUST NOT execute without HITL/user confirmation.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import allow, escalate, register_gate
from agentic_core.L5_safety.runtime_gates.contracts import (
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

SENSITIVE_DOMAINS = {"production", "financial", "legal", "medical", "security", "privacy", "customer_facing"}


@register_gate
class RiskTierGate:
    GATE_ID = "G05"
    PRIMARY_LAYER = "L5"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        impact_class = ctx.impact_class or ctx.intent.get("impact_class", "read")
        reversible = bool(
            ctx.reversible if ctx.reversible is not None else ctx.intent.get("reversible", True)
        )
        risk_tier = ctx.risk_tier or ctx.intent.get("risk_tier", "low")
        domains = set(ctx.intent.get("domains", []) or []) & SENSITIVE_DOMAINS
        user_explicit = bool(ctx.intent.get("user_explicit_consent", False))
        # Stop condition: high-impact irreversible without explicit HITL/user consent -> escalate.
        if impact_class in {"write", "egress"} and not reversible and not user_explicit:
            signals.append(
                RegressionSignal(name="unapproved_mutation_attempt_count", value=1.0, severity="alert")
            )
            return escalate(
                self.GATE_ID,
                "high_impact_irreversible",
                impact_class=impact_class,
                reversible=reversible,
            )
        if risk_tier == "high" or domains:
            signals.append(RegressionSignal(name="high_risk_action_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.SHRINK_SCOPE,
                reason_codes=["sensitive_domain" if domains else "high_risk_tier"],
                signals=signals,
                metadata={"domains": list(domains), "risk_tier": risk_tier},
            )
        return allow(self.GATE_ID, "risk_tier_acceptable", risk_tier=risk_tier)


__all__ = ["RiskTierGate"]
