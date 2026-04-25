"""G19 — Loop / Retry / Thrash Gate.

Spec: stop unproductive agent loops.
Stop: repeated unproductive retries MUST terminate or escalate.
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

DEFAULT_MAX_ITERATIONS = 10
DEFAULT_MAX_RETRY = 3


@register_gate
class LoopRetryThrashGate:
    GATE_ID = "G19"
    PRIMARY_LAYER = "L3"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        wf = ctx.workflow_state
        attempts = int(wf.get("attempt_count", 0))
        retries = int(wf.get("retry_count", 0))
        max_iter = int(wf.get("max_iterations", DEFAULT_MAX_ITERATIONS))
        max_retry = int(wf.get("max_retry", DEFAULT_MAX_RETRY))
        repeated_error = bool(wf.get("repeated_same_error", False))
        oscillation = bool(wf.get("oscillation_detected", False))
        no_new_signal = bool(wf.get("no_new_signal_loop", False))
        if attempts >= max_iter:
            signals.append(RegressionSignal(name="max_iteration_hit_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.STOP.value,
                reason_codes=["max_iterations_exceeded"],
                signals=signals,
                stop_condition_violated=True,
                metadata={"attempts": attempts, "max": max_iter},
            )
        if retries >= max_retry:
            signals.append(RegressionSignal(name="retry_thrash_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ESCALATE_HITL,
                reason_codes=["retry_ceiling_hit"],
                signals=signals,
                stop_condition_violated=True,
            )
        if repeated_error:
            signals.append(RegressionSignal(name="repeated_error_code_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.HEAL,
                reason_codes=["repeated_error_heal_path"],
                signals=signals,
            )
        if oscillation:
            signals.append(RegressionSignal(name="oscillation_detected_count", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.REROUTE,
                reason_codes=["oscillation_reroute"],
                signals=signals,
            )
        if no_new_signal:
            signals.append(RegressionSignal(name="no_new_signal_loop_count", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.SAFE_FALLBACK,
                alias=DecisionAlias.RETURN_BEST_PARTIAL.value,
                reason_codes=["no_new_signal_partial"],
                signals=signals,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            alias=DecisionAlias.CONTINUE.value,
            reason_codes=["loop_healthy"],
            signals=signals,
        )


__all__ = ["LoopRetryThrashGate"]
