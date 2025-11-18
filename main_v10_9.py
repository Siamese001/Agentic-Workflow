# FILE: main_v10_9.py
"""
Main Entry Point — v10_9 Agentic Workflow (ENTERPRISE REFACTOR)

This module provides the official entrypoint for the unified v10_9
agentic workflow.

It extends the original v10_9 entrypoint to fully support the
Enterprise / Production feature set from the 10_7 → 10_9
refactoring plan while preserving strict L1–L5 purity:

High-level pipeline:
    1. L1: route_plan() – produce a PlanObject for the requested task.
    2. L3: Orchestrator.run() – execute domain-specific pipeline (L2 + L4 + L5).
    3. Observability: summarize_run() – produce a structured run summary.
    4. Optional streaming: emit intermediate snapshots via callback.
    5. Return: updated state + phase + summary.

Design guarantees:
    • No direct references to previous versions (10_7, 10_8, LangGraph, etc.)
    • Single-pass execution (one L1 plan → one L3 run)
    • Layer purity (no L1–L5 logic in this file, only coordination)
    • Backward-compatible API:
        - Existing code can still call run_workflow_v10_9(initial_state)
        - New keyword-only parameters support compat_mode, debug_mode, streaming
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, Callable

from l1 import route_plan
from l3 import Orchestrator
from runtime_utils import CostTracker
from observability import summarize_run


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------


def _initialize_state(
    initial_state: Dict[str, Any],
    *,
    compat_mode: Optional[str] = None,
    debug_mode: bool = False,
) -> Dict[str, Any]:
    """
    Normalize the incoming state so that the orchestrator has
    all expected top-level keys and metadata, while remaining
    backward-compatible with earlier v10_9 usage.

    Ensures:
        • workflow_id present in root and metadata
        • messages is a list
        • metadata is a dict
        • compat_mode and debug_mode flags are stored in metadata
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

    # Attach compat/debug flags in a non-breaking way
    if compat_mode is not None:
        metadata["compat_mode"] = str(compat_mode)
    metadata["debug_mode"] = bool(debug_mode)

    return state


def _emit_stream_event(
    stream_callback: Optional[Callable[[Dict[str, Any]], Any]],
    *,
    event_type: str,
    payload: Dict[str, Any],
) -> None:
    """
    Lightweight event streaming hook.

    This is intentionally simple and lives outside L1–L5. It can be
    used by UIs or services that need progress updates (e.g., phase
    transitions, final result). Failures must never affect the main
    workflow.
    """
    if stream_callback is None:
        return
    try:
        stream_callback({"event": event_type, "payload": payload})
    except Exception:
        # Streaming is best-effort only; errors are swallowed.
        pass


# ---------------------------------------------------------------------------
# ASYNC ENTRYPOINT
# ---------------------------------------------------------------------------


async def run_workflow_v10_9(
    initial_state: Dict[str, Any],
    *,
    compat_mode: Optional[str] = None,
    debug_mode: bool = False,
    stream_callback: Optional[Callable[[Dict[str, Any]], Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a single v10_9 agentic workflow pass.

    Args:
        initial_state:
            dict describing the task, context, and any prior state to be
            used by L1.

        compat_mode:
            Optional compatibility mode flag for callers that want to
            emulate older behavior (e.g., v10_7/v10_8). This function
            itself does not change behavior based on compat_mode, but
            the flag is stored in state["metadata"]["compat_mode"] for
            downstream use by L1/L2/L3 if they choose to inspect it.

        debug_mode:
            Optional boolean to request additional debug metadata in the
            state["metadata"] block. This function sets the flag; L1–L5
            layers remain free to decide how to honor it.

        stream_callback:
            Optional callable that receives streaming events of the form:
                {"event": <str>, "payload": <dict>}
            Event types currently emitted:
                • "planning_started"
                • "planning_completed"
                • "execution_completed"
                • "workflow_completed"

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
    state = _initialize_state(initial_state, compat_mode=compat_mode, debug_mode=debug_mode)
    workflow_id = state["workflow_id"]

    # Tracking cost/timing spans
    cost_tracker = CostTracker()

    # ---- L1: PLANNING ----
    cost_tracker.start_span("planning")
    _emit_stream_event(
        stream_callback,
        event_type="planning_started",
        payload={"workflow_id": workflow_id},
    )
    plan = route_plan(state)
    cost_tracker.end_span("planning")
    _emit_stream_event(
        stream_callback,
        event_type="planning_completed",
        payload={"workflow_id": workflow_id, "plan_mode": plan.get("mode")},
    )

    # ---- L3: ORCHESTRATION + L2/L4/L5 ----
    orchestrator = Orchestrator()
    cost_tracker.start_span("execution")
    # Orchestrator.run is synchronous; we just call it directly.
    workflow_state = orchestrator.run(plan, state)
    cost_tracker.end_span("execution")
    _emit_stream_event(
        stream_callback,
        event_type="execution_completed",
        payload={
            "workflow_id": workflow_id,
            "phase": workflow_state.phase,
            "phase_history": workflow_state.phase_metadata.get(
                "history", [workflow_state.phase]
            ),
        },
    )

    final_state = workflow_state.state
    phase_history = workflow_state.phase_metadata.get("history", [workflow_state.phase])

    # ---- Observability Summary ----
    run_summary = summarize_run(
        workflow_id=workflow_id,
        state=final_state,
        phase_history=phase_history,
        cost_tracker=cost_tracker,
    )

    result = {
        "workflow_id": workflow_id,
        "phase": workflow_state.phase,
        "state": final_state,
        "phase_metadata": workflow_state.phase_metadata,
        "run_summary": run_summary,
    }

    _emit_stream_event(
        stream_callback,
        event_type="workflow_completed",
        payload={
            "workflow_id": workflow_id,
            "phase": workflow_state.phase,
            "summary": run_summary,
        },
    )

    return result


# ---------------------------------------------------------------------------
# SYNC WRAPPER
# ---------------------------------------------------------------------------


def run_workflow_sync(
    initial_state: Dict[str, Any],
    *,
    compat_mode: Optional[str] = None,
    debug_mode: bool = False,
    stream_callback: Optional[Callable[[Dict[str, Any]], Any]] = None,
) -> Dict[str, Any]:
    """
    Synchronous convenience wrapper around run_workflow_v10_9().

    Backward-compatible: existing callers can still call this with
    only the initial_state positional argument.
    """
    return asyncio.run(
        run_workflow_v10_9(
            initial_state,
            compat_mode=compat_mode,
            debug_mode=debug_mode,
            stream_callback=stream_callback,
        )
    )


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

    def _print_stream_event(event: Dict[str, Any]) -> None:
        print(f"[STREAM] {event['event']}: {event['payload']}")

    result = run_workflow_sync(
        example_state,
        compat_mode=None,
        debug_mode=True,
        stream_callback=_print_stream_event,
    )
    print("=== v10_9 Agentic Workflow Output ===")
    print("Workflow ID:", result["workflow_id"])
    print("Final Phase:", result["phase"])
    print("Run Summary:", result["run_summary"])
