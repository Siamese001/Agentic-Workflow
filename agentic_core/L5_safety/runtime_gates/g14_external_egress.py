"""G14 — External Egress Gate.

Spec: govern calls outside the local runtime boundary.
Stop: external egress without approved provider mapping MUST fail closed.
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

SECRET_RE = re.compile(
    r"(?:sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|api[_-]?key\s*[:=]\s*\S+)",
    re.IGNORECASE,
)


@register_gate
class ExternalEgressGate:
    GATE_ID = "G14"
    PRIMARY_LAYER = "L2"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        call = ctx.tool_call
        provider = call.get("provider", "")
        approved = set(call.get("approved_providers", []) or [])
        if not provider:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ALLOW,
                reason_codes=["no_egress"],
                signals=signals,
            )
        if approved and provider not in approved:
            signals.append(RegressionSignal(name="external_egress_denial_rate", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                reason_codes=["unapproved_provider"],
                signals=signals,
                metadata={"provider": provider},
                stop_condition_violated=True,
            )
        if call.get("provider_fallback_attempted"):
            signals.append(
                RegressionSignal(name="provider_fallback_attempt_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                reason_codes=["silent_provider_fallback_blocked"],
                signals=signals,
                stop_condition_violated=True,
            )
        payload = str(call.get("egress_payload", "") or "")
        if SECRET_RE.search(payload):
            signals.append(RegressionSignal(name="secret_redaction_count", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.REDACT,
                alias=DecisionAlias.REDACT_AND_ALLOW.value,
                reason_codes=["secret_in_egress_payload"],
                signals=signals,
            )
        if call.get("unexpected_network_call"):
            signals.append(RegressionSignal(name="unexpected_network_call_count", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ESCALATE_HITL,
                reason_codes=["unexpected_network_call"],
                signals=signals,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            reason_codes=["egress_approved"],
            signals=signals,
        )


__all__ = ["ExternalEgressGate"]
