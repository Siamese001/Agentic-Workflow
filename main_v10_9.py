# FILE: v10_9_clean/main_v10_9.py
"""
Main Entry Point — v10_9

This file provides the official entrypoint for the unified 10_9 agentic workflow.

High-level pipeline:
    1. L1: Select mode + generate PlanObject (via plan_router)
    2. L3: Global Orchestrator executes the plan
    3. Return the updated state (L4 adapters can be applied by caller)

This entrypoint does NOT mutate global state and contains NO domain logic.
It only coordinates the L1 → L3 workflow for a single pass.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from l1.plan_router import route_plan
from l3.orchestrator import Orchestrator


# ---------------------------------------------------------------------------
# Internal utilities
# ---------------------------------------------------------------------------

def _initialize_state(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure initial state has required metadata.
    Does NOT modify domain-specific fields.
    """

    state = dict(initial_state or {})
    metadata = state.setdefault("metadata", {})

    # Ensure workflow_id exists
    wf_id = (
        state.get("workflow_id")
        or metadata.get("workflow_id")
        or "workflow_v10_9"
    )
    state["workflow_id"] = wf_id
    metadata["workflow_id"] = wf_id

    # Ensure messages array exists
    if "messages" not in state or not isinstance(state["messages"], list):
        state["messages"] = []

    return state


# ---------------------------------------------------------------------------
# Async entrypoint
# ---------------------------------------------------------------------------

async def run_workflow_v10_9(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single v10_9 workflow cycle.

    Returns:
        A dict representing the updated orchestration state.
    """

    # Pre-process & normalize state
    state = _initialize_state(initial_state)

    # L1 — produce a PlanObject
    plan = route_plan(state)

    # L3 — globally orchestrate execution of this plan
    orchestrator = Orchestrator()
    workflow_state = await orchestrator.run(plan, state)

    # Return final unmutated state
    return dict(workflow_state.state)


# ---------------------------------------------------------------------------
# Synchronous convenience wrapper
# ---------------------------------------------------------------------------

def run_workflow_sync(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Equivalent to run_workflow_v10_9(), but synchronous.

    Usage:
        result = run_workflow_sync({"objective": "draft a summary"})
    """
    return asyncio.run(run_workflow_v10_9(initial_state))


# If executing directly (optional debug mode):
if __name__ == "__main__":
    example = {
        "objective": "create a short summary",
        "messages": [{"role": "user", "content": "Please summarize this into bullets"}],
    }
    out = run_workflow_sync(example)
    print("=== v10_9 workflow output ===")
    print(out)
