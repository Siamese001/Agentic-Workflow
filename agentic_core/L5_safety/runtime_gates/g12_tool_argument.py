"""G12 — Tool Argument Gate.

Spec: validate runtime tool arguments before invocation.
Stop: dangerous/mutating tool calls with ambiguous target MUST NOT execute.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import register_gate
from agentic_core.L5_safety.runtime_gates.contracts import (
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

WILDCARD_TOKENS = {"*", "**", ".*", "/*", ""}


@register_gate
class ToolArgumentGate:
    GATE_ID = "G12"
    PRIMARY_LAYER = "L2"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        call = ctx.tool_call
        args = call.get("args", {}) or {}
        is_mutating = bool(call.get("is_mutating", False))
        target = args.get("target", "")
        target_authority = call.get("target_authority", "")  # user_specified | policy_authorized | inferred
        # Schema validation (placeholder — orchestrator does jsonschema).
        if not call.get("args_schema_valid", True):
            signals.append(
                RegressionSignal(name="tool_arg_validation_failure_rate", value=1.0, severity="warn")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                reason_codes=["args_schema_invalid"],
                signals=signals,
            )
        # Stop: mutating with ambiguous/inferred target.
        if is_mutating and target_authority not in {"user_specified", "policy_authorized"}:
            signals.append(RegressionSignal(name="inferred_target_action_rate", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.CLARIFY,
                reason_codes=["mutating_inferred_target"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Wildcard scope rejection on risky actions.
        if is_mutating and (target in WILDCARD_TOKENS or any(w in str(target) for w in ("**", "/*"))):
            signals.append(
                RegressionSignal(name="broad_scope_arg_attempt_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.SHRINK_SCOPE,
                reason_codes=["wildcard_target_on_mutation"],
                signals=signals,
            )
        # Idempotency key for mutations.
        if is_mutating and not call.get("idempotency_key"):
            signals.append(RegressionSignal(name="idempotency_key_missing_count", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.RETRY,
                reason_codes=["idempotency_key_required"],
                signals=signals,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            reason_codes=["args_valid"],
            signals=signals,
        )


__all__ = ["ToolArgumentGate"]
