"""G22 — Output Quality Gate.

Spec: decide whether answer quality is acceptable before response leaves.
Stop: unsupported high-confidence claims MUST NOT exit.
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
class OutputQualityGate:
    GATE_ID = "G22"
    PRIMARY_LAYER = "Exit"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        out = ctx.output
        groundedness = float(out.get("groundedness", 1.0))
        faithfulness = float(out.get("faithfulness", 1.0))
        citation_support = float(out.get("citation_support", 1.0))
        completeness = float(out.get("completeness", 1.0))
        task_fit = float(out.get("task_fit", 1.0))
        confidence = float(out.get("confidence", 0.0))
        format_fit = bool(out.get("format_fit", True))
        # Stop: unsupported high-confidence claim.
        if confidence >= 0.8 and groundedness < 0.5:
            signals.append(RegressionSignal(name="hallucination_flag_rate", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.REVISE.value,
                reason_codes=["unsupported_high_confidence_claim"],
                signals=signals,
                stop_condition_violated=True,
            )
        if groundedness < 0.6 or faithfulness < 0.6:
            signals.append(RegressionSignal(name="groundedness_drop", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ABSTAIN,
                reason_codes=["weak_groundedness_or_faithfulness"],
                signals=signals,
            )
        if citation_support < 0.7:
            signals.append(RegressionSignal(name="citation_precision_drop", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.RETRY,
                alias=DecisionAlias.REVISE.value,
                reason_codes=["weak_citation_support"],
                signals=signals,
            )
        if completeness < 0.5 or task_fit < 0.5:
            signals.append(RegressionSignal(name="task_completion_drop", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.SAFE_FALLBACK,
                reason_codes=["incomplete_or_off_task"],
                signals=signals,
            )
        if not format_fit:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.RETRY,
                alias=DecisionAlias.REVISE.value,
                reason_codes=["format_mismatch"],
                signals=signals,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            reason_codes=["quality_ok"],
            signals=signals,
        )


__all__ = ["OutputQualityGate"]
