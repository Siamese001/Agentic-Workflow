"""G06 — HITL Approval Gate.

Spec: pause live execution when human authorization is required. Treats
human input as data, not sovereign authority. Re-clears human-modified
output through L5. Preserves audit trail of approve/modify/reject.

Allowed decisions: ESCALATE_HITL | APPROVE_TO_CONTINUE | MODIFY_THEN_RECLEAR
                  | REJECT | RETURN_TO_L1 | BLOCK_COMMIT.
Stop condition: human approval MUST NOT bypass L5 re-clearance or UWG write path.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import escalate, register_gate
from agentic_core.L5_safety.runtime_gates.types import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)


@register_gate
class HITLApprovalGate:
    GATE_ID = "G06"
    PRIMARY_LAYER = "L5"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        hitl = ctx.hitl
        if not hitl.get("review_requested"):
            decision = escalate(self.GATE_ID, "no_review_request", note="initialize escalation packet")
            _record_hitl_decision(decision, verdict="no_review_request", review_requested=False, latency_ms=0.0)
            return decision
        verdict = hitl.get("verdict", "pending")
        latency_ms = float(hitl.get("latency_ms", 0))
        signals.append(RegressionSignal(name="HITL_approval_latency", value=latency_ms, severity="info"))
        if verdict == "approve":
            decision = GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ALLOW,
                alias=DecisionAlias.APPROVE_TO_CONTINUE.value,
                reason_codes=["human_approved"],
                signals=signals,
            )
            _record_hitl_decision(decision, verdict=verdict, review_requested=True, latency_ms=latency_ms)
            return decision
        if verdict == "modify":
            # Modified outputs MUST be re-cleared through L5 (the orchestrator)
            # rather than allowed to bypass safety. Stop condition guard.
            signals.append(RegressionSignal(name="HITL_modify_rate", value=1.0, severity="warn"))
            decision = GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.RETRY,
                alias=DecisionAlias.MODIFY_THEN_RECLEAR.value,
                reason_codes=["human_modified_requires_reclear"],
                signals=signals,
            )
            _record_hitl_decision(decision, verdict=verdict, review_requested=True, latency_ms=latency_ms)
            return decision
        if verdict == "reject":
            signals.append(RegressionSignal(name="HITL_rejection_rate", value=1.0, severity="warn"))
            decision = GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.REJECT.value,
                reason_codes=["human_rejected"],
                signals=signals,
                stop_condition_violated=True,
            )
            _record_hitl_decision(decision, verdict=verdict, review_requested=True, latency_ms=latency_ms)
            return decision
        if verdict == "return_to_l1":
            decision = GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.REROUTE,
                alias=DecisionAlias.RETURN_TO_L1.value,
                reason_codes=["return_to_l1"],
                signals=signals,
            )
            _record_hitl_decision(decision, verdict=verdict, review_requested=True, latency_ms=latency_ms)
            return decision
        # Pending verdict.
        decision = escalate(self.GATE_ID, "verdict_pending", verdict=verdict)
        _record_hitl_decision(decision, verdict=verdict, review_requested=True, latency_ms=latency_ms)
        return decision


# =====================================================================
# Constitutional §29 — closed-loop wiring (W5.8)
# =====================================================================
import logging as _logging  # noqa: E402

_HITL_LOGGER = _logging.getLogger(__name__)
_HITL_HELPER = None  # type: ignore[var-annotated]


def _get_hitl_helper():
    """Lazy singleton for the L5/hitl RouterClosedLoopHelper."""
    global _HITL_HELPER  # noqa: PLW0603
    if _HITL_HELPER is not None:
        return _HITL_HELPER
    try:
        from tools.ledgers.router_helper import RouterClosedLoopHelper  # noqa: PLC0415

        _HITL_HELPER = RouterClosedLoopHelper(
            layer="L5",
            router="hitl",
            ledger_name="router_l5_hitl",
            repo_area="agentic_core/L5_safety/runtime_gates/g06_hitl_approval.py",
        )
        return _HITL_HELPER
    except ImportError:  # guardian: allow-log-and-swallow -- helper unavailable must not break HITL gate
        _HITL_LOGGER.debug("RouterClosedLoopHelper unavailable for L5/hitl", exc_info=True)
        return None


def _record_hitl_decision(
    decision: GateDecision,
    *,
    verdict: str,
    review_requested: bool,
    latency_ms: float,
) -> None:
    """Record HITL gate decision + bind outcome.

    Decision-and-outcome-in-one-shot. The "success" semantic is:
    - approve / return_to_l1 → success=True (forward progress)
    - modify / reject / escalate / pending → success=False (delayed/halted)

    Fail-soft: any helper failure is swallowed.
    """
    helper = _get_hitl_helper()
    if helper is None:
        return
    try:
        verdict_str = str(verdict)
        # Map verdicts to a stable cell label
        if verdict_str in {"approve"}:
            verdict_class = "approved"
            predicted_p = 1.0
            success = True
        elif verdict_str in {"return_to_l1"}:
            verdict_class = "rerouted"
            predicted_p = 0.7
            success = True
        elif verdict_str in {"modify"}:
            verdict_class = "modified"
            predicted_p = 0.5
            success = False
        elif verdict_str in {"reject"}:
            verdict_class = "rejected"
            predicted_p = 0.0
            success = False
        else:
            verdict_class = "escalated"
            predicted_p = 0.3
            success = False

        eu_score = -float(latency_ms) / 1000.0  # faster human review = better
        handle = helper.record_decision(
            selected=verdict_str,
            cell={"verdict_class": verdict_class},
            predicted_p_success=predicted_p,
            eu_score=eu_score,
            prediction_extras={
                "verdict": verdict_str,
                "review_requested": bool(review_requested),
                "latency_ms": float(latency_ms),
                "disposition": str(decision.disposition.value if hasattr(decision.disposition, "value") else decision.disposition),
                "stop_condition_violated": bool(getattr(decision, "stop_condition_violated", False)),
            },
        )
        helper.bind_outcome(
            handle,
            success=success,
            latency_ms=int(latency_ms),
            outcome_extras={"alias": str(getattr(decision, "alias", ""))},
        )
    except (AttributeError, TypeError, ValueError, RuntimeError):  # guardian: allow-log-and-swallow -- ledger emission is best-effort; HITL gate must never break
        _HITL_LOGGER.debug("g06_hitl_approval ledger emit failed", exc_info=True)


__all__ = ["HITLApprovalGate"]
