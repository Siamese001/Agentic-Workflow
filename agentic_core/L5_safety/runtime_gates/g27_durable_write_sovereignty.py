"""G27 — Durable Write Sovereignty Gate.

Spec: ensure all real mutations go through Universal Write Gateway only.
Stop: no direct L2, L3, HITL, or L6 durable write is allowed.
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

NON_UWG_CALLERS = {"L2", "L3", "L6", "HITL"}


@register_gate
class DurableWriteSovereigntyGate:
    GATE_ID = "G27"
    PRIMARY_LAYER = "UWG"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        write = ctx.memory_op
        is_proposed_mutation = bool(write.get("is_proposed_mutation", False))
        caller_layer = write.get("caller_layer", "")
        if not is_proposed_mutation:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ALLOW,
                alias=DecisionAlias.NO_WRITE.value,
                reason_codes=["answer_only"],
                signals=signals,
            )
        # Stop: non-UWG caller proposing direct write.
        if caller_layer in NON_UWG_CALLERS:
            signals.append(RegressionSignal(name="ghost_write_attempt_count", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.BLOCK_COMMIT,
                alias=DecisionAlias.REJECT_WRITE.value,
                reason_codes=["non_uwg_direct_write"],
                signals=signals,
                metadata={"caller_layer": caller_layer},
                stop_condition_violated=True,
            )
        # Required write metadata.
        if not write.get("signature_valid", True):
            signals.append(RegressionSignal(name="write_rejection_rate", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.BLOCK_COMMIT,
                reason_codes=["invalid_signature"],
                signals=signals,
                stop_condition_violated=True,
            )
        if not ctx.compliance_hash or not ctx.policy_hash:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.BLOCK_COMMIT,
                reason_codes=["missing_compliance_or_policy_hash"],
                signals=signals,
                stop_condition_violated=True,
            )
        if not write.get("capability_token_authorizes_write", True):
            signals.append(RegressionSignal(name="write_rejection_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.REQUIRE_HITL.value,
                reason_codes=["capability_token_insufficient"],
                signals=signals,
            )
        if write.get("blast_radius_too_wide"):
            signals.append(RegressionSignal(name="out_of_scope_diff_count", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ESCALATE_HITL,
                alias=DecisionAlias.REQUIRE_HITL.value,
                reason_codes=["wide_blast_radius"],
                signals=signals,
            )
        if not write.get("write_lock_claimed", True):
            signals.append(RegressionSignal(name="write_lock_conflict_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.RETRY,
                alias=DecisionAlias.LOCK_SUBSTRATE.value,
                reason_codes=["write_lock_unavailable"],
                signals=signals,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.COMMIT_REQUEST,
            alias=DecisionAlias.COMMIT.value,
            reason_codes=["uwg_authorized_commit"],
            signals=signals,
        )


__all__ = ["DurableWriteSovereigntyGate"]
