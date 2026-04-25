"""G02 — Identity / Tenant / Session Gate.

Spec: bind caller identity, tenant scope, session scope, region, access baseline.
Allowed decisions: ALLOW | DENY | RESTRICT | REDACT | ESCALATE_HITL.
Stop condition: if tenant/session boundary cannot be established, fail closed.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import allow, deny, register_gate
from agentic_core.L5_safety.runtime_gates.types import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)


@register_gate
class IdentitySessionGate:
    GATE_ID = "G02"
    PRIMARY_LAYER = "U0"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        # Stop condition: tenant + session must both resolve.
        if not ctx.tenant_id or not ctx.session_id:
            signals.append(RegressionSignal(name="session_scope_mismatch_count", value=1.0, severity="alert"))
            return deny(self.GATE_ID, "missing_tenant_or_session")
        # Cross-tenant near-miss detection: requested resource tenant differs from caller.
        requested_tenant = ctx.intent.get("requested_resource_tenant", "")
        if requested_tenant and requested_tenant != ctx.tenant_id:
            signals.append(RegressionSignal(name="cross_tenant_near_miss_count", value=1.0, severity="alert"))
            return deny(
                self.GATE_ID,
                "cross_tenant_attempt",
                requested_tenant=requested_tenant,
                caller_tenant=ctx.tenant_id,
            )
        # ACL: explicit deny list on caller_scope_baseline.allowed_resource_classes.
        requested_class = ctx.intent.get("resource_class", "")
        allowed_classes = ctx.caller_scope_baseline.get("allowed_resource_classes", [])
        if requested_class and allowed_classes and requested_class not in allowed_classes:
            signals.append(RegressionSignal(name="ACL_denial_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.RESTRICT.value,
                reason_codes=["acl_class_not_allowed"],
                signals=signals,
                metadata={"requested_class": requested_class},
            )
        # Stamp baseline (idempotent).
        ctx.caller_scope_baseline.setdefault("tenant_id", ctx.tenant_id)
        ctx.caller_scope_baseline.setdefault("session_id", ctx.session_id)
        return allow(self.GATE_ID, "identity_bound", signals=signals)


__all__ = ["IdentitySessionGate"]
