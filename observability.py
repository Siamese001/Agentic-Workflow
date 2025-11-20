# FILE: observability.py
"""
Unified Observability Module (v10_10) — TELEMETRY & META-LEARNING (REFACTORED)

This module implements the "Eyes" of the agent (Pillar 10).
It aggregates traces, metrics, and logs to produce the `RunSummary`.

Responsibilities:
    1. Distributed Tracing: Track spans across L1-L5.
    2. Metric Aggregation: Count tokens, latency, and errors.
    3. Run Summarization: Convert raw telemetry into a structured report.
    4. Meta-Feedback: Feed performance data back into `MetaProfile`.

Refactor Highlights (v10_10):
    • Strongly Typed: Consumes Pydantic payloads from `models.py`.
    • Meta-Integrated: Automatically updates biases via `meta_profile`.
    • Gateway-Aware: Native tracking for LLM and Tool usage.
"""

from __future__ import annotations

import time
import functools
from typing import Any, Dict, List, Optional, Callable, Awaitable

from models import (
    RunSummary, 
    TraceSpan, 
    Metric, 
    WorkflowState, 
    ExecutionResult,
    AgenticBaseModel
)
from meta_profile import (
    update_from_spans, 
    update_from_run_summary,
    get_meta_profile_snapshot
)
from runtime_utils import record_event

# =============================================================================
# TELEMETRY BUFFER (In-Memory)
# =============================================================================

class TelemetryBuffer:
    """
    Central store for run-level telemetry.
    Zero-dependency; purely stores data for the final report.
    """

    def __init__(self):
        self._metrics: List[Metric] = []
        self._spans: List[TraceSpan] = []
        self._summary_cache: Dict[str, RunSummary] = {}

    # --- SPANS ---
    def start_span(self, name: str, tags: Optional[Dict[str, Any]] = None) -> TraceSpan:
        now = time.time() * 1000.0
        span = TraceSpan(name=name, start_time_ms=now, end_time_ms=now, tags=tags or {})
        self._spans.append(span)
        return span

    def end_span(self, span: TraceSpan, extra_tags: Optional[Dict[str, Any]] = None) -> None:
        span.end_time_ms = time.time() * 1000.0
        if extra_tags:
            span.tags.update(extra_tags)
        record_event("span_complete", {"name": span.name, "duration": span.duration_ms()})

    def get_spans(self) -> List[TraceSpan]:
        return list(self._spans)

    # --- METRICS ---
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, Any]] = None) -> None:
        self._metrics.append(Metric(name=name, value=value, tags=tags or {}))

    # --- SUMMARIES ---
    def get_or_create_summary(self, workflow_id: str) -> RunSummary:
        if workflow_id not in self._summary_cache:
            self._summary_cache[workflow_id] = RunSummary(workflow_id=workflow_id)
        return self._summary_cache[workflow_id]

# Global Singleton
TELEMETRY = TelemetryBuffer()


# =============================================================================
# DECORATORS
# =============================================================================

def trace_span_async(span_name: str):
    """Async decorator to auto-trace execution."""
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


# =============================================================================
# SUMMARIZER ENGINE
# =============================================================================

def summarize_run(
    workflow_id: str,
    final_state: Dict[str, Any], # This is the serialised state from L4
    phase_history: List[str]
) -> RunSummary:
    """
    Constructs the final Golden Record of the execution.
    """
    summary = TELEMETRY.get_or_create_summary(workflow_id)
    summary.phases = phase_history

    # 1. Extract Domain Metrics from State
    # Because L4.state returns dicts (serialized models), we safely access keys.
    
    # Strategy
    if strat := final_state.get("strategy_result"):
        decision = strat.get("aggregated_decision", "unknown")
        TELEMETRY.record_metric("strategy_decision", 1, {"type": decision})
        
    # RAG
    if rag := final_state.get("rag_result"):
        doc_count = len(rag.get("documents", []))
        summary.counts["rag_docs"] = doc_count

    # QA
    if qa := final_state.get("qa_result"):
        report = qa.get("report", {})
        passed = report.get("passed", False)
        issues = report.get("findings", [])
        if not passed:
            summary.issues["qa"] = [f"{i.get('check_id')}: {i.get('message')}" for i in issues]
    
    # Safety
    if safety := final_state.get("safety_result"):
        report = safety.get("report", {})
        if report.get("blocked"):
            issues = report.get("issues", [])
            summary.issues["safety"] = [f"{i.get('category')}: {i.get('message')}" for i in issues]

    # 2. Aggregate Timings
    spans = TELEMETRY.get_spans()
    for s in spans:
        summary.timings[s.name] = s.duration_ms()

    # 3. META-FEEDBACK LOOP (Pillar 5)
    # "The Agent learns from its own execution."
    
    # Feed timings back to Routing Bias (e.g. "Planning took too long -> prefer_fast")
    update_from_spans(spans)
    
    # Feed failures back to Planning Bias (e.g. "QA failed -> conservative mode")
    # We reconstruct a dict-based summary for the meta-profile updater
    meta_input = {
        "issues": summary.issues,
        "counts": summary.counts
    }
    update_from_run_summary(meta_input)

    # 4. Snapshot the Brain
    # Capture the exact biases active at the end of the run
    summary.meta_profile = get_meta_profile_snapshot()

    return summary
