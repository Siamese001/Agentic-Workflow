"""G11 — Tool / Model Registry Gate.

Spec: ensure only approved tools/models/providers are invoked.
Stop: tool/model not on approved roster MUST NOT be invoked.
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


@register_gate
class ToolModelRegistryGate:
    GATE_ID = "G11"
    PRIMARY_LAYER = "L2"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        call = ctx.tool_call
        tool_id = call.get("tool_id", "")
        model_id = call.get("model_id", "")
        allowed_tools = set(call.get("allowed_tools", []) or [])
        allowed_models = set(call.get("allowed_models", []) or [])
        registry_digest_ok = bool(call.get("registry_digest_ok", True))
        if not registry_digest_ok:
            signals.append(
                RegressionSignal(name="registry_digest_mismatch_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.BLOCK.value,
                reason_codes=["registry_digest_mismatch"],
                signals=signals,
                stop_condition_violated=True,
            )
        if tool_id and allowed_tools and tool_id not in allowed_tools:
            signals.append(RegressionSignal(name="unknown_tool_attempt_count", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.BLOCK.value,
                reason_codes=["tool_not_on_roster"],
                signals=signals,
                metadata={"tool_id": tool_id},
                stop_condition_violated=True,
            )
        if model_id and allowed_models and model_id not in allowed_models:
            signals.append(RegressionSignal(name="provider_drift_count", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.BLOCK.value,
                reason_codes=["model_not_on_roster"],
                signals=signals,
                metadata={"model_id": model_id},
                stop_condition_violated=True,
            )
        if call.get("silent_fallback_attempted"):
            signals.append(
                RegressionSignal(name="silent_fallback_attempt_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.BLOCK.value,
                reason_codes=["silent_fallback_blocked"],
                signals=signals,
                stop_condition_violated=True,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            reason_codes=["registry_ok"],
            signals=signals,
        )


__all__ = ["ToolModelRegistryGate"]
