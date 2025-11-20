# FILE: observability.py
"""
Unified Observability Module (v10_10) — TELEMETRY & META-LEARNING

This module implements Pillar 10 (Observability).
It aggregates traces, metrics, and logs to produce the `RunSummary`.
Crucially, it feeds this data back into the `MetaProfile` to enable learning.

Responsibilities:
    1. Distributed Tracing: Track spans across L1-L5.
    2. Metric Aggregation: Count tokens, latency, and errors.
    3. Run Summarization: Convert raw telemetry into a Golden Record.
    4. Meta-Feedback: Trigger bias updates in `MetaProfile`.

Refactor Highlights (v10_10):
    • Strictly Typed: Consumes Pydantic payloads.
    • Meta-Integrated: Closes the feedback loop automatically.
"""

from __future__ import annotations

import time
import functools
from typing import Any, Dict, List, Optional, Callable, Awaitable

from models import (
    RunSummary, 
    TraceSpan, 
    WorkflowState,
    AgenticBaseModel
)
from meta_profile import META_PROFILE
from runtime_utils import record_event

# =============================================================================
# TELEMETRY BUFFER (In-Memory)
# =============================================================================

class TelemetryBuffer:
    """
    Central store for run-level telemetry.
    Stores transient data before summarization.
    """

    def __init__(self):
        self._spans: List[TraceSpan] = []
        self._metrics: Dict[str, float] = {}
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
        
        # Emit low-level event (Pillar 10)
        record_event("span_complete", {
            "name": span.name, 
            "duration": span.duration_ms(),
            "tags": span.tags
        })

    def get_spans(self) -> List[TraceSpan]:
        return list(self._spans)

    # --- METRICS ---
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, Any]] = None) -> None:
        # Simple counter/gauge simulation
        self._metrics[name] = value
        record_event("metric", {"name": name, "value": value, "tags": tags or {}})

    # --- SUMMARY CACHE ---
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
    """Async decorator to auto-trace execution blocks."""
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
    final_state: Dict[str, Any], # Serialized State from L4
    phase_history: List[str]
) -> RunSummary:
    """
    Constructs the final Golden Record of the execution.
    Extracts domain-specific outcomes and updates the MetaProfile.
    """
    summary = TELEMETRY.get_or_create_summary(workflow_id)
    summary.phases = phase_history

    # 1. Extract Domain Metrics (From Serialized Pydantic Models)
    
    # Strategy
    if strat := final_state.get("strategy_result"):
        # strat is a dict here
        decision = strat.get("selected_branch_id", "unknown")
        TELEMETRY.record_metric("strategy.branch_selected", 1, {"branch": decision})
        
    # RAG
    if rag := final_state.get("rag_result"):
        docs = rag.get("documents", [])
        summary.counts["rag_docs"] = len(docs)

    # QA
    if qa := final_state.get("qa_result"):
        # QAPayload: { passed: bool, findings: List[QAFinding] }
        passed = qa.get("passed", False)
        findings = qa.get("findings", [])
        if not passed:
            # Format: "[severity] ID: Message"
            summary.issues["qa"] = [
                f"[{f.get('severity')}] {f.get('finding_id')}: {f.get('message')}" 
                for f in findings
            ]
    
    # Safety
    if safety := final_state.get("safety_result"):
        # SafetyPayload: { blocked: bool, findings: List[SafetyFinding] }
        blocked = safety.get("blocked", False)
        findings = safety.get("findings", [])
        if blocked or findings:
            summary.issues["safety"] = [
                f"{f.get('rule_id')} (Violated: {f.get('violated')})" 
                for f in findings if f.get('violated')
            ]

    # 2. Aggregate Timings
    spans = TELEMETRY.get_spans()
    for s in spans:
        summary.timings[s.name] = s.duration_ms()

    # 3. META-FEEDBACK LOOP (Pillar 5)
    # "The Agent learns from its own execution."
    
    # A. Update Routing Bias based on Latency
    META_PROFILE.update_from_spans(spans)
    
    # B. Update Planning/Safety Bias based on Failures
    META_PROFILE.update_from_issues(summary.issues)

    # 4. Snapshot the Brain
    # Capture the exact biases active at the end of the run for audit
    summary.meta_profile = META_PROFILE.profile.model_dump()

    return summary
