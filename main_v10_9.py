# FILE: main_v10_9.py
"""
Main Entry Point — v10_9 Agentic Workflow (ENTERPRISE REFACTOR)

This module provides the official entrypoint for the unified v10_9
agentic workflow. It is the ONLY module outside the L1–L5 layers that
performs orchestrated end-to-end execution.

Responsibilities:
    • Accept initial state dict from caller (API/CLI/service).
    • Normalize state into L4.StateAdapter.
    • Call L1 (planning) via l1.route_plan.
    • Call L3 (orchestration) via Orchestrator.run().
    • Collect telemetry, return structured WorkflowState.

Non-responsibilities:
    • NO planning logic
    • NO tool/LLM execution
    • NO state mutation beyond adapter
    • NO safety/policy decisions
    • NO provider/SDK logic

Layer purity must be preserved fully.
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
    Normalize the incoming state so that Orchestrator has the minimal
    required top-level keys and metadata.

    Ensures:
        • workflow_id present in root and metadata
        • messages is a list
        • metadata is a dict
        • compat/debug flags stored in metadata
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

    This lives above L1–L5. Failures must not propagate.
    """
    if stream_callback is None:
        return
    try:
        stream_callback({"event": event_type, "payload": payload})
    except Exception:
        # Streaming is best-effort only.
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
            Raw dictionary describing the task and context.

        compat_mode:
            Optional compatibility flag (e.g., "10_7", "10_8"). The value
            is attached to metadata and may influence downstream L1/L2
            components.

        debug_mode:
            Attach extended debug metadata into metadata["debug_mode"].

        stream_callback:
            Optional function receiving streaming events:
                {"event": <str>, "payload": <dict>}

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

    # -------- Normalize & prepare state -------------------------------------
    state = _initialize_state(
        initial_state,
        compat_mode=compat_mode,
        debug_mode=debug_mode,
    )
    workflow_id = state["workflow_id"]

    # -------- Tracking spans -------------------------------------------------
    cost_tracker = CostTracker()

    # -------- L1: PLANNING --------------------------------------------------
    cost_tracker.start_span("planning")
    _emit_stream_event(
        stream_callback,
        event_type="planning_started",
        payload={"workflow_id": workflow_id},
    )

    # Single L1 planning step
    plan = route_plan(state)

    cost_tracker.end_span("planning")
    _emit_stream_event(
        stream_callback,
        event_type="planning_completed",
        payload={"workflow_id": workflow_id, "plan_mode": plan.get("mode")},
    )

    # -------- L3: EXECUTION (L2 + L4 + L5) ----------------------------------
    orchestrator = Orchestrator()

    cost_tracker.start_span("execution")
    # Orchestrator.run is synchronous by design.
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

    # -------- Observability Summary -----------------------------------------
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
    Synchronous wrapper around run_workflow_v10_9().

    This is the primary entrypoint for CLI / local execution systems.
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
