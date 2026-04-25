"""G25 — Runtime Regression / Anomaly Gate.

Spec: protect current run when live behavior deviates materially from
expected task-class baseline.
Stop: severe anomaly in high-risk action MUST pause or escalate before
action / egress / write.
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

# Spec-aligned: 3x baseline = severe; 1.5x = warn.
SEVERE_RATIO = 3.0
WARN_RATIO = 1.5


def _ratio(observed: float, expected: float) -> float:
    if expected <= 0:
        return 1.0
    return observed / expected


@register_gate
class RuntimeAnomalyGate:
    GATE_ID = "G25"
    PRIMARY_LAYER = "L6"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        baseline = ctx.baseline
        observed = ctx.observed
        if not baseline:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ALLOW,
                reason_codes=["no_baseline_available"],
                signals=signals,
            )
        anomalies: list[str] = []
        # Cost / token / latency anomaly detection.
        for metric, signal_name in (
            ("tokens", "cost_latency_anomaly"),
            ("cost_usd", "cost_latency_anomaly"),
            ("latency_ms", "cost_latency_anomaly"),
            ("tool_count", "tool_count_anomaly"),
            ("retry_count", "retry_anomaly"),
        ):
            obs = float(observed.get(metric, 0))
            exp = float(baseline.get(metric, 0))
            r = _ratio(obs, exp)
            if r >= SEVERE_RATIO:
                anomalies.append(f"{metric}_severe_{r:.1f}x")
                signals.append(RegressionSignal(name=signal_name, value=r, severity="alert"))
            elif r >= WARN_RATIO:
                signals.append(RegressionSignal(name=signal_name, value=r, severity="warn"))
        # Boolean anomalies.
        if observed.get("retrieval_weakness"):
            anomalies.append("retrieval_weakness")
            signals.append(RegressionSignal(name="support_score_anomaly", value=1.0, severity="warn"))
        if observed.get("safety_low_confidence"):
            anomalies.append("safety_low_confidence")
            signals.append(RegressionSignal(name="safety_confidence_anomaly", value=1.0, severity="alert"))
        if observed.get("schema_drift"):
            anomalies.append("schema_drift")
            signals.append(RegressionSignal(name="schema_drift_anomaly", value=1.0, severity="warn"))
        if observed.get("unusual_tool_action"):
            anomalies.append("unusual_tool_action")
            signals.append(RegressionSignal(name="tool_count_anomaly", value=1.0, severity="warn"))
        if observed.get("hitl_modify_spike"):
            signals.append(RegressionSignal(name="HITL_modify_spike", value=1.0, severity="warn"))
        # Stop: severe anomaly + high-risk current action.
        impact = ctx.impact_class or ctx.intent.get("impact_class", "")
        is_high_risk = impact in {"write", "egress"} or ctx.risk_tier == "high"
        severe = any("_severe_" in a or a == "safety_low_confidence" for a in anomalies)
        if severe and is_high_risk:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ESCALATE_HITL,
                alias=DecisionAlias.FORCE_HITL.value,
                reason_codes=["severe_anomaly_high_risk"],
                signals=signals,
                stop_condition_violated=True,
                metadata={"anomalies": anomalies},
            )
        if severe:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                alias=DecisionAlias.DOWNGRADE_AUTONOMY.value,
                reason_codes=["severe_anomaly"],
                signals=signals,
                metadata={"anomalies": anomalies},
            )
        if anomalies:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                reason_codes=["mild_anomaly"],
                signals=signals,
                metadata={"anomalies": anomalies},
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            alias=DecisionAlias.CONTINUE.value,
            reason_codes=["within_baseline"],
            signals=signals,
        )


__all__ = ["RuntimeAnomalyGate"]
