# FILE: observability.py
"""
Observability / Telemetry Layer (v10_10 · Phase 3)
==================================================

This module provides:
    • Structured spans (start_span / end_span)
    • Structured events (emit_node_event, emit_telemetry_event)
    • Typed retrieval + ranking events:
          – RetrievalAttemptEvent
          – RetrievalSuccessEvent
          – RetrievalFailureEvent
          – RankingEvent
    • Cost snapshot emission
    • Deterministic logging for DAG orchestration (L3)
    • Zero external I/O (collects events; callers decide persistence)

Design constraints:
    • No LLM calls.
    • No state mutation outside in-memory telemetry buffers.
    • No routing / planning decisions.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional, List

from models import (
    TelemetryEvent,
    RetrievalAttemptEvent,
    RetrievalSuccessEvent,
    RetrievalFailureEvent,
    RankingEvent,
    CostSnapshot,
)


# =============================================================================
# GLOBAL IN-MEMORY TELEMETRY BUFFER
# =============================================================================

_telemetry_buffer: List[TelemetryEvent] = []
_span_stack: List[Dict[str, Any]] = []


# =============================================================================
# INTERNAL HELPERS
# =============================================================================


def _now_ms() -> int:
    return int(time.time() * 1000)


def _log(evt: TelemetryEvent) -> None:
    """
    Store event in in-memory buffer; downstream layers
    can choose to flush, export, persist, or ignore.
    """
    _telemetry_buffer.append(evt)


# =============================================================================
# SPANS
# =============================================================================


def start_span(name: str, ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a uniquely identified span and record the start time.

    Returns a span record dict that must be passed to end_span().
    """
    span_id = str(uuid.uuid4())
    record = {
        "span_id": span_id,
        "name": name,
        "start_ms": _now_ms(),
        "ctx": ctx or {},
    }
    _span_stack.append(record)

    _log(
        TelemetryEvent(
            name=name,
            span_id=span_id,
            ts_ms=record["start_ms"],
            attributes={
                "event_type": "span_start",
                "span_id": span_id,
                "ctx": ctx or {},
            },
        )
    )

    return record


def end_span(span_record: Dict[str, Any]) -> None:
    """
    Close a previously-started span.

    If the span is not in the stack (already closed or unknown), this
    is a no-op.
    """
    if span_record not in _span_stack:
        return

    _span_stack.remove(span_record)
    end_ms = _now_ms()
    duration = end_ms - span_record["start_ms"]

    _log(
        TelemetryEvent(
            name=span_record["name"],
            span_id=span_record["span_id"],
            ts_ms=end_ms,
            attributes={
                "event_type": "span_end",
                "span_id": span_record["span_id"],
                "duration_ms": duration,
                "ctx": span_record.get("ctx", {}),
            },
        )
    )


# =============================================================================
# NODE-LEVEL EVENTS (L3)
# =============================================================================


def emit_node_event(node: str, status: str, details: Optional[str] = None) -> None:
    """
    Node-level events for L3 orchestration visibility.

    Example:
        emit_node_event("strategy", "start")
        emit_node_event("strategy", "success")
    """
    _log(
        TelemetryEvent(
            name=node,
            ts_ms=_now_ms(),
            attributes={
                "event_type": "node",
                "status": status,
                "details": details,
            },
        )
    )


# =============================================================================
# GENERIC EVENT EMISSION
# =============================================================================


def emit_telemetry_event(name: str, attributes: Dict[str, Any]) -> None:
    """
    General-purpose event emission for arbitrary telemetry use cases.
    """
    _log(
        TelemetryEvent(
            name=name,
            ts_ms=_now_ms(),
            attributes=attributes,
        )
    )


def log_exception(name: str, exc: Exception) -> None:
    """
    Emit an error-level telemetry event for exceptions.
    """
    _log(
        TelemetryEvent(
            name=name,
            ts_ms=_now_ms(),
            attributes={
                "event_type": "exception",
                "error": str(exc),
            },
        )
    )


# Convenience aliases for infrastructure layers (runtime_utils, etc.)
def record_event(name: str, attributes: Dict[str, Any]) -> None:
    """
    Convenience wrapper so infrastructure code can call record_event(...)
    without depending on TelemetryEvent directly.
    """
    emit_telemetry_event(name, attributes)


def record_exception(name: str, exc: Exception) -> None:
    """
    Convenience wrapper so infrastructure code can call record_exception(...)
    and still use the same telemetry pipeline as log_exception.
    """
    log_exception(name, exc)


# =============================================================================
# PHASE 3 — RETRIEVAL EVENTS
# =============================================================================


def emit_retrieval_attempt(evt: RetrievalAttemptEvent) -> None:
    """
    Emit a typed retrieval attempt event.
    """
    _log(evt)


def emit_retrieval_success(evt: RetrievalSuccessEvent) -> None:
    """
    Emit a typed retrieval success event.
    """
    _log(evt)


def emit_retrieval_failure(evt: RetrievalFailureEvent) -> None:
    """
    Emit a typed retrieval failure event.
    """
    _log(evt)


# =============================================================================
# PHASE 3 — RANKING EVENTS
# =============================================================================


def emit_ranking_event(evt: RankingEvent) -> None:
    """
    Emit a typed ranking event (e.g. for RRF fusion).
    """
    _log(evt)


# =============================================================================
# COST SNAPSHOT
# =============================================================================


def emit_cost_snapshot(snapshot: CostSnapshot) -> None:
    """
    Used by L2 after Strategy/Drafting/QA/Safety completes.

    The CostSnapshot is converted into telemetry attributes.
    """
    _log(
        TelemetryEvent(
            name="costs",
            ts_ms=_now_ms(),
            attributes={
                "event_type": "cost_snapshot",
                **snapshot.model_dump(),
            },
        )
    )


# =============================================================================
# PHASE 4 — EVAL / SIMULATION EVENTS
# =============================================================================


def emit_resilience_event(name: str, attributes: Dict[str, Any]) -> None:
    """Generic entrypoint for resilience-related telemetry events."""

    emit_telemetry_event(name, attributes)


def emit_golden_eval_event(
    *,
    workflow_id: str,
    scenario_id: str,
    passed: bool,
    score: float,
    summary: Dict[str, Any],
    routing_trace: Optional[List[Dict[str, Any]]] = None,
    council_summary: Optional[Dict[str, Any]] = None,
    resilience_summary: Optional[Dict[str, Any]] = None,
    cost_snapshot: Optional[CostSnapshot] = None,
) -> None:
    """Emit a GoldenEvalEvent capturing end-to-end evaluation results."""

    attrs: Dict[str, Any] = {
        "event_type": "golden_eval",
        "workflow_id": workflow_id,
        "scenario_id": scenario_id,
        "passed": passed,
        "score": score,
        "summary": summary,
    }

    if routing_trace is not None:
        attrs["routing_trace"] = routing_trace
    if council_summary is not None:
        attrs["council_summary"] = council_summary
    if resilience_summary is not None:
        attrs["resilience_summary"] = resilience_summary
    if cost_snapshot is not None:
        attrs["cost_snapshot"] = cost_snapshot.model_dump()

    emit_telemetry_event("golden_eval", attrs)


def emit_scenario_simulation_event(
    *,
    workflow_id: Optional[str],
    scenario_id: str,
    outcome: Dict[str, Any],
    telemetry: Dict[str, Any],
    error_taxonomy: Optional[Dict[str, Any]] = None,
) -> None:
    """Emit a ScenarioSimulationEvent summarizing a simulation run."""

    attrs: Dict[str, Any] = {
        "event_type": "scenario_simulation",
        "workflow_id": workflow_id,
        "scenario_id": scenario_id,
        "outcome": outcome,
        "telemetry": telemetry,
    }
    if error_taxonomy is not None:
        attrs["error_taxonomy"] = error_taxonomy

    emit_telemetry_event("scenario_simulation", attrs)


def emit_scenario_start_event(
    *,
    workflow_id: Optional[str],
    scenario_id: str,
    description: Optional[str] = None,
) -> None:
    """Emit a ScenarioStartEvent before running a simulation/eval scenario."""

    emit_telemetry_event(
        "scenario_start",
        {
            "event_type": "scenario_start",
            "workflow_id": workflow_id,
            "scenario_id": scenario_id,
            "description": description,
        },
    )


def emit_scenario_end_event(
    *,
    workflow_id: Optional[str],
    scenario_id: str,
    passed: Optional[bool] = None,
    score: Optional[float] = None,
) -> None:
    """Emit a ScenarioEndEvent after completing a simulation/eval scenario."""

    emit_telemetry_event(
        "scenario_end",
        {
            "event_type": "scenario_end",
            "workflow_id": workflow_id,
            "scenario_id": scenario_id,
            "passed": passed,
            "score": score,
        },
    )


def emit_council_arbitration_event(
    *,
    workflow_id: Optional[str],
    scenario_id: Optional[str],
    role: str,
    arbitration: Dict[str, Any],
) -> None:
    """Emit a CouncilArbitrationEvent based on council arbitration summary."""

    attrs: Dict[str, Any] = {
        "event_type": "council_arbitration",
        "workflow_id": workflow_id,
        "scenario_id": scenario_id,
        "role": role,
        **arbitration,
    }
    emit_telemetry_event("council_arbitration", attrs)


def emit_resilience_trace_event(
    *,
    workflow_id: Optional[str],
    scenario_id: Optional[str],
    name: str,
    attributes: Dict[str, Any],
) -> None:
    """Emit a ResilienceTraceEvent that tags existing resilience attributes."""

    attrs = dict(attributes)
    attrs.setdefault("event_type", "resilience_trace")
    attrs["workflow_id"] = workflow_id
    attrs["scenario_id"] = scenario_id
    emit_resilience_event(name, attrs)


# =============================================================================
# PUBLIC INSPECTION APIS
# =============================================================================


def get_all_events() -> List[TelemetryEvent]:
    """
    Return a shallow copy of the telemetry buffer.
    """
    return list(_telemetry_buffer)


def clear_events() -> None:
    """
    Clear all telemetry events and open spans.

    Intended primarily for unit tests.
    """
    _telemetry_buffer.clear()
    _span_stack.clear()
