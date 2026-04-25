"""G06 — HITL Approval Gate.

Spec: pause live execution when human authorization is required. Treats
human input as data, not sovereign authority. Re-clears human-modified
output through L5. Preserves audit trail of approve/modify/reject.

Allowed decisions: ESCALATE_HITL | APPROVE_TO_CONTINUE | MODIFY_THEN_RECLEAR
                  | REJECT | RETURN_TO_L1 | BLOCK_COMMIT.
Stop condition: human approval MUST NOT bypass L5 re-clearance or UWG write path.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import escalate, register_gate
from agentic_core.L5_safety.runtime_gates.types import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)


@register_gate
class HITLApprovalGate:
    GATE_ID = "G06"
    PRIMARY_LAYER = "L5"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        hitl = ctx.hitl
        if not hitl.get("review_requested"):
            return escalate(self.GATE_ID, "no_review_request", note="initialize escalation packet")
        verdict = hitl.get("verdict", "pending")
        latency_ms = float(hitl.get("latency_ms", 0))
        signals.append(RegressionSignal(name="HITL_approval_latency", value=latency_ms, severity="info"))
        if verdict == "approve":
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ALLOW,
                alias=DecisionAlias.APPROVE_TO_CONTINUE.value,
                reason_codes=["human_approved"],
                signals=signals,
            )
        if verdict == "modify":
            # Modified outputs MUST be re-cleared through L5 (the orchestrator)
            # rather than allowed to bypass safety. Stop condition guard.
            signals.append(RegressionSignal(name="HITL_modify_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.RETRY,
                alias=DecisionAlias.MODIFY_THEN_RECLEAR.value,
                reason_codes=["human_modified_requires_reclear"],
                signals=signals,
            )
        if verdict == "reject":
            signals.append(RegressionSignal(name="HITL_rejection_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.REJECT.value,
                reason_codes=["human_rejected"],
                signals=signals,
                stop_condition_violated=True,
            )
        if verdict == "return_to_l1":
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.REROUTE,
                alias=DecisionAlias.RETURN_TO_L1.value,
                reason_codes=["return_to_l1"],
                signals=signals,
            )
        # Pending verdict.
        return escalate(self.GATE_ID, "verdict_pending", verdict=verdict)


__all__ = ["HITLApprovalGate"]
