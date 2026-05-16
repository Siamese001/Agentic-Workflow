"""G03 — Intent / Ambiguity Gate.

Spec: ensure the system understands enough to act safely.
Allowed decisions: ALLOW | CLARIFY | ABSTAIN | SAFE_FALLBACK | SHRINK_SCOPE.
Stop condition: ambiguity affecting irreversible action / external egress / durable
write MUST clarify or escalate before action.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import allow, register_gate
from agentic_core.L5_safety.runtime_gates.contracts import (
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

AMBIGUITY_FIELDS = ("target", "action", "recipient", "file", "data_source", "time_range", "write_scope")
HIGH_RISK_FORMS = {"external_action", "durable_write", "workflow"}


@register_gate
class IntentAmbiguityGate:
    GATE_ID = "G03"
    PRIMARY_LAYER = "L1"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        intent = ctx.intent
        # Required: identify primary objective + deliverable.
        objective = intent.get("objective", "")
        deliverable = intent.get("deliverable", "")
        if not objective or not deliverable:
            signals.append(RegressionSignal(name="clarification_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.CLARIFY,
                reason_codes=["missing_objective_or_deliverable"],
                signals=signals,
            )
        ambiguous = [f for f in AMBIGUITY_FIELDS if intent.get(f) == "ambiguous"]
        ask_form = intent.get(
            "ask_form", "read_only"
        )  # read_only | answer_only | external_action | durable_write | workflow
        # Stop condition: ambiguity affecting irreversible action / egress / write.
        if ambiguous and ask_form in HIGH_RISK_FORMS:
            signals.append(RegressionSignal(name="ambiguous_action_attempts", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.CLARIFY,
                reason_codes=["high_risk_ambiguity"],
                signals=signals,
                metadata={"ambiguous_fields": ambiguous, "ask_form": ask_form},
                stop_condition_violated=True,
            )
        if ambiguous:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.SHRINK_SCOPE,
                reason_codes=["benign_ambiguity_shrink"],
                signals=signals,
                metadata={"ambiguous_fields": ambiguous},
            )
        return allow(self.GATE_ID, "intent_clear")


__all__ = ["IntentAmbiguityGate"]
