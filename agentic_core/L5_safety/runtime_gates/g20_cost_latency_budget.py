"""G20 — Cost / Latency / Budget Gate.

Spec: prevent runaway runtime cost, latency, and resource consumption.
Stop: exhausted budget MUST prevent additional autonomous steps.
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
class CostLatencyBudgetGate:
    GATE_ID = "G20"
    PRIMARY_LAYER = "L3"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        b = ctx.budget
        used_tokens = int(b.get("used_tokens", 0))
        max_tokens = int(b.get("max_tokens", 1_000_000))
        used_tool_calls = int(b.get("used_tool_calls", 0))
        max_tool_calls = int(b.get("max_tool_calls", 50))
        used_model_calls = int(b.get("used_model_calls", 0))
        max_model_calls = int(b.get("max_model_calls", 30))
        elapsed_ms = float(b.get("elapsed_ms", 0))
        slo_ms = float(b.get("slo_ms", 30_000))
        cost_usd = float(b.get("cost_usd", 0))
        max_cost_usd = float(b.get("max_cost_usd", 1.0))
        # Stop: token / cost / call exhaustion.
        if used_tokens >= max_tokens:
            signals.append(RegressionSignal(name="tokens_per_task_spike", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.STOP_ITERATION.value,
                reason_codes=["token_budget_exhausted"],
                signals=signals,
                stop_condition_violated=True,
            )
        if cost_usd >= max_cost_usd:
            signals.append(RegressionSignal(name="cost_per_task_spike", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.STOP_ITERATION.value,
                reason_codes=["cost_budget_exhausted"],
                signals=signals,
                stop_condition_violated=True,
            )
        if used_tool_calls >= max_tool_calls:
            signals.append(RegressionSignal(name="tool_calls_per_task_spike", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.STOP_ITERATION.value,
                reason_codes=["tool_call_ceiling"],
                signals=signals,
                stop_condition_violated=True,
            )
        if used_model_calls >= max_model_calls:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.STOP_ITERATION.value,
                reason_codes=["model_call_ceiling"],
                signals=signals,
                stop_condition_violated=True,
            )
        if elapsed_ms >= slo_ms:
            signals.append(RegressionSignal(name="p95_latency_spike", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.SAFE_FALLBACK,
                alias=DecisionAlias.TIMEOUT.value,
                reason_codes=["slo_breached"],
                signals=signals,
            )
        # Soft warnings — encourage downgrade well before exhaustion.
        if used_tokens > 0.8 * max_tokens or cost_usd > 0.8 * max_cost_usd:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.SHRINK_SCOPE,
                alias=DecisionAlias.DEGRADE_MODEL_TIER.value,
                reason_codes=["budget_pressure_80pct"],
                signals=signals,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            alias=DecisionAlias.CONTINUE.value,
            reason_codes=["budget_ok"],
            signals=signals,
        )


__all__ = ["CostLatencyBudgetGate"]
