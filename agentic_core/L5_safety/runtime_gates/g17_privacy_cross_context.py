"""G17 — Privacy / Cross-Context Gate.

Spec: prevent user/tenant/session/connector/task data bleed.
Stop: cross-tenant / cross-session leakage MUST block output.
"""

from __future__ import annotations

import re

from agentic_core.L5_safety.runtime_gates.base import register_gate
from agentic_core.L5_safety.runtime_gates.types import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

PII_PATTERNS = (
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
    re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),  # credit card
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),  # email
)


@register_gate
class PrivacyCrossContextGate:
    GATE_ID = "G17"
    PRIMARY_LAYER = "L5"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        out = ctx.output
        # Stop: tenant ACL violation explicit signal.
        if out.get("tenant_acl_violation"):
            signals.append(RegressionSignal(name="tenant_acl_violation_count", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                reason_codes=["tenant_acl_violation"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Cross-session bleed — explicit flag from orchestrator.
        if out.get("cross_session_bleed"):
            signals.append(
                RegressionSignal(name="cross_context_near_miss_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.ISOLATE.value,
                reason_codes=["cross_session_bleed"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Connector permission staleness.
        if out.get("connector_permission_stale"):
            signals.append(
                RegressionSignal(name="connector_permission_error_rate", value=1.0, severity="warn")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.REQUIRE_PERMISSION.value,
                reason_codes=["stale_connector_permission"],
                signals=signals,
            )
        # PII / secret scrub.
        text = str(out.get("text", "") or "")
        hits = [p.pattern for p in PII_PATTERNS if p.search(text)]
        if hits:
            signals.append(RegressionSignal(name="redaction_event_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.REDACT,
                reason_codes=["pii_detected"],
                signals=signals,
                metadata={"hit_patterns": len(hits)},
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            reason_codes=["privacy_ok"],
            signals=signals,
        )


__all__ = ["PrivacyCrossContextGate"]
