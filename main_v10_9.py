# FILE: main_v10_9.py
"""
Main Entry Point — v10_9 Agentic Workflow (FULLY AGENTIC, REFINED)

This module provides the official entrypoint for the unified v10_9
agentic workflow.

High-level pipeline:
    1. L1: route_plan() – produce a PlanObject for the requested task.
    2. L3: Orchestrator.run() – execute domain-specific pipeline (L2 + L4 + L5).
    3. Observability: summarize_run() – produce a structured run summary.
    4. Return: updated state + phase + summary.

Design guarantees:
    • No direct references to previous versions (10_7, 10_8, LangGraph, etc.)
    • Single-pass execution (one L1 plan → one L3 run)
    • Layer purity (no L1–L5 logic in this file, only coordination)
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from l1 import route_plan
from l3 import Orchestrator
from runtime_utils import CostTracker
from observability import summarize_run


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------


def _initialize_state(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize the incoming state so that the orchestrator has
    all expected top-level keys.

    Ensures:
        • workflow_id present in root and metadata
        • messages is a list
        • metadata is a dict
    """
    state = dict(initial_state or {})
    metadata = state.setdefault("metadata", {})

    workflow_id = (
        state.get("workflow_id")
        or metadata.get("workflow_id")
        or "workflow_v10_9"
    )
    state["workflow_id"] = workflow_id
    metadata["workflow_id"] = workflow_id

    # Ensure messages array exists
    if not isinstance(state.get("messages"), list):
        state["messages"] = []

    return state


# ---------------------------------------------------------------------------
# ASYNC ENTRYPOINT
# ---------------------------------------------------------------------------


async def run_workflow_v10_9(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single v10_9 agentic workflow pass.

    Args:
        initial_state: dict describing the task, context, and any
                       prior state to be used by L1.

    Returns:
        dict:
            {
                "workflow_id": str,
                "phase": str,
                "state": <final state dict>,
                "phase_metadata": {...},
                "run_summary": {...},
            }
    """

    # Normalize and prepare state
    state = _initialize_state(initial_state)
    workflow_id = state["workflow_id"]

    # Tracking cost/timing spans
    cost_tracker = CostTracker()

    # ---- L1: PLANNING ----
    cost_tracker.start_span("planning")
    plan = route_plan(state)
    cost_tracker.end_span("planning")

    # ---- L3: ORCHESTRATION + L2/L4/L5 ----
    orchestrator = Orchestrator()
    cost_tracker.start_span("execution")
    # Orchestrator.run is synchronous; we just call it directly.
    workflow_state = orchestrator.run(plan, state)
    cost_tracker.end_span("execution")

    final_state = workflow_state.state
    phase_history = workflow_state.phase_metadata.get("history", [workflow_state.phase])

    # ---- Observability Summary ----
    run_summary = summarize_run(
        workflow_id=workflow_id,
        state=final_state,
        phase_history=phase_history,
        cost_tracker=cost_tracker,
    )

    return {
        "workflow_id": workflow_id,
        "phase": workflow_state.phase,
        "state": final_state,
        "phase_metadata": workflow_state.phase_metadata,
        "run_summary": run_summary,
    }


# ---------------------------------------------------------------------------
# SYNC WRAPPER
# ---------------------------------------------------------------------------


def run_workflow_sync(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous convenience wrapper around run_workflow_v10_9().
    """
    return asyncio.run(run_workflow_v10_9(initial_state))


# ---------------------------------------------------------------------------
# OPTIONAL CLI TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    example_state = {
        "objective": "draft a concise professional summary",
        "messages": [
            {"role": "user", "content": "Summarize my profile for an executive recruiter."}
        ],
        "resume": {
            "master_resume": {
                "summary": "Senior leader with 15+ years of experience in AI, data, and product.",
                "professional_experience": [],
            }
        },
    }

    result = run_workflow_sync(example_state)
    print("=== v10_9 Agentic Workflow Output ===")
    print("Workflow ID:", result["workflow_id"])
    print("Final Phase:", result["phase"])
    print("Run Summary:", result["run_summary"])
