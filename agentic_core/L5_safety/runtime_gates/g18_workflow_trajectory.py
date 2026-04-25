"""G18 — Workflow Trajectory Gate.

Spec: control multi-step workflow behavior.
Stop: L3 MUST NOT re-decide L0 route or persist durable truth.
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
class WorkflowTrajectoryGate:
    GATE_ID = "G18"
    PRIMARY_LAYER = "L3"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        wf = ctx.workflow_state
        # Stop: L3 attempted route mutation or durable persist.
        if wf.get("attempts_route_mutation") or wf.get("attempts_durable_persist"):
            signals.append(
                RegressionSignal(name="scope_expansion_attempt_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.FAIL_WORKFLOW.value,
                reason_codes=["L3_overstepped_authority"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Dependencies satisfied?
        unsatisfied = wf.get("unsatisfied_dependencies", [])
        if unsatisfied:
            signals.append(RegressionSignal(name="dependency_violation_count", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.RETRY,
                alias=DecisionAlias.HOLD_NODE.value,
                reason_codes=["dependencies_unsatisfied"],
                signals=signals,
                metadata={"unsatisfied": unsatisfied},
            )
        # Handoff failure.
        if wf.get("handoff_failed"):
            signals.append(RegressionSignal(name="handoff_failure_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.REROUTE,
                reason_codes=["handoff_failure"],
                signals=signals,
            )
        # Branch independence violation.
        if wf.get("branches_share_state"):
            signals.append(RegressionSignal(name="branch_explosion_count", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.SHRINK_SCOPE,
                reason_codes=["branches_share_state"],
                signals=signals,
            )
        # Trajectory class drift.
        expected = wf.get("expected_trajectory_class", "")
        observed = wf.get("trajectory_class", "")
        if expected and observed and expected != observed:
            signals.append(RegressionSignal(name="unexpected_trajectory_class", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                reason_codes=["trajectory_class_drift"],
                signals=signals,
                metadata={"expected": expected, "observed": observed},
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            alias=DecisionAlias.CONTINUE.value,
            reason_codes=["trajectory_ok"],
            signals=signals,
        )


__all__ = ["WorkflowTrajectoryGate"]
