"""G09 — Evidence Quality Gate.

Spec: verify evidence is strong enough to support an answer/action.
Stop condition: no answer may present unsupported evidence as certain.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import register_gate
from agentic_core.L5_safety.runtime_gates.contracts import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)


@register_gate
class EvidenceQualityGate:
    GATE_ID = "G09"
    PRIMARY_LAYER = "C0"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        ev = ctx.evidence
        sources = ev.get("source_ids", [])
        if not sources:
            signals.append(
                RegressionSignal(name="evidence_contract_failure_rate", value=1.0, severity="warn")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ABSTAIN,
                alias=DecisionAlias.EMPTY.value,
                reason_codes=["no_sources"],
                signals=signals,
                stop_condition_violated=True,
            )
        if not ev.get("source_resolution_ok", True):
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.BLOCKED.value,
                reason_codes=["source_unresolvable"],
                signals=signals,
                stop_condition_violated=True,
            )
        if ev.get("contradictions", 0) > 0:
            signals.append(RegressionSignal(name="contradiction_hidden_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                alias=DecisionAlias.CONFLICTED.value,
                reason_codes=["contradictions_present"],
                signals=signals,
            )
        support = float(ev.get("support_score", 0.0))
        coverage = float(ev.get("coverage", 0.0))
        if support < 0.4 or coverage < 0.4:
            signals.append(RegressionSignal(name="citation_support_rate_drop", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.RETRY,
                alias=DecisionAlias.REFINE_ONCE.value,
                reason_codes=["weak_evidence"],
                signals=signals,
                metadata={"support": support, "coverage": coverage},
            )
        if support < 0.7 or coverage < 0.6:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                alias=DecisionAlias.WEAK_WITH_CAVEATS.value,
                reason_codes=["weak_with_caveats"],
                signals=signals,
            )
        if not ev.get("cited_spans"):
            signals.append(RegressionSignal(name="unsupported_inference_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                alias=DecisionAlias.WEAK_WITH_CAVEATS.value,
                reason_codes=["missing_cited_spans"],
                signals=signals,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            alias=DecisionAlias.PASS.value,
            reason_codes=["evidence_strong"],
            signals=signals,
        )


__all__ = ["EvidenceQualityGate"]
