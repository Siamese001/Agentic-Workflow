"""G16 — Memory Access Gate.

Spec: control read/write access to memory and durable state.
Stop: L1/L2/L6 MUST NOT directly mutate durable memory.
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

# Layers explicitly forbidden from direct durable memory mutation per spec.
NON_UWG_LAYERS = {"L1", "L2", "L6"}
SENSITIVE_TAGS = {"pii", "secret", "credential", "internal_only"}


@register_gate
class MemoryAccessGate:
    GATE_ID = "G16"
    PRIMARY_LAYER = "L4"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        op = ctx.memory_op
        kind = op.get("kind", "read")  # read | proposed_update
        caller_layer = op.get("caller_layer", "")
        tags = set(op.get("tags", []) or [])
        no_memory_mode = bool(op.get("no_memory_mode", False))
        if no_memory_mode:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.READ_DENY.value,
                reason_codes=["no_memory_mode"],
                signals=signals,
            )
        if kind == "read":
            if tags & SENSITIVE_TAGS and not op.get("sensitive_authorized"):
                signals.append(
                    RegressionSignal(name="sensitive_memory_trigger_count", value=1.0, severity="warn")
                )
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.REDACT,
                    reason_codes=["sensitive_memory_redacted"],
                    signals=signals,
                )
            tenant_match = op.get("tenant_match", True)
            if not tenant_match:
                signals.append(
                    RegressionSignal(name="cross_context_memory_near_miss_count", value=1.0, severity="alert")
                )
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.DENY,
                    alias=DecisionAlias.READ_DENY.value,
                    reason_codes=["tenant_mismatch"],
                    signals=signals,
                    stop_condition_violated=True,
                )
            if not op.get("relevant", True):
                signals.append(
                    RegressionSignal(name="irrelevant_memory_reference_rate", value=1.0, severity="info")
                )
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.SHRINK_SCOPE,
                    reason_codes=["irrelevant_memory"],
                    signals=signals,
                )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ALLOW,
                alias=DecisionAlias.READ_ALLOW.value,
                reason_codes=["read_allowed"],
                signals=signals,
            )
        # proposed_update path.
        if caller_layer in NON_UWG_LAYERS:
            signals.append(RegressionSignal(name="memory_write_rejection_rate", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.BLOCK_COMMIT,
                alias=DecisionAlias.BLOCK_UPDATE.value,
                reason_codes=["non_uwg_caller_blocked"],
                signals=signals,
                stop_condition_violated=True,
                metadata={"caller_layer": caller_layer},
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.COMMIT_REQUEST,
            alias=DecisionAlias.PROPOSE_UPDATE.value,
            reason_codes=["proposed_update_routed_to_uwg"],
            signals=signals,
        )


__all__ = ["MemoryAccessGate"]
