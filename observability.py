# FILE: observability.py
"""
Observability / Telemetry Layer (v10_10 · Phase 3 — FINAL)
==========================================================

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

Non-responsibilities:
    • No LLM calls
    • No retrieval
    • No ranking logic
    • No state mutation
    • No safety decisions
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


# =============================================================================
# PHASE 3 — RETRIEVAL EVENTS
# =============================================================================

def emit_retrieval_attempt(evt: RetrievalAttemptEvent) -> None:
    """
    Emit a typed retrieval attempt event.

    Typical usage from retrieval layer:
        emit_retrieval_attempt(
            RetrievalAttemptEvent(
                name="retrieval",
                method="hybrid",
                query=...,
                ts_ms=...,
                attributes={...},
            )
        )
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
# DAG / NODE EVENTS (L3)
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
