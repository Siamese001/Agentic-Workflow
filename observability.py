# FILE: observability.py
"""
Observability / Telemetry Layer (v10_10 · Phase 3)
==================================================

This module provides:
    • Structured spans (start_span / end_span)
    • Structured events (emit_node_event, emit_telemetry_event)
    • Retrieval + Ranking event types (Phase 3 additions)
    • Cost snapshot emission
    • Deterministic logging for DAG orchestration (L3)
    • Zero external I/O (print-to-log; callers decide persistence layer)

Non-responsibilities:
    • No LLM calls
    • No retrieval
    • No ranking logic
    • No state mutation
    • No safety filtering

This file is intentionally pure-observability:
    - context-free
    - thread-safe
    - deterministic
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

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

_telemetry_buffer: list[TelemetryEvent] = []
_span_stack: list[Dict[str, Any]] = []


# =============================================================================
# INTERNAL HELPERS
# =============================================================================

def _now_ms() -> int:
    return int(time.time() * 1000)


def _log(evt: TelemetryEvent):
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
            type="span_start",
            name=name,
            timestamp_ms=record["start_ms"],
            metadata={"span_id": span_id, "ctx": ctx or {}},
        )
    )

    return record


def end_span(span_record: Dict[str, Any]):
    """
    Close a previously-started span.
    """
    if span_record not in _span_stack:
        return

    _span_stack.remove(span_record)
    end_ms = _now_ms()
    duration = end_ms - span_record["start_ms"]

    _log(
        TelemetryEvent(
            type="span_end",
            name=span_record["name"],
            timestamp_ms=end_ms,
            metadata={
                "span_id": span_record["span_id"],
                "duration_ms": duration,
                "ctx": span_record.get("ctx", {}),
            },
        )
    )


# =============================================================================
# EVENT EMISSION
# =============================================================================

def emit_telemetry_event(name: str, attributes: Dict[str, Any]):
    """
    General-purpose event emission for arbitrary telemetry use cases.
    """
    _log(
        TelemetryEvent(
            type="event",
            name=name,
            timestamp_ms=_now_ms(),
            metadata=attributes,
        )
    )


def log_exception(name: str, exc: Exception):
    """
    Emit an error-level telemetry event for exceptions.
    """
    _log(
        TelemetryEvent(
            type="exception",
            name=name,
            timestamp_ms=_now_ms(),
            metadata={"error": str(exc)},
        )
    )


# =============================================================================
# PHASE 3 — RETRIEVAL EVENTS
# =============================================================================

def emit_retrieval_attempt(evt: RetrievalAttemptEvent):
    _log(evt)


def emit_retrieval_success(evt: RetrievalSuccessEvent):
    _log(evt)


def emit_retrieval_failure(evt: RetrievalFailureEvent):
    _log(evt)


# =============================================================================
# PHASE 3 — RANKING EVENTS
# =============================================================================

def emit_ranking_event(evt: RankingEvent):
    _log(evt)


# =============================================================================
# DAG / NODE EVENTS (L3)
# =============================================================================

def emit_node_event(node: str, status: str, details: Optional[str] = None):
    """
    Node-level events for L3 orchestration visibility.
    """
    _log(
        TelemetryEvent(
            type="node",
            name=node,
            timestamp_ms=_now_ms(),
            metadata={"status": status, "details": details},
        )
    )


# =============================================================================
# COST SNAPSHOT
# =============================================================================

def emit_cost_snapshot(snapshot: CostSnapshot):
    """
    Used by L2 run() after Strategy/Drafting/QA/Safety completes.
    """
    _log(
        TelemetryEvent(
            type="cost_snapshot",
            name="costs",
            timestamp_ms=_now_ms(),
            metadata=snapshot.model_dump(),
        )
    )


# =============================================================================
# PUBLIC INSPECTION APIS
# =============================================================================

def get_all_events() -> list[TelemetryEvent]:
    return list(_telemetry_buffer)


def clear_events():
    _telemetry_buffer.clear()
    _span_stack.clear()
