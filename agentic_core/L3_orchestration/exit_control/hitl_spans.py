"""OTel span emission for runtime HITL lifecycle.

Per ADR-023 §3.6 and plan P2.3, four discrete spans are emitted:

| Span name        | Required attributes                                            |
|------------------|----------------------------------------------------------------|
| hitl.escalate    | run_id, trace_id, class, approver_pool, timeout_s, policy_snap |
| hitl.approved    | run_id, trace_id, approver_id, latency_ms, rationale_len       |
| hitl.denied      | run_id, trace_id, approver_id, latency_ms, reason_code         |
| hitl.timeout     | run_id, trace_id, timeout_s, fallback_taken                    |

If ``opentelemetry.trace`` is not installed, span emission is a no-op and the
module still imports — callers need not branch on availability.
"""

from __future__ import annotations

# OTel GenAI semconv opt-out: this module emits L3 HITL-escalation governance
# spans (escalation gate, decision capture, return-to-L1) \u2014 not GenAI agent /
# workflow / tool invocations. Plan: three-bucket-gap-remediation-069806 (W3).
__non_genai_emitter__ = "L3 HITL escalation spans — governance boundary, not GenAI invocations"

from typing import Any

try:
    from opentelemetry import trace as _otel_trace

    _TRACER: Any = _otel_trace.get_tracer("agentic_core.runtime.hitl")
    _OTEL_AVAILABLE = True
except ImportError:  # pragma: no cover — optional dep
    _TRACER = None
    _OTEL_AVAILABLE = False


# Span name SSOT — consumers (otel_mcp, eval engine) bind on these literals.
SPAN_ESCALATE = "hitl.escalate"
SPAN_APPROVED = "hitl.approved"
SPAN_DENIED = "hitl.denied"
SPAN_TIMEOUT = "hitl.timeout"


def _emit(name: str, attributes: dict[str, Any]) -> None:
    if not _OTEL_AVAILABLE or _TRACER is None:
        return
    # Filter out None values — OTel rejects them on some SDKs.
    clean = {k: v for k, v in attributes.items() if v is not None}
    with _TRACER.start_as_current_span(name) as span:
        for k, v in clean.items():
            span.set_attribute(k, v)


def emit_escalate(
    *,
    run_id: str,
    trace_id: str,
    hitl_class: str,
    approver_pool: str,
    timeout_s: int,
    policy_snapshot: str,
) -> None:
    _emit(
        SPAN_ESCALATE,
        {
            "run_id": run_id,
            "trace_id": trace_id,
            "hitl.class": hitl_class,
            "hitl.approver_pool": approver_pool,
            "hitl.timeout_s": timeout_s,
            "hitl.policy_snapshot": policy_snapshot,
        },
    )


def emit_approved(
    *,
    run_id: str,
    trace_id: str,
    approver_id: str,
    latency_ms: int,
    rationale_len: int = 0,
) -> None:
    _emit(
        SPAN_APPROVED,
        {
            "run_id": run_id,
            "trace_id": trace_id,
            "hitl.approver_id": approver_id,
            "hitl.latency_ms": latency_ms,
            "hitl.rationale_len": rationale_len,
        },
    )


def emit_denied(
    *,
    run_id: str,
    trace_id: str,
    approver_id: str,
    latency_ms: int,
    reason_code: str,
) -> None:
    _emit(
        SPAN_DENIED,
        {
            "run_id": run_id,
            "trace_id": trace_id,
            "hitl.approver_id": approver_id,
            "hitl.latency_ms": latency_ms,
            "hitl.reason_code": reason_code,
        },
    )


def emit_timeout(
    *,
    run_id: str,
    trace_id: str,
    timeout_s: int,
    fallback_taken: str,
) -> None:
    _emit(
        SPAN_TIMEOUT,
        {
            "run_id": run_id,
            "trace_id": trace_id,
            "hitl.timeout_s": timeout_s,
            "hitl.fallback_taken": fallback_taken,
        },
    )


__all__ = [
    "SPAN_APPROVED",
    "SPAN_DENIED",
    "SPAN_ESCALATE",
    "SPAN_TIMEOUT",
    "emit_approved",
    "emit_denied",
    "emit_escalate",
    "emit_timeout",
]
