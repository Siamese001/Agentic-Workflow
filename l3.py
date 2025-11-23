# FILE: 10_10/l3.py
"""
L3 Orchestration Layer (v10_10 · Phase 3 — FINAL)
==================================================

Responsibilities (strict L3-only):

    • Orchestrate the end-to-end workflow at the L3 layer.
    • Delegate all DAG execution and correction-loop logic to workflow_graph.
    • Wrap orchestration in deterministic spans and node-level telemetry.
    • Coordinate with L2 (execution) and L4/L5 (state, safety) through typed
      result bundles only.

This module MUST NOT:
    • Call language models directly (L2-only, via provider agents).
    • Perform retrieval, ranking, or prompting (RAG stack only).
    • Mutate persisted state (L4-only via StateTransitionEvent).
    • Enforce safety policies (L5-only via SafetyPolicy / PolicyDecisionEvent).

Public API:

    async def orchestrate_execution(plans, ctx) -> L2ResultBundle
        Canonical Phase-3 orchestration entrypoint.

    async def run_l3_workflow(plans, ctx) -> L2ResultBundle
        Backward-compatible alias preserved for older call sites.

All detailed DAG semantics (node-level parallelism, failure modes,
correction loop) live in workflow_graph.run_workflow_graph.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Optional, Any, Dict, List

from models import WorkflowPlanBundle, ExecutionContext, L2ResultBundle
from observability import start_span, end_span, emit_node_event, log_exception
from core.workflow_graph import run_workflow_graph
from core.l5 import safety_gate


# =============================================================================
# Top-level L3 Orchestration API
# =============================================================================


@dataclass
class DAGResult:
    """Lightweight DAG result container used by tests.

    This mirrors the fields accessed in tests/test_end_to_end_v10_10.py
    without imposing additional constraints on the orchestration logic.
    """

    l2_results: L2ResultBundle
    final_state_patch: Dict[str, Any]
    safety_passed: bool
    corrected: bool = False
    corrections: List[Any] = field(default_factory=list)


async def orchestrate_execution(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    Orchestrate the full L2 workflow using the Phase-3 DAG + correction loop.

    Steps:
        1. Start an L3-level span ("l3.orchestrate").
        2. Emit high-level L3 node events (start/success/error).
        3. Delegate to workflow_graph.run_workflow_graph for actual DAG
           execution and correction-loop handling.
        4. Catch any fatal errors and return
           L2ResultBundle.empty_with_error(message).
    """
    span = start_span("l3.orchestrate", ctx=ctx.span_context())
    emit_node_event("l3_orchestrator", "start", details=None)
    try:
        results = await run_workflow_graph(plans, ctx)
        emit_node_event("l3_orchestrator", "success", details=None)
        return results
    except Exception as exc:  # noqa: BLE001
        log_exception("l3.run_fatal", exc)
        emit_node_event("l3_orchestrator", "error", details=str(exc))
        return L2ResultBundle.empty_with_error(str(exc))
    finally:
        end_span(span)


async def run_l3_workflow(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    Backward-compatible alias for orchestrate_execution.

    Older callers (e.g., earlier L4/state adapter or entrypoint code) may
    still refer to run_l3_workflow; this function keeps that surface stable
    while delegating all orchestration to orchestrate_execution.
    """
    return await orchestrate_execution(plans, ctx)


def run_dag(
    ctx: ExecutionContext,
    plans: WorkflowPlanBundle,
    max_retries: int | None = None,
) -> DAGResult:
    """Synchronous test-facing entrypoint wrapping the L3 orchestration.

    The max_retries parameter is accepted for backward compatibility
    with earlier test suites but is currently ignored; correction-loop
    behavior is governed by the ExecutionContext.config profile.
    """

    l2_results = asyncio.run(orchestrate_execution(plans, ctx))

    # Derive a simple strategy_text from the chosen or first strategy branch.
    strategy_text = ""
    try:
        branches = list(getattr(l2_results.strategy, "branches", []) or [])
        chosen_id = getattr(l2_results.strategy, "chosen_branch_id", None)
        branch = None
        if branches and chosen_id is not None:
            for b in branches:
                if getattr(b, "id", None) == chosen_id:
                    branch = b
                    break
        if branch is None and branches:
            branch = branches[0]
        if branch is not None:
            strategy_text = getattr(branch, "description", "") or getattr(branch, "text", "") or ""
        else:
            strategy_text = "error"
    except Exception:
        strategy_text = "error"

    # Build RAG evidence view.
    rag_evidence: List[Dict[str, Any]] = []
    try:
        for ev in list(getattr(l2_results.rag, "evidence", []) or []):
            rag_evidence.append(
                {
                    "text": getattr(ev, "text", ""),
                    "score": getattr(ev, "score", 0.0),
                    "source": getattr(ev, "source", None),
                }
            )
    except Exception:
        rag_evidence = []

    # Drafted sections view.
    drafted_sections: List[Dict[str, Any]] = []
    try:
        for sec in list(getattr(l2_results.drafting, "sections", []) or []):
            drafted_sections.append(
                {
                    "title": getattr(sec, "title", ""),
                    "text": getattr(sec, "text", ""),
                }
            )
    except Exception:
        drafted_sections = []

    # QA findings view.
    qa_findings: List[Dict[str, Any]] = []
    try:
        for f in list(getattr(l2_results.qa, "findings", []) or []):
            qa_findings.append(
                {
                    "id": getattr(f, "id", ""),
                    "severity": getattr(f, "severity", ""),
                    "message": getattr(f, "message", ""),
                }
            )
    except Exception:
        qa_findings = []

    # Safety findings view.
    safety_findings: List[Dict[str, Any]] = []
    try:
        for f in list(getattr(l2_results.safety, "findings", []) or []):
            safety_findings.append(
                {
                    "id": getattr(f, "check_id", ""),
                    "category": getattr(f, "category", ""),
                    "severity": getattr(f, "severity", ""),
                    "message": getattr(f, "message", ""),
                }
            )
    except Exception:
        safety_findings = []

    safety_passed = safety_gate(l2_results.safety)

    # Minimal, deterministic patch structure matching GOLDEN_PATCH keys.
    final_state_patch: Dict[str, Any] = {
        "strategy_text": strategy_text,
        "rag_evidence": rag_evidence,
        "drafted_sections": drafted_sections,
        "qa_findings": qa_findings,
        "safety_findings": safety_findings,
        "correction_signals": [],
        "safety_passed": safety_passed,
    }

    return DAGResult(
        l2_results=l2_results,
        final_state_patch=final_state_patch,
        safety_passed=safety_passed,
        corrected=False,
        corrections=[],
    )
