# FILE: main_v10_9.py
"""
Main Entry Point — v10_9 Agentic Workflow (META-AWARE, FULL STACK L1–L5)

This module is the ONLY top-level orchestrator responsible for running
the entire agentic workflow end-to-end. It coordinates all layers:

    • L1: Planning (strategy, rag, drafting, bullets, qa, safety, meta, prompt_eng)
    • L2: Execution (retrieval, drafting, QA, safety evaluation, meta)
    • L3: Orchestration (DAG execution)
    • L4: State (memory, patches, correction logs)
    • L5: Safety, Policy, Arbitration

Additionally, this refactored version fully incorporates the META
profile biasing layer based on 10_8 → 10_9 restoration and the 14
OpenAI agentic subdomain requirements.

KEY FEATURES (UPGRADED):

    • Fully typed PlanObject and ExecutionResult flows.
    • Deterministic DAG-based execution via L3.
    • Stream callbacks for observability (optional).
    • Meta-profile integration (planning, routing, safety, correction).
    • Safety + policy + arbitration pipeline at the end of run.
    • Run summary injected with safety, policy, arbitration, meta-profile.

This file contains NO business logic, NO tool calls, NO reasoning,
NO planning. Its purpose is purely orchestration across layers.
"""

from __future__ import annotations
import asyncio
from typing import Any, Dict, Optional, Callable

# L1
from core.l1 import plan as l1_plan

# L3
from core.l3 import DAGExecutor

# L4
from core.l4 import StateAdapter

# L5
from core.l5 import SafetyEngine, PolicyEngine, ArbitrationEngine, SafetyMode

# MODELS
from models import (
    PlanObject,
    FramingProfile,
    ContextProfile,
    ToolingProfile,
    SafetyOutputProfile,
    AccessPolicy,
)

# OBSERVABILITY
from runtime.observability.utils import summarize_run

# RUNTIME UTILS
from runtime.runtime_utils_v10_9 import CostTracker


# =============================================================================
# 1. INTERNAL HELPERS
# =============================================================================

def _initialize_state(
    initial_state: Optional[Dict[str, Any]],
    *,
    compat_mode: Optional[str],
    debug_mode: bool,
) -> Dict[str, Any]:
    """
    Normalize incoming state for orchestration.

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

    # Ensure messages exist
    if not isinstance(state.get("messages"), list):
        state["messages"] = []

    # Compat + debug metadata
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
    Best-effort stream event emission.
    """
    if stream_callback is None:
        return
    try:
        stream_callback({"event": event_type, "payload": payload})
    except Exception:
        pass  # never break main workflow


def _build_profiles(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the typed FramingProfile, ContextProfile, ToolingProfile,
    SafetyOutputProfile, AccessPolicy used by L1 planners.
    """
    objective = str(state.get("objective", ""))
    audience = str(state.get("audience", "general"))
    domain = str(state.get("domain", "generic"))

    framing = FramingProfile(
        goal=objective or "agentic_workflow_run",
        success_criteria=[],
        failure_modes=[],
        guardrails=[],
        domain=domain,
        audience=audience,
        tone="professional",
    )

    context_profile = ContextProfile()
    tooling_profile = ToolingProfile()
    safety_profile = SafetyOutputProfile()
    access_policy = AccessPolicy()

    return {
        "framing_profile": framing,
        "context_profile": context_profile,
        "tooling_profile": tooling_profile,
        "safety_profile": safety_profile,
        "access_policy": access_policy,
    }


def _extract_job_resume_texts(state: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract job_text and resume_text (used across all L1 plans).
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


# =============================================================================
# 2. BUILD MASTER PLAN FROM L1
# =============================================================================

def _build_master_plan(state: Dict[str, Any]) -> PlanObject:
    """
    Build a PLAN for the entire workflow: strategy → rag → drafting → bullets →
    qa → safety → meta_learning → prompt_engineering.

    This includes constructing the DAG structure required by L3.
    """

    profiles = _build_profiles(state)
    jrt = _extract_job_resume_texts(state)

    modes = [
        "strategy",
        "rag",
        "drafting",
        "bullets",
        "qa",
        "safety",
        "meta_learning",
        "prompt_engineering",
    ]

    per_mode_plans = {}
    for mode in modes:
        per_mode_plans[mode] = l1_plan(
            mode=mode,
            job_text=jrt["job_text"],
            resume_text=jrt["resume_text"],
            framing_profile=profiles["framing_profile"],
            context_profile=profiles["context_profile"],
            tooling_profile=profiles["tooling_profile"],
            safety_profile=profiles["safety_profile"],
            access_policy=profiles["access_policy"],
        )

    # Build DAG nodes
    dag_nodes = [
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

    master_dict = per_mode_plans["strategy"].to_dict()
    master_dict["mode"] = "orchestration"
    master_dict["workflow_id"] = state.get("workflow_id", "workflow_v10_9")
    master_dict["dag"] = {"nodes": dag_nodes}

    return PlanObject(master_dict)


# =============================================================================
# 3. ASYNC ENTRYPOINT
# =============================================================================

async def run_workflow_v10_9(
    initial_state: Dict[str, Any],
    *,
    compat_mode: Optional[str] = None,
    debug_mode: bool = False,
    stream_callback: Optional[Callable[[Dict[str, Any]], Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a single v10_9 agentic workflow pass.
    """

    # ---------- Normalize state ----------
    state = _initialize_state(initial_state, compat_mode=compat_mode, debug_mode=debug_mode)
    workflow_id = state["workflow_id"]

    cost_tracker = CostTracker()

    _emit_stream_event(stream_callback, event_type="workflow_started", payload={"workflow_id": workflow_id})

    # ---------- Initialize L4 ----------
    state_adapter = StateAdapter()
    state_adapter.reset(state)
    state = state_adapter.state

    # ---------- L1 Planning ----------
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

    # ---------- L3 Orchestration (DAG + L2 + L4) ----------
    dag_executor = DAGExecutor(state_adapter=state_adapter)

    cost_tracker.start_span("execution")
    workflow_state = dag_executor.run(plan, state)
    cost_tracker.end_span("execution")

    _emit_stream_event(
        stream_callback,
        event_type="execution_completed",
        payload={"workflow_id": workflow_id, "phase": workflow_state.phase.value},
    )

    final_state = workflow_state.result
    phase_history = workflow_state.metadata.get("history", [workflow_state.phase.value])
    phase_metadata = {"history": phase_history}

    # ---------- L5: Safety / Policy / Arbitration ----------
    safety_engine = SafetyEngine()
    safety_report = safety_engine.evaluate_content(final_state, plan)

    mode = SafetyMode.BALANCED
    policy_engine = PolicyEngine(base_mode=mode)
    policy_decision = policy_engine.review(safety_report)

    arb_engine = ArbitrationEngine()
    arbitration = arb_engine.arbitrate(policy_decision, safety_report)

    _emit_stream_event(
        stream_callback,
        event_type="safety_evaluated",
        payload={
            "workflow_id": workflow_id,
            "policy_decision": policy_decision,
            "arbitration": arbitration.to_dict() if hasattr(arbitration, "to_dict") else vars(arbitration),
        },
    )

    # ---------- Observability Summary ----------
    run_summary = summarize_run(
        workflow_id=workflow_id,
        state=final_state,
        phase_history=phase_history,
        cost_tracker=cost_tracker,
    )

    run_summary.setdefault("safety", {})
    run_summary["safety"]["report"] = safety_report
    run_summary["safety"]["policy"] = policy_decision
    run_summary["safety"]["arbitration"] = arbitration.to_dict() if hasattr(arbitration, "to_dict") else vars(arbitration)

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


# =============================================================================
# 4. SYNC WRAPPER
# =============================================================================

def run_workflow_sync(
    initial_state: Dict[str, Any],
    *,
    compat_mode: Optional[str] = None,
    debug_mode: bool = False,
    stream_callback: Optional[Callable[[Dict[str, Any]], Any]] = None,
) -> Dict[str, Any]:
    """
    Blocking wrapper around run_workflow_v10_9() for CLI/local execution.
    """
    return asyncio.run(
        run_workflow_v10_9(
            initial_state,
            compat_mode=compat_mode,
            debug_mode=debug_mode,
            stream_callback=stream_callback,
        )
    )


# =============================================================================
# 5. OPTIONAL CLI TEST
# =============================================================================

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

    def _print_stream(event: Dict[str, Any]) -> None:
        print(f"[STREAM] {event['event']}: {event['payload']}")

    result = run_workflow_sync(
        example_state,
        compat_mode=None,
        debug_mode=True,
        stream_callback=_print_stream,
    )
    print("=== v10_9 Agentic Workflow Output ===")
    print("Workflow ID:", result["workflow_id"])
    print("Final Phase:", result["phase"])
    print("Run Summary:", result["run_summary"])
