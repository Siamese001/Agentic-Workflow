# FILE: 10_10/observability.py
"""
Observability Utilities (v10_10 · Phase 0)
=========================================

This module provides a SAFE, MINIMAL, and DETERMINISTIC observability layer
for the v10_10 agentic architecture.

Phase 0 goals (Option A – in-memory, deterministic):
    • Structured span logging (start/end).
    • Structured event logging (TelemetryEvent).
    • Structured exception logging.
    • Hooks for:
        – StateTransitionEvent (L4)
        – PolicyDecisionEvent (L5)
        – CostSnapshot (meta / batch)
    • In-memory buffers suitable for:
        – unit tests,
        – golden evaluation,
        – simulation and meta-learning.

Non-goals (for Phase 0):
    • No external dependencies (no OpenTelemetry client).
    • No network calls.
    • No asynchronous exporters.
    • No persistent storage.
    • No external dashboards.

The API is designed to be backward-compatible with existing v10_10 callsites:
    • start_span(name: str, ctx: Optional[dict]) -> span_id
    • end_span(span_id)
    • record_exception(event_name: str, exc: Exception)
"""

from __future__ import annotations

import threading
import time
import traceback
from typing import Any, Dict, List, Optional

from .models import (
    TelemetryEvent,
    CostSnapshot,
    PolicyDecisionEvent,
    StateTransitionEvent,
)


# ======================================================================
# INTERNAL STATE (IN-MEMORY BUFFERS)
# ======================================================================

# Span records (start/end, duration, context)
_SPANS: List[Dict[str, Any]] = []

# TelemetryEvent records
_TELEMETRY_EVENTS: List[TelemetryEvent] = []

# PolicyDecisionEvent records
_POLICY_DECISIONS: List[PolicyDecisionEvent] = []

# StateTransitionEvent records
_STATE_TRANSITIONS: List[StateTransitionEvent] = []

# Raw low-level event log (for debugging / tests)
_RAW_EVENTS: List[Dict[str, Any]] = []

# Simple span id generator
_SPAN_COUNTER = 0
_SPAN_LOCK = threading.Lock()


# ======================================================================
# SPAN API (BACKWARD-COMPATIBLE)
# ======================================================================


def start_span(name: str, ctx: Optional[Dict[str, Any]] = None) -> str:
    """
    Start a new span and return its span_id.

    Existing v10_10 callsites:
        span = start_span("l2.execute_strategy", ctx=ctx.span_context())
        ...
        end_span(span)
    """
    global _SPAN_COUNTER

    with _SPAN_LOCK:
        _SPAN_COUNTER += 1
        span_id = f"span-{_SPAN_COUNTER}"

    ts = time.time()
    record = {
        "id": span_id,
        "name": name,
        "ts_start": ts,
        "ts_end": None,
        "duration_ms": None,
        "ctx": ctx or {},
        "error": None,
    }
    _SPANS.append(record)

    _safe_emit(
        {
            "type": "span.start",
            "id": span_id,
            "name": name,
            "ctx": ctx or {},
            "ts": ts,
        }
    )
    return span_id


def end_span(span: str, error: Optional[Exception] = None) -> None:
    """
    End a span previously created by start_span().

    The `span` argument is the span_id string returned by start_span().
    If `error` is provided, mark the span as errored and emit an error event.
    """
    ts = time.time()
    # Find span in reverse order for efficiency (latest first).
    for rec in reversed(_SPANS):
        if rec["id"] == span:
            rec["ts_end"] = ts
            rec["duration_ms"] = int((ts - rec["ts_start"]) * 1000)
            if error is not None:
                rec["error"] = str(error)
            break

    payload: Dict[str, Any] = {
        "type": "span.end",
        "id": span,
        "ts": ts,
    }
    if error is not None:
        payload["error"] = str(error)

    _safe_emit(payload)


# ======================================================================
# EXCEPTION LOGGING (BACKWARD-COMPATIBLE)
# ======================================================================


def record_exception(event_name: str, exc: Exception) -> None:
    """
    Emit a structured exception event with full traceback.

    Existing v10_10 usage examples:
        record_exception("l2.strategy_error", exc)
        record_exception("l3.dag_failure", exc)
    """
    _safe_emit(
        {
            "type": "exception",
            "event": event_name,
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ts": time.time(),
        }
    )


# ======================================================================
# TELEMETRY EVENTS (NEW FOR G15–G17, G20)
# ======================================================================


def emit_telemetry_event(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    span_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
) -> TelemetryEvent:
    """
    Emit a TelemetryEvent and store it in-memory.

    Attributes:
        • name        – logical event name ("rag.query", "qa.completed").
        • attributes  – arbitrary structured data describing the event.
        • span_id     – optional span_id from start_span().
        • workflow_id – optional workflow ID.
    """
    ts_ms = int(time.time() * 1000)
    event = TelemetryEvent(
        name=name,
        span_id=span_id,
        workflow_id=workflow_id,
        ts_ms=ts_ms,
        attributes=attributes or {},
    )
    _TELEMETRY_EVENTS.append(event)

    _safe_emit(
        {
            "type": "telemetry",
            "name": name,
            "span_id": span_id,
            "workflow_id": workflow_id,
            "ts_ms": ts_ms,
            "attributes": attributes or {},
        }
    )
    return event


def emit_policy_decision(decision: PolicyDecisionEvent) -> None:
    """
    Record a structured PolicyDecisionEvent (L5).

    This is used to satisfy G20–G21 for safety auditability.
    """
    _POLICY_DECISIONS.append(decision)

    _safe_emit(
        {
            "type": "policy.decision",
            "decision": decision.decision,
            "reason": decision.reason,
            "workflow_id": decision.workflow_id,
            "check_id": decision.check_id,
            "details": decision.details,
            "ts": time.time(),
        }
    )


def emit_state_transition(event: StateTransitionEvent) -> None:
    """
    Record a structured StateTransitionEvent (from L4).

    This satisfies G15 and G34–G36 by linking state changes to telemetry.
    """
    _STATE_TRANSITIONS.append(event)

    _safe_emit(
        {
            "type": "state.transition",
            "event_id": event.event_id,
            "workflow_id": event.workflow_id,
            "kind": event.kind,
            "metadata": event.metadata,
            "ts": time.time(),
        }
    )


def emit_cost_snapshot(
    workflow_id: str,
    span_id: Optional[str],
    cost: CostSnapshot,
) -> None:
    """
    Emit a cost accounting snapshot for a workflow or span.

    This will be used by batch / simulation / golden eval to analyze cost
    trends and enforce budgets (G16, G20).
    """
    _safe_emit(
        {
            "type": "cost.snapshot",
            "workflow_id": workflow_id,
            "span_id": span_id,
            "input_tokens": cost.input_tokens,
            "output_tokens": cost.output_tokens,
            "total_cost_usd": cost.total_cost_usd,
            "ts": time.time(),
        }
    )


# ======================================================================
# INTROSPECTION HELPERS (FOR TESTS, GOLDEN EVAL, SIMULATION)
# ======================================================================


def get_span_log() -> List[Dict[str, Any]]:
    """
    Return a shallow copy of all span records.

    Intended for tests and simulation; not for production use.
    """
    return list(_SPANS)


def get_telemetry_log() -> List[TelemetryEvent]:
    """
    Return a shallow copy of all TelemetryEvent records.
    """
    return list(_TELEMETRY_EVENTS)


def get_policy_decisions() -> List[PolicyDecisionEvent]:
    """
    Return a shallow copy of all PolicyDecisionEvent records.
    """
    return list(_POLICY_DECISIONS)


def get_state_transitions() -> List[StateTransitionEvent]:
    """
    Return a shallow copy of all StateTransitionEvent records.
    """
    return list(_STATE_TRANSITIONS)


def get_raw_event_log() -> List[Dict[str, Any]]:
    """
    Return a shallow copy of the low-level raw event log.
    """
    return list(_RAW_EVENTS)


def reset_observability() -> None:
    """
    Reset all in-memory observability buffers.

    This is useful for unit tests and simulation harnesses that want to
    ensure a clean slate.
    """
    global _SPANS, _TELEMETRY_EVENTS, _POLICY_DECISIONS, _STATE_TRANSITIONS, _RAW_EVENTS
    global _SPAN_COUNTER

    _SPANS = []
    _TELEMETRY_EVENTS = []
    _POLICY_DECISIONS = []
    _STATE_TRANSITIONS = []
    _RAW_EVENTS = []
    _SPAN_COUNTER = 0


# ======================================================================
# INTERNAL LOW-LEVEL EMIT
# ======================================================================


def _safe_emit(record: Dict[str, Any]) -> None:
    """
    Internal: append the record to the in-memory raw event log.

    This function is intentionally conservative: if we ever extend it to
    write to stdout or files, we must keep it side-effect free for tests.
    """
    _RAW_EVENTS.append(record)
