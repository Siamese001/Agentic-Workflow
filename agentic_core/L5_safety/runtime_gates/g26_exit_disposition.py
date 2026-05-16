"""G26 — Exit Disposition Gate.

Spec: make final live decision for sealed runtime artifacts or RET short-circuits.
Stop: no sealed result may leave runtime without explicit exit disposition.
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
class ExitDispositionGate:
    GATE_ID = "G26"
    PRIMARY_LAYER = "Exit"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        out = ctx.output
        sealed = bool(out.get("sealed", False))
        if not sealed:
            signals.append(RegressionSignal(name="exit_denial_rate", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                reason_codes=["unsealed_artifact"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Validate sub-results required by spec.
        sub_results = out.get("sub_results", {}) or {}
        required = ("policy", "schema", "support", "safety", "sandbox", "mutation_authorization")
        missing = [k for k in required if sub_results.get(k) not in {"pass", "n/a"}]
        if missing:
            signals.append(RegressionSignal(name="exit_denial_rate", value=1.0, severity="warn"))
            # Distinguish soft fixes from hard fails.
            if any(sub_results.get(k) == "fail" for k in ("policy", "safety", "mutation_authorization")):
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.DENY,
                    reason_codes=["hard_subgate_fail"],
                    signals=signals,
                    metadata={"failing": [k for k in required if sub_results.get(k) == "fail"]},
                    stop_condition_violated=True,
                )
            if any(sub_results.get(k) == "fail" for k in ("schema", "support")):
                signals.append(RegressionSignal(name="reroute_rate", value=1.0, severity="warn"))
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.REROUTE,
                    reason_codes=["soft_subgate_fail_reroute"],
                    signals=signals,
                )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ABSTAIN,
                reason_codes=["incomplete_subgate_results"],
                signals=signals,
                metadata={"missing": missing},
            )
        # Commit-class artifact?
        if out.get("requires_commit"):
            signals.append(RegressionSignal(name="commit_request_rejection_rate", value=0.0, severity="info"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.COMMIT_REQUEST,
                alias=DecisionAlias.COMMIT.value,
                reason_codes=["routed_to_uwg"],
                signals=signals,
            )
        if out.get("requires_hitl"):
            signals.append(RegressionSignal(name="escalate_rate", value=1.0, severity="info"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ESCALATE_HITL,
                reason_codes=["explicit_hitl_required"],
                signals=signals,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            reason_codes=["exit_clear"],
            signals=signals,
        )


__all__ = ["ExitDispositionGate"]
