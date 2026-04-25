"""G21 — Output Schema Gate.

Spec: ensure generated output conforms to required schema and format.
Stop: required schema failure MUST block exit unless safe fallback permitted.
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
class OutputSchemaGate:
    GATE_ID = "G21"
    PRIMARY_LAYER = "Exit"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        out = ctx.output
        required = bool(out.get("schema_required", False))
        valid = bool(out.get("schema_valid", True))
        repair_attempts = int(out.get("repair_attempts", 0))
        max_repair = int(out.get("max_repair", 1))
        repair_allowed = bool(out.get("repair_allowed", True))
        safe_fallback_allowed = bool(out.get("safe_fallback_allowed", False))
        missing_fields = out.get("missing_required_fields", []) or []
        missing_citations = bool(out.get("missing_citation_anchors", False))
        invalid_json = bool(out.get("invalid_json", False))
        if not required and valid:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ALLOW,
                reason_codes=["schema_not_required"],
                signals=signals,
            )
        if invalid_json:
            signals.append(RegressionSignal(name="invalid_json_rate", value=1.0, severity="warn"))
        if missing_fields:
            signals.append(RegressionSignal(name="missing_required_field_rate", value=1.0, severity="warn"))
        if missing_citations:
            signals.append(RegressionSignal(name="citation_anchor_missing_rate", value=1.0, severity="warn"))
        if not valid:
            signals.append(RegressionSignal(name="schema_failure_rate", value=1.0, severity="warn"))
            if repair_allowed and repair_attempts < max_repair:
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.RETRY,
                    alias=DecisionAlias.REPAIR.value,
                    reason_codes=["schema_repair_attempt"],
                    signals=signals,
                    metadata={"attempt": repair_attempts + 1, "max": max_repair},
                )
            if safe_fallback_allowed:
                return GateDecision(
                    gate_id=self.GATE_ID,
                    disposition=Disposition.SAFE_FALLBACK,
                    reason_codes=["schema_unrepairable_fallback"],
                    signals=signals,
                )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.REJECT.value,
                reason_codes=["schema_unrepairable"],
                signals=signals,
                stop_condition_violated=True,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            reason_codes=["schema_valid"],
            signals=signals,
        )


__all__ = ["OutputSchemaGate"]
