"""
Telemetry & Observability Layer — v10_9

Provides unified, deterministic primitives for:
  • Metrics (counters, gauges, events)
  • Spans & traces (timing)
  • Safety log hooks
  • Predictive cache snapshotting
  • Policy auto-tuning stubs
  • Integration points for L1–L5 orchestration

This module is intentionally framework-agnostic and produces no logs except
append-only in-memory structures that are safe for Codex and controlled
runtime environments.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


# ======================================================================
# METRIC EVENTS
# ======================================================================

@dataclass
class MetricEvent:
    """Simple metric point (counter or gauge)."""
    name: str
    value: float
    tags: Dict[str, Any] = field(default_factory=dict)


# ======================================================================
# SPAN / TRACE SUPPORT
# ======================================================================

@dataclass
class SpanEvent:
    """Timed event for execution intervals."""
    name: str
    start_time_ms: float
    end_time_ms: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)

    def duration_ms(self) -> float:
        if self.end_time_ms is None:
            return 0.0
        return max(self.end_time_ms - self.start_time_ms, 0.0)


@dataclass
class TraceContext:
    """Trace containing multiple spans."""
    trace_id: str
    spans: Dict[str, SpanEvent] = field(default_factory=dict)


# ======================================================================
# IN-MEMORY EVENT STORAGE
# ======================================================================

TELEMETRY_EVENTS: List[Dict[str, Any]] = []
SAFETY_LOG: List[Dict[str, Any]] = []


def record_event(name: str, payload: Dict[str, Any]) -> None:
    """Append a structured metric/event."""
    TELEMETRY_EVENTS.append(
        {
            "name": name,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


def get_events() -> List[Dict[str, Any]]:
    """Return a snapshot of recorded events."""
    return list(TELEMETRY_EVENTS)


# ======================================================================
# COST / SPAN TRACKING (INTERFACE-COMPATIBLE WITH L3 / L4)
# ======================================================================

@dataclass
class CostTracker:
    """
    Tracks timing spans compatible with orchestration & L4 state.

    This is a light-weight façade intentionally NOT coupled to
    cost_tracker.py; it only exposes what telemetry needs.
    """

    spans: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def start_span(self, name: str) -> None:
        self.spans[name] = {"start": time.perf_counter(), "end": None}

    def end_span(self, name: str) -> None:
        span = self.spans.get(name)
        if span and span["end"] is None:
            span["end"] = time.perf_counter()

    def snapshot(self) -> Dict[str, Any]:
        """Return span durations in ms for external consumers."""
        snapshot_spans: List[Dict[str, float]] = []
        for span_name in sorted(self.spans.keys()):
            span = self.spans[span_name]
            start = span.get("start", 0.0) or 0.0
            end = span.get("end", start)
            duration_ms = max((end - start) * 1000.0, 0.0)
            snapshot_spans.append(
                {
                    "name": span_name,
                    "duration_ms": duration_ms,
                }
            )
        return {"spans": snapshot_spans}


# ======================================================================
# SAFETY LOGGING
# ======================================================================

def log_safety_decision(payload: Dict[str, Any], patch: Dict[str, Any]) -> None:
    """Append only; zero side effects."""
    SAFETY_LOG.append(
        {
            "payload": payload,
            "patch": patch,
            "ts": datetime.utcnow().isoformat(),
        }
    )


# ======================================================================
# PREDICTIVE CACHE (UTILITY)
# ======================================================================

class PredictiveCache:
    """Simple deterministic key-value memoization for telemetry/QA."""

    def __init__(self) -> None:
        self.cache: Dict[str, Any] = {}

    def get(self, signature: str) -> Any:
        return self.cache.get(signature)

    def set(self, signature: str, value: Any) -> None:
        self.cache[signature] = value

    def snapshot(self) -> Dict[str, Any]:
        return dict(self.cache)


# ======================================================================
# POLICY AUTOTUNER (STUB)
# ======================================================================

class PolicyAutoTunerStub:
    """
    Deterministic policy tuning stub for orchestration.
    Accepts state + metrics → produces lightweight tuning rules.
    """

    def suggest_config(self, state: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "temperature": 0.3,
            "max_tokens": 500,
            "routing_adjustment": "none",
        }

