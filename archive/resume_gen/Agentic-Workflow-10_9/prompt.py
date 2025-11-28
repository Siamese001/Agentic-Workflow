# FILE: observability.py
"""
Unified Observability Module (v10_9) — META / INFRASTRUCTURE LAYER (REFINED)

This module provides the entire observability subsystem for the v10_9
agentic runtime. It sits strictly ABOVE L1–L5 and owns:

    • Run-level tracing and metrics collection
    • Span-based performance tracking
    • Metric recording (counts, ratios, histograms – in memory)
    • Structured run summaries for:
        - Strategy
        - RAG
        - Bullets
        - Drafting
        - QA
        - Safety
        - HIL
        - Meta-learning
    • Async span decorators for instrumentation
    • Telemetry aggregation for end-of-run summaries
    • Meta-profile updates from spans + run_summary

Layer Guardrails:

    • NO L1 cognition
    • NO L2 tool/LLM execution
    • NO L3 orchestration logic
    • NO L4 state mutation logic
    • NO L5 safety/policy decisions
    • NO provider SDK calls

This refactor additionally:

    • Fixes mismatches with the refactored payload formats (l1–l2–l3).
    • Integrates with meta_profile.update_from_spans and update_from_run_summary.
    • Exposes meta_profile snapshot in the returned run_summary.
"""

from __future__ import annotations

import time
import functools
import asyncio
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable, Awaitable

from runtime.runtime_utils_v10_9 import CostTracker, record_event
from meta_profile import (
    update_from_spans,
    update_from_run_summary,
    get_meta_profile_snapshot,
)


# ============================================================================
# 1. BASIC DATA STRUCTURES
# ============================================================================

@dataclass
class TraceSpan:
    """Represents a single performance span."""
    name: str
    start_time_ms: float
    end_time_ms: float
    tags: Dict[str, Any] = field(default_factory=dict)

    def duration_ms(self) -> float:
        return max(0.0, self.end_time_ms - self.start_time_ms)


@dataclass
class Metric:
    """Represents a single numeric metric."""
    name: str
    value: float
    tags: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunSummary:
    """
    Aggregated summary for a single workflow run.

    Fields:
        • workflow_id
        • phases        – ordered list of phases
        • timings       – span durations
        • counts        – metric counters
        • issues        – domain-specific issue lists
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

    This is pure infra: it holds metrics, spans, and summaries for each
    workflow_id. It never mutates application state.
    """

    def __init__(self):
        self._metrics: List[Metric] = []
        self._spans: List[TraceSpan] = []
        self._summaries: Dict[str, RunSummary] = {}

    # ---- Metrics ------------------------------------------------------------

    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, Any]] = None) -> None:
        m = Metric(name=name, value=float(value), tags=tags or {})
        self._metrics.append(m)
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


# Global buffer (safe for in-process execution)
TELEMETRY = TelemetryBuffer()


# ============================================================================
# 3. ASYNC SPAN DECORATOR
# ============================================================================

def trace_span_async(span_name: str):
    """
    Decorator for async functions: records a named span in TELEMETRY.
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
# 4. RUN-LEVEL DOMAIN SUMMARIES
# ============================================================================

def summarize_strategy(workflow_id: str, state: Dict[str, Any]) -> None:
    strat = state.get("strategy_result", {}) or {}
    # Our L3 stores the StrategyExecutionPayload.to_dict() directly
    # so we look for aggregated_decision or selected_branch.strategy_name
    decision_name = strat.get("aggregated_decision")
    if not decision_name:
        selected_branch = strat.get("selected_branch") or {}
        decision_name = selected_branch.get("strategy_name") or "unknown"
    TELEMETRY.record_metric(
        "strategy_decision",
        1.0,
        {"workflow_id": workflow_id, "decision": decision_name},
    )


def summarize_rag(workflow_id: str, state: Dict[str, Any]) -> None:
    rag = state.get("rag_result", {}) or {}
    # RAGExecutionPayload.to_dict() shape: {"queries": [...], "documents": [...], ...}
    docs = rag.get("documents") or []
    TELEMETRY.increment_count(workflow_id, "rag_documents", len(docs))


def summarize_bullets(workflow_id: str, state: Dict[str, Any]) -> None:
    bullets_block = state.get("bullet_result") or {}
    bullets = bullets_block.get("bullets") or []
    TELEMETRY.increment_count(workflow_id, "bullets_generated", len(bullets))


def summarize_draft(workflow_id: str, state: Dict[str, Any]) -> None:
    draft_block = state.get("draft_result") or {}
    # DraftExecutionPayload.to_dict(): {"sections": [...], "full_text": "...", ...}
    sections = draft_block.get("sections") or []
    TELEMETRY.increment_count(workflow_id, "draft_sections", len(sections))


def summarize_qa(workflow_id: str, state: Dict[str, Any]) -> None:
    qa_block = state.get("qa_result") or {}
    report = qa_block.get("report") or qa_block
    issues = report.get("issues", [])
    for iss in issues:
        TELEMETRY.record_issue(workflow_id, "qa", str(iss))


def summarize_safety(workflow_id: str, state: Dict[str, Any]) -> None:
    safety_block = state.get("safety_result") or {}
    report = safety_block.get("report") or safety_block
    issues = report.get("issues", [])
    for iss in issues:
        TELEMETRY.record_issue(workflow_id, "safety", str(iss))


def summarize_hil(workflow_id: str, state: Dict[str, Any]) -> None:
    hil = state.get("hil_result") or {}
    response = hil.get("response")
    if response:
        TELEMETRY.increment_count(workflow_id, "hil_interventions", 1)
        TELEMETRY.record_issue(workflow_id, "hil", "hil_response_present")


def summarize_meta_learning(workflow_id: str, state: Dict[str, Any]) -> None:
    meta = state.get("meta_learning_result") or {}
    snapshot = meta.get("snapshot") or {}
    findings = snapshot.get("findings") or []
    TELEMETRY.increment_count(workflow_id, "meta_findings", len(findings))


# ============================================================================
# 5. RUN SUMMARY AGGREGATOR (META-INTEGRATED)
# ============================================================================

def summarize_run(
    workflow_id: str,
    state: Dict[str, Any],
    phase_history: List[str],
    cost_tracker: Optional[CostTracker] = None,
) -> Dict[str, Any]:
    """
    Build a structured run summary for a workflow, combining:

        • phase history
        • timing spans (from CostTracker and TELEMETRY)
        • domain metrics and issues
        • meta_profile updates (from spans and run_summary)
    """
    # Record phase history
    TELEMETRY.record_phase_transition(workflow_id, phase_history)

    # Record timings using CostTracker snapshot (if available)
    if cost_tracker is not None and hasattr(cost_tracker, "snapshot"):
        snapshot = cost_tracker.snapshot()
        for span in snapshot.get("spans", []):
            name = span.get("name", "")
            duration_ms = float(span.get("duration_ms", 0.0))
            if name:
                TELEMETRY.record_timing(workflow_id, name, duration_ms)

    # Domain-specific summaries
    summarize_strategy(workflow_id, state)
    summarize_rag(workflow_id, state)
    summarize_bullets(workflow_id, state)
    summarize_draft(workflow_id, state)
    summarize_qa(workflow_id, state)
    summarize_safety(workflow_id, state)
    summarize_hil(workflow_id, state)
    summarize_meta_learning(workflow_id, state)

    # Construct raw summary dataclass
    summary = TELEMETRY.get_summary(workflow_id)
    if not summary:
        base_summary = {
            "workflow_id": workflow_id,
            "phases": list(phase_history),
            "timings": {},
            "counts": {},
            "issues": {},
        }
        # Still update meta_profile from spans/run_summary, then attach snapshot
        spans_for_meta = [
            {"name": s.name, "duration_ms": s.duration_ms()}
            for s in TELEMETRY.get_spans()
        ]
        if spans_for_meta:
            update_from_spans(spans_for_meta)

        update_from_run_summary(base_summary)
        base_summary["meta_profile"] = get_meta_profile_snapshot()
        return base_summary

    run_summary = asdict(summary)

    # --- META-PROFILE UPDATE: from spans ---
    spans_for_meta = [
        {"name": s.name, "duration_ms": s.duration_ms()}
        for s in TELEMETRY.get_spans()
    ]
    if spans_for_meta:
        update_from_spans(spans_for_meta)

    # --- META-PROFILE UPDATE: from run_summary ---
    update_from_run_summary(run_summary)

    # Attach meta_profile snapshot
    run_summary["meta_profile"] = get_meta_profile_snapshot()

    return run_summary
