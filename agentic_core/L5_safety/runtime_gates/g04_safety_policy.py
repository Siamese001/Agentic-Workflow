"""G04 — Safety / Policy Gate.

Spec: enforce active policy across request, plan, route, execution, exit.
Allowed decisions: ALLOW | DENY | SAFE_FALLBACK | SHRINK_SCOPE | ESCALATE_HITL | REROUTE.
Stop condition: missing/inconsistent policy_hash MUST block route/execution.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import allow, deny, escalate, register_gate
from agentic_core.L5_safety.runtime_gates.contracts import (
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

DISALLOWED_TRANSFORMS = {"build_weapon", "csam", "deanonymize_user", "exfil_secrets"}


@register_gate
class SafetyPolicyGate:
    GATE_ID = "G04"
    PRIMARY_LAYER = "L5"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        # Stop condition: policy_hash missing or inconsistent.
        if not ctx.policy_hash:
            signals.append(RegressionSignal(name="policy_mismatch_count", value=1.0, severity="alert"))
            return deny(self.GATE_ID, "missing_policy_hash")
        expected_hash = ctx.caller_scope_baseline.get("expected_policy_hash", "")
        if expected_hash and expected_hash != ctx.policy_hash:
            signals.append(RegressionSignal(name="policy_mismatch_count", value=1.0, severity="alert"))
            return deny(
                self.GATE_ID,
                "policy_hash_inconsistent",
                expected=expected_hash,
                actual=ctx.policy_hash,
            )
        risk = ctx.intent.get("safety_risk_class", "low")
        transform = ctx.intent.get("transform", "")
        if transform in DISALLOWED_TRANSFORMS:
            signals.append(
                RegressionSignal(name="unsafe_request_pass_through_count", value=1.0, severity="alert")
            )
            return deny(self.GATE_ID, "disallowed_transform", transform=transform)
        if risk == "high":
            return escalate(self.GATE_ID, "high_safety_risk_class", risk=risk)
        # Doctrine 00C parent FORBIDDEN OUTPUTS: gates emit verdicts only.
        # Surface the would-be compliance binding as verdict metadata; the
        # owner layer (U0/L5 policy plane) is responsible for committing it
        # to ctx. Mirror of G02's caller_scope_baseline_proposal pattern.
        decision = allow(self.GATE_ID, "policy_satisfied")
        if not ctx.compliance_hash:
            decision.metadata.setdefault(
                "compliance_hash_proposal",
                f"compliance::{ctx.policy_hash}",
            )
        return decision


__all__ = ["SafetyPolicyGate"]
