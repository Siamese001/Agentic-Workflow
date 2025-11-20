# FILE: 10_10/main_v10_10.py
"""
Main Entry Point — v10_10 Agentic Workflow (L1–L5 Refactor)

This is the v10_10 refactor of the v10_9 main entrypoint. :contentReference[oaicite:1]{index=1}

It no longer uses:
    • PlanObject
    • DAGExecutor
    • StateAdapter
    • SafetyEngine / PolicyEngine / ArbitrationEngine
    • CostTracker
    • Multi-agent or HIL payloads

Instead, it wires together the new, strictly layered architecture:

    • L1: build_workflow_plan_bundle (no LLM, no tools)
    • L2: execute_workflow_plans       (LLM + tools; called inside L3)
    • L3: run_dag                      (DAG + retries + correction surfaces)
    • L4: apply_state_patch            (deterministic state patch; called in L3)
    • L5: safety_gate                  (deterministic safety policy; called in L3)

This module exposes:
    • async run_workflow_v10_10(initial_state, compat_mode, debug_mode, stream_callback)
    • sync  run_workflow_sync_v10_10(...)

It bridges from the v10_9-style "initial_state" dict to the new
typed v10_10 models (JobInput, ResumeInput, WorkflowConfig).
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional, Callable

from models import (
    JobInput,
    ResumeInput,
    WorkflowConfig,
    ExecutionContext,
)
from routing import RoutingPolicy
from registry import build_default_prompt_registry
from runtime_utils import PredictiveCacheManager, SandboxConfig
from l1 import build_workflow_plan_bundle
from l3 import run_dag
from observability import start_span, end_span, record_event


# =============================================================================
# 1. STATE NORMALIZATION (FROM v10_9 STYLE)
# =============================================================================

def _initialize_state(
    initial_state: Optional[Dict[str, Any]],
    *,
    compat_mode: Optional[str],
    debug_mode: bool,
) -> Dict[str, Any]:
    """
    Normalize incoming state dict.

    Ensures:
        • workflow_id is present
        • messages is a list
        • metadata is a dict
        • compat/debug flags are stored in metadata

    This is a simplified v10_10 variant of the v10_9 initializer. :contentReference[oaicite:2]{index=2}
    """
    state: Dict[str, Any] = dict(initial_state or {})
    metadata = state.setdefault("metadata", {})

    workflow_id = (
        state.get("workflow_id")
        or metadata.get("workflow_id")
        or "workflow_v10_10"
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
    Best-effort stream event emission, as in v10_9 main. :contentReference[oaicite:3]{index=3}
    """
    if stream_callback is None:
        return
    try:
        stream_callback({"event": event_type, "payload": payload})
    except Exception:
        # Observability must not break the workflow
        pass


def _extract_job_resume_texts(state: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract job_text and resume_text from a v10_9-style initial_state.

    Mirrors the logic from v10_9 main where possible. :contentReference[oaicite:4]{index=4}
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
# 2. BRIDGE: BUILD TYPED INPUT MODELS FROM STATE
# =============================================================================

def _build_job_input_from_state(state: Dict[str, Any]) -> JobInput:
    """
    Construct a JobInput from v10_9-style state.

    Since v10_9 had a free-form PlanObject, we approximate:
        • title      ← state.get("job_title") or "Unknown Role"
        • role_type  ← state.get("role_type") or "unspecified"
        • seniority  ← state.get("seniority") or "unspecified"
        • posting_text ← job_text extracted from state
        • requirements ← state.get("requirements", []) if present
    """
    jt = _extract_job_resume_texts(state)["job_text"]

    return JobInput(
        title=str(state.get("job_title") or "Unknown Role"),
        role_type=str(state.get("role_type") or "unspecified"),
        seniority=str(state.get("seniority") or "unspecified"),
        posting_text=jt,
        requirements=list(state.get("requirements", [])),
    )


def _build_resume_input_from_state(state: Dict[str, Any]) -> ResumeInput:
    """
    Construct a ResumeInput from v10_9-style state.

    We look into state["resume"]["master_resume"] if available.
    """
    resume_root = (state.get("resume") or {}).get("master_resume") or {}
    if not isinstance(resume_root, dict):
        resume_root = {}

    return ResumeInput(
        name=str(resume_root.get("name", "Candidate")),
        email=resume_root.get("email"),
        phone=resume_root.get("phone"),
        linkedin=resume_root.get("linkedin"),
        summary=resume_root.get("summary"),
        experience_sections=list(resume_root.get("professional_experience", [])),
        skills=list(resume_root.get("skills", [])),
        projects=list(resume_root.get("projects", [])),
    )


def _build_config_from_state(state: Dict[str, Any]) -> WorkflowConfig:
    """
    Optionally pick up config hints from state; otherwise use defaults.
    """
    cfg = state.get("config") or {}
    return WorkflowConfig(
        cost_budget=float(cfg.get("cost_budget", 0.10)),
        latency_slo_ms=int(cfg.get("latency_slo_ms", 3000)),
        safety_sensitivity=int(cfg.get("safety_sensitivity", 3)),
        drafting_depth=int(cfg.get("drafting_depth", 3)),
        target_tone=str(cfg.get("target_tone", "professional")),
        target_total_tokens=int(cfg.get("target_total_tokens", 1800)),
    )


# =============================================================================
# 3. ASYNC ENTRYPOINT (v10_10)
# =============================================================================

async def run_workflow_v10_10(
    initial_state: Dict[str, Any],
    *,
    compat_mode: Optional[str] = None,
    debug_mode: bool = False,
    stream_callback: Optional[Callable[[Dict[str, Any]], Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a single v10_10 agentic workflow pass, starting from a v10_9-style
    initial_state dict but using the v10_10 L1–L5 architecture.
    """

    # ---------- Normalize state ----------
    state = _initialize_state(initial_state, compat_mode=compat_mode, debug_mode=debug_mode)
    workflow_id = state["workflow_id"]

    _emit_stream_event(
        stream_callback,
        event_type="workflow_started",
        payload={"workflow_id": workflow_id},
    )

    # ---------- Build Typed Inputs ----------
    job = _build_job_input_from_state(state)
    resume = _build_resume_input_from_state(state)
    config = _build_config_from_state(state)

    # ---------- Build DI Components ----------
    routing_policy = RoutingPolicy()
    prompt_registry = build_default_prompt_registry()
    sandbox = SandboxConfig()
    cache_manager = PredictiveCacheManager(max_entries=1024)

    # ---------- Build ExecutionContext ----------
    ctx = ExecutionContext(
        job=job,
        resume=resume,
        config=config,
        routing_policy=routing_policy,
        sandbox_config=sandbox,
        prompt_registry=prompt_registry,
        cache_manager=cache_manager,
        meta_profile_snapshot=None,  # future: integrate meta_profile
    )

    # ---------- L1 Planning ----------
    planning_span = start_span("planning", ctx=ctx.span_context())
    plans = build_workflow_plan_bundle(
        job=job,
        resume=resume,
        config=config,
        meta_profile=None,
        routing_policy=routing_policy,
        prompt_registry=prompt_registry,
    )
    end_span(planning_span)

    _emit_stream_event(
        stream_callback,
        event_type="planning_completed",
        payload={"workflow_id": workflow_id, "complexity": plans.strategy.complexity.value},
    )

    # ---------- L3 DAG Orchestration (L2 + L4 + L5) ----------
    exec_span = start_span("execution", ctx=ctx.span_context())
    dag_result = run_dag(ctx, plans, max_retries=2)
    end_span(exec_span)

    _emit_stream_event(
        stream_callback,
        event_type="execution_completed",
        payload={
            "workflow_id": workflow_id,
            "corrected": dag_result.corrected,
            "safety_passed": dag_result.safety_passed,
        },
    )

    # ---------- Build Final Output ----------
    final_state_patch = dag_result.final_state_patch

    result = {
        "workflow_id": workflow_id,
        "state_patch": final_state_patch,
        "safety_passed": dag_result.safety_passed,
        "corrected": dag_result.corrected,
        # L2 raw results (optional, for debugging / downstream processing)
        "l2_results": {
            "strategy": dag_result.l2_results.strategy.model_dump(),
            "rag": dag_result.l2_results.rag.model_dump(),
            "drafting": dag_result.l2_results.drafting.model_dump(),
            "qa": dag_result.l2_results.qa.model_dump(),
            "safety": dag_result.l2_results.safety.model_dump(),
        },
    }

    _emit_stream_event(
        stream_callback,
        event_type="workflow_completed",
        payload={
            "workflow_id": workflow_id,
            "safety_passed": dag_result.safety_passed,
            "corrected": dag_result.corrected,
        },
    )

    return result


# =============================================================================
# 4. SYNC WRAPPER
# =============================================================================

def run_workflow_sync_v10_10(
    initial_state: Dict[str, Any],
    *,
    compat_mode: Optional[str] = None,
    debug_mode: bool = False,
    stream_callback: Optional[Callable[[Dict[str, Any]], Any]] = None,
) -> Dict[str, Any]:
    """
    Blocking wrapper around run_workflow_v10_10() for CLI/local execution.
    """
    return asyncio.run(
        run_workflow_v10_10(
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
        "job_description": "Senior AI leader role overseeing ML platforms.",
        "messages": [
            {"role": "user", "content": "Summarize my profile for an executive recruiter."}
        ],
        "resume": {
            "master_resume": {
                "name": "Senior AI Leader",
                "summary": "Senior leader with 15+ years of experience in AI, data, and product.",
                "professional_experience": [],
                "skills": ["AI", "ML", "Cloud"],
            }
        },
    }

    def _print_stream(event: Dict[str, Any]) -> None:
        print(f"[STREAM] {event['event']}: {event['payload']}")

    result = run_workflow_sync_v10_10(
        example_state,
        compat_mode=None,
        debug_mode=True,
        stream_callback=_print_stream,
    )
    print("=== v10_10 Workflow Result ===")
    print(json.dumps(result, indent=2))
