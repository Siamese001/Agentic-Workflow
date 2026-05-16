"""G28 — Audit / Trace Completeness Gate.

Spec: ensure runtime decisions are traceable and reviewable.
Stop: if audit-grade trace is required and missing, commit MUST be blocked
and exit may be blocked based on policy.
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

REQUIRED_SPANS = (
    "trace_root",
    "route_contract",
    "tool_invocations",
    "evidence_contracts",
    "step_outputs",
    "exit_disposition",
)


@register_gate
class AuditTraceCompletenessGate:
    GATE_ID = "G28"
    PRIMARY_LAYER = "L6"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        artifacts = ctx.trace_artifacts
        audit_required = bool(artifacts.get("audit_required", False))
        commit_in_run = bool(artifacts.get("commit_in_run", False))
        spans = artifacts.get("spans", {}) or {}
        missing = [s for s in REQUIRED_SPANS if not spans.get(s)]
        if missing:
            signals.append(
                RegressionSignal(
                    name="missing_span_rate", value=len(missing) / len(REQUIRED_SPANS), severity="warn"
                )
            )
        # Hash chain integrity.
        if commit_in_run and not artifacts.get("audit_hash_chain_ok", True):
            signals.append(RegressionSignal(name="audit_hash_mismatch", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.BLOCK_COMMIT,
                reason_codes=["audit_hash_mismatch"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Commit receipt required when commit happened.
        if commit_in_run and not spans.get("commit_receipts"):
            signals.append(
                RegressionSignal(name="invocation_record_missing_rate", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.BLOCK_COMMIT,
                reason_codes=["missing_commit_receipt"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Trace join failure.
        if artifacts.get("trace_join_failure"):
            signals.append(RegressionSignal(name="trace_join_failure_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                alias=DecisionAlias.NON_REPLAYABLE.value,
                reason_codes=["trace_join_failure"],
                signals=signals,
            )
        # Missing required spans + audit required = block.
        if missing and audit_required:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.BLOCK_EXIT.value,
                reason_codes=["audit_spans_missing"],
                signals=signals,
                metadata={"missing": missing},
                stop_condition_violated=True,
            )
        if missing:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.MARK_DEGRADED,
                reason_codes=["partial_audit_trace"],
                signals=signals,
                metadata={"missing": missing},
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            reason_codes=["audit_complete"],
            signals=signals,
        )


__all__ = ["AuditTraceCompletenessGate"]
