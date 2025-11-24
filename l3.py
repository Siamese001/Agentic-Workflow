"""Coordinates how the resume workflow runs end to end so planning, drafting, QA, and safety steps happen in the right order and produce traceable, explainable results."""

# FILE: 10_10/l3.py

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List

from core.models.models import WorkflowPlanBundle, ExecutionContext, L2ResultBundle
from runtime.observability import start_span, end_span, emit_node_event, log_exception
from workflow_graph import run_workflow_graph
from l5 import safety_gate
from self_correction import evaluate_all_surfaces, aggregate_correction_signals
from eval.health.adapter import collect_error_events


# =============================================================================
# Top-level L3 Orchestration API
# =============================================================================


@dataclass
class DAGResult:
    """Collects the key artifacts from a workflow run so teams can quickly see how a resume was planned, drafted, checked, and cleared for safety without digging into low-level logs."""

    # Canonical L2 execution bundle (strategy, retrieval, drafting, QA, safety).
    l2_results: L2ResultBundle

    # High-level safety outcome as decided by L5.
    safety_passed: bool

    # Meta-level correction information (observation-only, no state mutation).
    corrected: bool = False
    corrections: List[Any] = field(default_factory=list)
    correction_signals: List[Any] = field(default_factory=list)


async def orchestrate_execution(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """Runs the full workflow using the current orchestration rules so a static plan turns into a coordinated resume rewrite with enough telemetry to understand outcomes and fix issues."""
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
    """Compatibility wrapper that forwards to :func:`orchestrate_execution`.

    This keeps older integration points working while the orchestration logic
    lives in a single modern entry point. The behavior is the same: given a
    plan and context, it runs the workflow and returns the execution results.
    """
    return await orchestrate_execution(plans, ctx)


def run_dag(
    ctx: ExecutionContext,
    plans: WorkflowPlanBundle,
    max_retries: int | None = None,
) -> DAGResult:
    """Runs the orchestrated workflow from synchronous code and returns a compact view of strategy, evidence, drafted sections, QA, and safety so resume runs are easy to review and compare."""

    l2_results = asyncio.run(orchestrate_execution(plans, ctx))

    # ------------------------------------------------------------------
    # Best-effort correction signal evaluation (META-only, no mutation).
    # ------------------------------------------------------------------
    correction_signals: List[Dict[str, Any]] = []
    try:
        signals = evaluate_all_surfaces(
            strategy=l2_results.strategy,
            rag=l2_results.rag,
            drafting=l2_results.drafting,
            qa=l2_results.qa,
            safety=l2_results.safety,
        )
        # Attach all surface-level signals as plain dicts for schema safety.
        for s in signals:
            correction_signals.append(
                {
                    "surface": getattr(s, "surface", None),
                    "severity": getattr(s, "severity", None),
                    "reason": getattr(s, "reason", None),
                    "recommended_action": getattr(s, "recommended_action", None),
                }
            )

        # Optionally highlight the aggregate signal in the same structure.
        best = aggregate_correction_signals(signals)
        if best is not None and getattr(best, "needs_correction", False):
            correction_signals.append(
                {
                    "surface": getattr(best, "surface", None),
                    "severity": getattr(best, "severity", None),
                    "reason": getattr(best, "reason", None),
                    "recommended_action": getattr(best, "recommended_action", None),
                    "aggregate": True,
                }
            )
    except Exception as exc:  # noqa: BLE001
        # Correction evaluation must never break synchronous callers.
        log_exception("l3.run_dag.correction_signals_error", exc)

    # ------------------------------------------------------------------
    # AIS error telemetry snapshot (observation-only, no decisions here).
    # ------------------------------------------------------------------
    ais_error_events: List[Dict[str, Any]] = []
    try:
        ais_error_events = collect_error_events() or []
    except Exception as exc:  # noqa: BLE001
        log_exception("l3.run_dag.ais_collection_error", exc)
    else:
        # Normalize AIS error events into additional correction_signals entries so
        # downstream consumers can see both self-correction signals and
        # infrastructure-observed issues in one compact list. These remain
        # observation-only and do not drive retries or re-planning at L3.
        for evt in ais_error_events:
            try:
                correction_signals.append(
                    {
                        "surface": "ais.error",  # telemetry source
                        "severity": evt.get("severity", "error"),
                        "reason": evt.get("error_code") or evt.get("code"),
                        "recommended_action": None,
                        "message": evt.get("message"),
                    }
                )
            except Exception:
                # AIS normalization must never break run_dag; ignore bad events.
                continue

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
        # L3 attaches correction signals and AIS error telemetry as a compact
        # view only; L4 state schema does not need to know about them.
        "correction_signals": correction_signals,
        "ais_error_events": ais_error_events,
        "safety_passed": safety_passed,
    }

    # Mark the run as corrected if any correction signals (including AIS-derived)
    # are present. This remains an observation-only flag; it does not trigger
    # retries or re-planning at L3.
    corrected = bool(correction_signals)

    return DAGResult(
        l2_results=l2_results,
        final_state_patch=final_state_patch,
        safety_passed=safety_passed,
        corrected=corrected,
        corrections=[],
        correction_signals=correction_signals,
    )
