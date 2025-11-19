# FILE: main_v10_9.py
"""
Main Entry Point — v10_9 Agentic Workflow (ENTERPRISE REFACTOR, RESTORED)

This module provides the official entrypoint for the unified v10_9
agentic workflow. It is the ONLY module outside the L1–L5 layers that
performs orchestrated end-to-end execution.

Responsibilities:
    • Accept initial state dict from caller (API/CLI/service).
    • Normalize state into L4.StateAdapter.
    • Build a multi-mode L1 master PlanObject (strategy → rag → drafting → bullets → qa → safety → meta).
    • Execute the plan via L3 DAGExecutor (which calls L2 and L4).
    • Evaluate final content via L5 SafetyEngine/PolicyEngine/ArbitrationEngine.
    • Collect telemetry, return structured WorkflowState + summary.

Non-responsibilities:
    • NO planning logic beyond invoking L1.
    • NO tool/LLM execution (L2 only).
    • NO DAG logic (L3 only).
    • NO state mutation beyond adapter (L4 only).
    • NO raw safety/policy logic (L5 only).
    • NO provider/SDK logic.

Layer purity must be preserved fully.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, Callable, List

from l1 import plan as l1_plan
from l3 import DAGExecutor
from l4 import StateAdapter
from l5 import SafetyEngine, PolicyEngine, ArbitrationEngine, SafetyMode
from models import (
    PlanObject,
    FramingProfile,
    ContextProfile,
    ToolingProfile,
    SafetyOutputProfile,
    AccessPolicy,
)
from runtime_utils import CostTracker
from observability import summarize_run


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------


def _initialize_state(
    initial_state: Optional[Dict[str, Any]],
    *,
    compat_mode: Optional[str],
    debug_mode: bool,
) -> Dict[str, Any]:
    """Normalize incoming state for orchestration.

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
    """Lightweight event streaming hook.

    This lives above L1–L5. Failures must not propagate.
    """
    if stream_callback is None:
        return
    try:
        stream_callback({"event": event_type, "payload": payload})
    except Exception:
        # Streaming is best-effort only.
        pass


def _build_profiles(state: Dict[str, Any]) -> Dict[str, Any]:
    """Construct framing/context/tooling/safety profiles from state.

    This is a thin adapter to feed L1 planners with typed contracts.
    """
    objective = str(state.get("objective", ""))
    audience = str(state.get("audience", "general"))
    domain = str(state.get("domain", "generic"))

    framing = FramingProfile(
        goal=objective or "agentic_workflow_run",
        success_criteria=[],
        failure_modes=[],
        guardrails=[],
        domain=domain or None,
        audience=audience or None,
        tone="professional",
    )

    context_profile = ContextProfile()
    tooling_profile = ToolingProfile()
    safety_profile = SafetyOutputProfile()  # uses default BALANCED mode
    access_policy = AccessPolicy()  # no explicit restrictions by default

    return {
        "framing_profile": framing,
        "context_profile": context_profile,
        "tooling_profile": tooling_profile,
        "safety_profile": safety_profile,
        "access_policy": access_policy,
    }


def _extract_job_and_resume_text(state: Dict[str, Any]) -> Dict[str, str]:
    """Best-effort extraction of job_text and resume_text from state.

    This mirrors v10_8 behavior where L1 planners inferred from JD and
    resume strings. If these are absent, we degrade gracefully.
    """
    job_text = str(
        state.get("job_description")
        or state.get("job_text")
        or state.get("jd_text")
        or ""
    )

    resume_summary = ""
    resume = (state.get("resume") or {}).get("master_resume") or {}
    if isinstance(resume, dict):
        resume_summary = str(resume.get("summary", ""))

    return {"job_text": job_text, "resume_text": resume_summary}


def _build_master_plan(state: Dict[str, Any]) -> PlanObject:
    """Build a multi-mode PlanObject for DAGExecutor.

    Modes included (v10_8 parity):
        • strategy
        • rag
        • drafting
        • bullets
        • qa
        • safety
        • meta_learning
        • prompt_engineering
    """
    profiles = _build_profiles(state)
    jt_rt = _extract_job_and_resume_text(state)

    # Per-mode planning from L1
    modes: List[str] = [
        "strategy",
        "rag",
        "drafting",
        "bullets",
        "qa",
        "safety",
        "meta_learning",
        "prompt_engineering",
    ]

    per_mode_plans: Dict[str, PlanObject] = {}
    for mode in modes:
        per_mode_plans[mode] = l1_plan(
            mode=mode,
            job_text=jt_rt["job_text"],
            resume_text=jt_rt["resume_text"],
            framing_profile=profiles["framing_profile"],
            context_profile=profiles["context_profile"],
            tooling_profile=profiles["tooling_profile"],
            safety_profile=profiles["safety_profile"],
            access_policy=profiles["access_policy"],
        )

    # DAG nodes: linear chain with a few convergences
    dag_nodes: List[Dict[str, Any]] = [
        {
            "name": "strategy",
            "mode": "strategy",
            "depends_on": [],
            "max_retries": 0,
            "plan": per_mode_plans["strategy"].to_dict(),
        },
        {
            "name": "rag",
            "mode": "rag",
            "depends_on": ["strategy"],
            "max_retries": 1,
            "plan": per_mode_plans["rag"].to_dict(),
        },
        {
            "name": "drafting",
            "mode": "drafting",
            "depends_on": ["strategy", "rag"],
            "max_retries": 1,
            "plan": per_mode_plans["drafting"].to_dict(),
        },
        {
            "name": "bullets",
            "mode": "bullets",
            "depends_on": ["drafting"],
            "max_retries": 0,
            "plan": per_mode_plans["bullets"].to_dict(),
        },
        {
            "name": "qa",
            "mode": "qa",
            "depends_on": ["drafting"],
            "max_retries": 0,
            "plan": per_mode_plans["qa"].to_dict(),
        },
        {
            "name": "safety",
            "mode": "safety",
            "depends_on": ["qa"],
            "max_retries": 0,
            "plan": per_mode_plans["safety"].to_dict(),
        },
        {
            "name": "meta_learning",
            "mode": "meta_learning",
            "depends_on": ["safety"],
            "max_retries": 0,
            "plan": per_mode_plans["meta_learning"].to_dict(),
        },
        {
            "name": "prompt_engineering",
            "mode": "prompt_engineering",
            "depends_on": ["strategy"],
            "max_retries": 0,
            "plan": per_mode_plans["prompt_engineering"].to_dict(),
        },
    ]

    # Base plan uses strategy plan as a seed
    master_dict = per_mode_plans["strategy"].to_dict()
    master_dict["mode"] = "orchestration"
    master_dict["workflow_id"] = state.get("workflow_id", "workflow_v10_9")
    master_dict["dag"] = {"nodes": dag_nodes}

    return PlanObject(master_dict)


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
    """Execute a single v10_9 agentic workflow pass.

    Args:
        initial_state:
            Raw dictionary describing the task and context.

        compat_mode:
            Optional compatibility flag (e.g., "10_7", "10_8").
            The value is attached to metadata and may influence downstream
            components (L1–L3) in future extensions.

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

    cost_tracker = CostTracker()

    _emit_stream_event(
        stream_callback,
        event_type="workflow_started",
        payload={"workflow_id": workflow_id},
    )

    # -------- Initialize L4 StateAdapter ------------------------------------
    state_adapter = StateAdapter()
    state_adapter.reset(state)
    state = state_adapter.state

    # -------- L1: PLANNING --------------------------------------------------
    _emit_stream_event(
        stream_callback,
        event_type="planning_started",
        payload={"workflow_id": workflow_id},
    )

    cost_tracker.start_span("planning")
    plan = _build_master_plan(state)
    cost_tracker.end_span("planning")

    _emit_stream_event(
        stream_callback,
        event_type="planning_completed",
        payload={"workflow_id": workflow_id, "plan_mode": plan.get("mode")},
    )

    # -------- L3: EXECUTION (DAG + L2 + L4) ---------------------------------
    dag_executor = DAGExecutor(state_adapter=state_adapter)

    cost_tracker.start_span("execution")
    workflow_state = dag_executor.run(plan, state)
    cost_tracker.end_span("execution")

    _emit_stream_event(
        stream_callback,
        event_type="execution_completed",
        payload={
            "workflow_id": workflow_id,
            "phase": workflow_state.phase.value,
        },
    )

    # Normalize WorkflowState (new v10_9) to legacy-compatible shape
    final_state = workflow_state.result
    phase_history = workflow_state.metadata.get("history", [workflow_state.phase.value])
    phase_metadata = {"history": phase_history}

    # -------- L5: SAFETY / POLICY / ARBITRATION -----------------------------
    safety_engine = SafetyEngine()
    safety_report = safety_engine.evaluate_content(final_state, plan)

    # Default to BALANCED mode; can be extended via compat metadata.
    mode = SafetyMode.BALANCED
    policy_engine = PolicyEngine(mode=mode)
    policy_decision = policy_engine.review(safety_report)

    arb_engine = ArbitrationEngine()
    arbitration = arb_engine.decide(policy_decision, safety_report)

    _emit_stream_event(
        stream_callback,
        event_type="safety_evaluated",
        payload={
            "workflow_id": workflow_id,
            "policy_decision": policy_decision,
            "arbitration": arbitration,
        },
    )

    # -------- Observability Summary -----------------------------------------
    run_summary = summarize_run(
        workflow_id=workflow_id,
        state=final_state,
        phase_history=phase_history,
        cost_tracker=cost_tracker,
    )
    # Attach safety/policy/arbitration to run_summary for richer telemetry.
    run_summary.setdefault("safety", {})
    run_summary["safety"]["report"] = safety_report
    run_summary["safety"]["policy"] = policy_decision
    run_summary["safety"]["arbitration"] = arbitration

    result = {
        "workflow_id": workflow_id,
        "phase": workflow_state.phase.value,
        "state": final_state,
        "phase_metadata": phase_metadata,
        "run_summary": run_summary,
    }

    _emit_stream_event(
        stream_callback,
        event_type="workflow_completed",
        payload={
            "workflow_id": workflow_id,
            "phase": workflow_state.phase.value,
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
    """Synchronous wrapper around run_workflow_v10_9().

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
        print(f"[STREAM] {event['event']}: {event['payload']}")  # type: ignore[index]

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
