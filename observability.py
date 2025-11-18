# FILE: observability.py
"""
Unified Observability Module (v10_9) — FULL AGENTIC IMPLEMENTATION

This module provides high-level observability utilities for the v10_9
agentic runtime, sitting *above* the low-level primitives in
runtime_utils.py.

Responsibilities:
    • Run-level tracing and metrics collection
    • Span-based performance tracking (phase / stage spans)
    • Metric recording (counts, ratios, histograms – in memory)
    • Structured run summaries for:
        - Strategy
        - RAG
        - Bullets
        - Drafting
        - QA
        - Safety
    • Simple decorators for instrumenting async call sites

Design:
    • Uses CostTracker + record_event() from runtime_utils
    • In-memory only (no external dependencies)
    • Deterministic, safe, and optional (no-op friendly)

Layer boundary:
    • ABOVE L1–L5 (meta layer)
    • NO cognition, execution, orchestration, state mutation, or safety decisions
"""

from __future__ import annotations

import time
import functools
import asyncio
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable, Awaitable

from runtime_utils import CostTracker, record_event


# ============================================================================
# 1. BASIC DATA STRUCTURES
# ============================================================================

@dataclass
class TraceSpan:
    name: str
    start_time_ms: float
    end_time_ms: float
    tags: Dict[str, Any] = field(default_factory=dict)

    def duration_ms(self) -> float:
        return max(0.0, self.end_time_ms - self.start_time_ms)


@dataclass
class Metric:
    name: str
    value: float
    tags: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunSummary:
    """
    Aggregated summary for a single workflow run.

    Fields:
        • workflow_id
        • phases        – list of phase names (in order)
        • timings       – span durations by name
        • counts        – arbitrary counters (e.g., bullets_generated)
        • issues        – QA / safety issues
    """
    workflow_id: str
    phases: List[str] = field(default_factory=list)
    timings: Dict[str, float] = field(default_factory=dict)
    counts: Dict[str, int] = field(default_factory=dict)
    issues: Dict[str, List[str]] = field(default_factory=dict)


# ============================================================================
# 2. IN-MEMORY TELEMETRY BUFFER
# ============================================================================

class TelemetryBuffer:
    """
    Central store for run-level telemetry (in-memory only).

    This is intentionally simple – it can be replaced by any external
    telemetry backend without affecting call sites.
    """

    def __init__(self):
        self._metrics: List[Metric] = []
        self._spans: List[TraceSpan] = []
        self._summaries: Dict[str, RunSummary] = {}

    # ---- Metrics ------------------------------------------------------------

    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, Any]] = None) -> None:
        metric = Metric(name=name, value=float(value), tags=tags or {})
        self._metrics.append(metric)
        record_event("metric", {"name": name, "value": value, "tags": tags or {}})

    def get_metrics(self) -> List[Metric]:
        return list(self._metrics)

    # ---- Spans --------------------------------------------------------------

    def start_span(self, name: str, tags: Optional[Dict[str, Any]] = None) -> TraceSpan:
        now = time.time() * 1000.0
        span = TraceSpan(name=name, start_time_ms=now, end_time_ms=now, tags=tags or {})
        self._spans.append(span)
        return span

    def end_span(self, span: TraceSpan, extra_tags: Optional[Dict[str, Any]] = None) -> None:
        span.end_time_ms = time.time() * 1000.0
        if extra_tags:
            span.tags.update(extra_tags)
        record_event("span", {"name": span.name, "duration_ms": span.duration_ms(), "tags": span.tags})

    def get_spans(self) -> List[TraceSpan]:
        return list(self._spans)

    # ---- Run summaries ------------------------------------------------------

    def get_or_create_summary(self, workflow_id: str) -> RunSummary:
        if workflow_id not in self._summaries:
            self._summaries[workflow_id] = RunSummary(workflow_id=workflow_id)
        return self._summaries[workflow_id]

    def record_phase_transition(self, workflow_id: str, phase_history: List[str]) -> None:
        summary = self.get_or_create_summary(workflow_id)
        summary.phases = list(phase_history)

    def record_timing(self, workflow_id: str, name: str, duration_ms: float) -> None:
        summary = self.get_or_create_summary(workflow_id)
        summary.timings[name] = float(duration_ms)

    def increment_count(self, workflow_id: str, key: str, delta: int = 1) -> None:
        summary = self.get_or_create_summary(workflow_id)
        summary.counts[key] = summary.counts.get(key, 0) + int(delta)

    def record_issue(self, workflow_id: str, domain: str, issue: str) -> None:
        summary = self.get_or_create_summary(workflow_id)
        issues = summary.issues.setdefault(domain, [])
        issues.append(issue)

    def get_summary(self, workflow_id: str) -> Optional[RunSummary]:
        return self._summaries.get(workflow_id)

    def all_summaries(self) -> List[RunSummary]:
        return [s for _, s in sorted(self._summaries.items())]


# Global buffer
TELEMETRY = TelemetryBuffer()


# ============================================================================
# 3. DECORATORS FOR ASYNC SPAN TRACING
# ============================================================================

def trace_span_async(span_name: str):
    """
    Decorator for instrumenting async functions with a named span.

    Example:
        @trace_span_async("drafting")
        async def run_drafting(...):
            ...
    """
    def decorator(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            span = TELEMETRY.start_span(span_name, tags={"function": fn.__name__})
            try:
                result = await fn(*args, **kwargs)
                TELEMETRY.end_span(span)
                return result
            except Exception as exc:
                TELEMETRY.end_span(span, extra_tags={"error": str(exc)})
                raise
        return wrapper
    return decorator


# ============================================================================
# 4. RUN-LEVEL HELPERS FOR L2/L3 INTEGRATION
# ============================================================================

def summarize_strategy(workflow_id: str, state: Dict[str, Any]) -> None:
    strat = state.get("strategy_result", {}) or {}
    selected = strat.get("selected_strategy") or {}
    name = selected.get("summary") or selected.get("branch_id") or "unknown"
    TELEMETRY.record_metric("strategy_branch_selected", 1.0, {"workflow_id": workflow_id, "branch": name})


def summarize_rag(workflow_id: str, state: Dict[str, Any]) -> None:
    rag = state.get("rag_result", {}) or {}
    docs = rag.get("documents") or []
    TELEMETRY.increment_count(workflow_id, "rag_documents", len(docs))


def summarize_bullets(workflow_id: str, state: Dict[str, Any]) -> None:
    bullets = state.get("bullet_result", {}).get("bullets") or []
    TELEMETRY.increment_count(workflow_id, "bullets_generated", len(bullets))


def summarize_draft(workflow_id: str, state: Dict[str, Any]) -> None:
    draft = state.get("draft_result", {}).get("draft") or []
    TELEMETRY.increment_count(workflow_id, "draft_sections", len(draft))


def summarize_qa(workflow_id: str, state: Dict[str, Any]) -> None:
    qa = state.get("qa_result", {}).get("report") or {}
    issues = qa.get("issues", [])
    for issue in issues:
        TELEMETRY.record_issue(workflow_id, "qa", str(issue))


def summarize_safety(workflow_id: str, state: Dict[str, Any]) -> None:
    safety = state.get("safety_result", {}).get("report") or {}
    issues = safety.get("issues", [])
    for issue in issues:
        TELEMETRY.record_issue(workflow_id, "safety", str(issue))


def summarize_run(workflow_id: str, state: Dict[str, Any], phase_history: List[str], cost_tracker: Optional[CostTracker] = None) -> Dict[str, Any]:
    """
    Build a final run summary for a workflow, after L3 completion.
    """
    TELEMETRY.record_phase_transition(workflow_id, phase_history)
    summarize_strategy(workflow_id, state)
    summarize_rag(workflow_id, state)
    summarize_bullets(workflow_id, state)
    summarize_draft(workflow_id, state)
    summarize_qa(workflow_id, state)
    summarize_safety(workflow_id, state)

    summary = TELEMETRY.get_summary(workflow_id)
    out = asdict(summary) if summary else {"workflow_id": workflow_id}

    if cost_tracker is not None:
        out["cost_spans"] = cost_tracker.snapshot()["spans"]

    return out
