"""G01 — Request Ingress Gate.

Spec: prevent invalid, malformed, abusive, unintelligible, or out-of-scope
requests from entering deeper runtime.

Required checks (from spec):
- validate accepted transport and envelope shape
- assign request_id, session_id, trace_root
- enforce size, quota, and duplicate controls
- reject malformed request schemas before L1
- detect obvious unsafe or abusive input
- produce normalized validated_request or rejection reason

Allowed decisions: ALLOW | DENY | CLARIFY | SAFE_FALLBACK | THROTTLE
Stop condition: if no valid request envelope exists, downstream MUST NOT run.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import (
    GATE_REGISTRY,  # noqa: F401  (registry import for side effects)
    allow,
    deny,
    register_gate,
)
from agentic_core.L5_safety.runtime_gates.contracts import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

# Spec: enforce size and abuse controls.
MAX_PAYLOAD_BYTES = 1_000_000  # 1 MB hard ceiling
ABUSE_PATTERNS = (
    "ignore previous instructions",
    "system prompt",
    "reveal your prompt",
)


@register_gate
class RequestIngressGate:
    GATE_ID = "G01"
    PRIMARY_LAYER = "U0"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        # Stop condition: missing envelope -> fail closed.
        if not ctx.request_id or not ctx.session_id or not ctx.trace_root:
            signals.append(RegressionSignal(name="malformed_request_rate", value=1.0, severity="alert"))
            return deny(
                self.GATE_ID,
                "missing_envelope",
                missing=[f for f in ("request_id", "session_id", "trace_root") if not getattr(ctx, f, "")],
            )
        # Size / quota controls.
        payload_bytes = int(ctx.intent.get("payload_bytes", 0) or 0)
        if payload_bytes > MAX_PAYLOAD_BYTES:
            signals.append(RegressionSignal(name="quota_violation_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.THROTTLE.value,
                reason_codes=["payload_too_large"],
                signals=signals,
                metadata={"payload_bytes": payload_bytes, "max": MAX_PAYLOAD_BYTES},
                stop_condition_violated=True,
            )
        # Duplicate suppression hint (orchestrator-side dedupe).
        if ctx.intent.get("duplicate_of_request_id"):
            signals.append(RegressionSignal(name="duplicate_request_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.SAFE_FALLBACK,
                reason_codes=["duplicate_request"],
                signals=signals,
            )
        # Abuse pattern detection.
        text = str(ctx.intent.get("raw_text", "") or "").lower()
        for pat in ABUSE_PATTERNS:
            if pat in text:
                signals.append(RegressionSignal(name="jailbreak_attempt_rate", value=1.0, severity="alert"))
                return deny(self.GATE_ID, "abuse_pattern_detected", pattern=pat)
        # Malformed schema check (intent must declare objective).
        if not ctx.intent.get("objective"):
            signals.append(RegressionSignal(name="malformed_request_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.CLARIFY,
                reason_codes=["missing_objective"],
                signals=signals,
            )
        decision = allow(self.GATE_ID, "validated_request")
        decision.signals = signals
        return decision


__all__ = ["RequestIngressGate"]
