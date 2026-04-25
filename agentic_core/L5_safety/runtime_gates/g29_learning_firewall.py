"""G29 — Learning Firewall Gate.

Spec: prevent L6 learning, shadow evaluation, or meta-learning from
mutating current run.
Stop: learning signals MUST NOT mutate or rescue completed current run.
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
class LearningFirewallGate:
    GATE_ID = "G29"
    PRIMARY_LAYER = "L6"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        sig = ctx.learning_signal
        attempts_current_run_mutation = bool(sig.get("attempts_current_run_mutation", False))
        attempts_l4_direct_write = bool(sig.get("attempts_l4_direct_write", False))
        run_status = sig.get("run_status", "in_progress")
        # Stop: learning attempting to mutate current run.
        if attempts_current_run_mutation:
            signals.append(
                RegressionSignal(name="live_learning_mutation_attempt_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.BLOCK_LIVE_MUTATION.value,
                reason_codes=["learning_attempted_current_run_mutation"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Stop: L6 attempting direct L4 write.
        if attempts_l4_direct_write:
            signals.append(
                RegressionSignal(name="rubric_drift_without_receipt_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.BLOCK_COMMIT,
                alias=DecisionAlias.BLOCK_LIVE_MUTATION.value,
                reason_codes=["L6_direct_L4_write_blocked"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Promotion attempt without approval.
        if sig.get("attempts_promotion_without_approval"):
            signals.append(
                RegressionSignal(name="unapproved_promotion_attempt_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.REJECT_PROMOTION.value,
                reason_codes=["unapproved_promotion"],
                signals=signals,
            )
        # Shadow eval bleed into runtime.
        if sig.get("shadow_eval_bleed"):
            signals.append(
                RegressionSignal(name="shadow_eval_to_runtime_bleed_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.BLOCK_LIVE_MUTATION.value,
                reason_codes=["shadow_eval_runtime_bleed"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Proposed update for future runs only.
        if sig.get("proposes_update"):
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.COMMIT_REQUEST,
                alias=DecisionAlias.UWG_COMMIT_AFTER_APPROVAL.value,
                reason_codes=["proposed_future_update_via_uwg"],
                signals=signals,
            )
        # Sealed run: archive only.
        if run_status == "sealed":
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ALLOW,
                alias=DecisionAlias.ARCHIVE.value,
                reason_codes=["archive_only"],
                signals=signals,
            )
        # In-progress run: hold for review at end.
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.MARK_DEGRADED,
            alias=DecisionAlias.HOLD_FOR_REVIEW.value,
            reason_codes=["hold_for_post_run_review"],
            signals=signals,
        )


__all__ = ["LearningFirewallGate"]
