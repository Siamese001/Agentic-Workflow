# FILE: main_v10_10.py
"""
Main Orchestration Entrypoint (v10_10 · Phase 2)
================================================

This is the top-level runtime entrypoint for the v10_10 workflow.

Phase-2 guarantees:
    • Pure orchestration only — NO LLM calls here.
    • All LLM calls route through L2 → cognitive_agents → prompt_builder.
    • All prompts routed through prompt_system_v10_10 with ACL enforcement.
    • All state mutation (future L4) strictly excluded here.
    • All model routing governed via RoutingPolicy.
    • Observability spans for the entire workflow.
    • Deterministic execution: L1 → L2 → L3/L5 orchestration pattern.

Valid high-level data flow:
    1. L1:   planning only (no tools, no LLM).
    2. L2:   LLM execution (strategy, drafting, QA, safety pre-check).
    3. L3:   control flow, retries, fallback behaviors.
    4. L4:   state updates (disabled until Phase 4).
    5. L5:   safety enforcement (policy finalization).

This file constructs:
    • ExecutionContext
    • Performs L1 planning
    • Calls L2 workflow executor
    • Applies L3/L5 enforcement logic
    • Returns a final structured result bundle
"""

from __future__ import annotations

import traceback
from typing import Optional

from models import (
    JobInput,
    ResumeInput,
    WorkflowConfig,
    WorkflowPlanBundle,
    ExecutionContext,
    FinalWorkflowResult,
)

from observability import start_span, end_span, log_exception, record_event
from l1 import generate_workflow_plans
from l2 import execute_workflow_plans
from l3 import orchestrate_l3_fallbacks
from l5 import enforce_final_safety_policy

from routing import RoutingPolicy
from runtime_utils import SandboxConfig
from meta_profile import load_meta_profile_snapshot


# =============================================================================
# Initialization Helpers
# =============================================================================


def _build_execution_context(
    *,
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    routing_policy: Optional[RoutingPolicy] = None,
    sandbox: Optional[SandboxConfig] = None,
) -> ExecutionContext:
    """
    Build the typed ExecutionContext consumed by all layers.
    """
    rp = routing_policy or RoutingPolicy.from_config(config)
    sb = sandbox or SandboxConfig()

    meta = load_meta_profile_snapshot(
        job=job,
        resume=resume,
        config=config,
    )

    return ExecutionContext(
        job=job,
        resume=resume,
        config=config,
        routing_policy=rp,
        sandbox_config=sb,
        cache_manager=None,
        prompt_registry=None,
        meta_profile_snapshot=meta,
    )


# =============================================================================
# Main Orchestration Entry Point
# =============================================================================


def run_workflow(
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
) -> FinalWorkflowResult:
    """
    Single public API for executing the full v10_10 workflow.

    Validated processing order:
        1. Build ExecutionContext
        2. L1: planning (pure reasoning)
        3. L2: execution (LLM calls)
        4. L3: fallback & recovery routing
        5. L5: enforce safety policy
        6. Return FinalWorkflowResult
    """

    top_span = start_span("workflow.run", {"job": job.title, "resume": resume.name})

    try:
        # ------------------------------------------------------------------
        # Build unified context
        # ------------------------------------------------------------------
        ctx = _build_execution_context(job=job, resume=resume, config=config)
        record_event("workflow.context_ready")

        # ------------------------------------------------------------------
        # L1 – Planning (NO LLM calls, no retrieval)
        # ------------------------------------------------------------------
        l1_span = start_span("workflow.l1_planning")
        try:
            plans: WorkflowPlanBundle = generate_workflow_plans(job, resume, config)
            record_event("workflow.l1_completed")
        except Exception as exc:
            log_exception("workflow.l1_error", exc)
            end_span(l1_span)
            raise
        end_span(l1_span)

        # ------------------------------------------------------------------
        # L2 – Execution (all LLM calls routed through cognitive agents)
        # ------------------------------------------------------------------
        l2_span = start_span("workflow.l2_execute")
        try:
            l2_results = execute_workflow_plans(plans, ctx)
            record_event("workflow.l2_completed")
        except Exception as exc:
            log_exception("workflow.l2_error", exc)
            end_span(l2_span)
            raise
        end_span(l2_span)

        # ------------------------------------------------------------------
        # L3 – Orchestration / fallback logic
        # ------------------------------------------------------------------
        l3_span = start_span("workflow.l3_orchestration")
        try:
            l3_results = orchestrate_l3_fallbacks(
                l2_results=l2_results,
                plans=plans,
                ctx=ctx,
            )
            record_event("workflow.l3_completed")
        except Exception as exc:
            log_exception("workflow.l3_error", exc)
            end_span(l3_span)
            raise
        end_span(l3_span)

        # ------------------------------------------------------------------
        # L5 – Final safety enforcement (policy layer)
        # ------------------------------------------------------------------
        l5_span = start_span("workflow.l5_safety")
        try:
            safe_result = enforce_final_safety_policy(
                l3_results=l3_results,
                safety_plan=plans.safety,
                ctx=ctx,
            )
            record_event("workflow.l5_completed")
        except Exception as exc:
            log_exception("workflow.l5_error", exc)
            end_span(l5_span)
            raise
        end_span(l5_span)

        # ------------------------------------------------------------------
        # Final output
        # ------------------------------------------------------------------
        return FinalWorkflowResult(
            job=job,
            resume=resume,
            config=config,
            strategy=l2_results.strategy,
            rag=l2_results.rag,
            drafting=l2_results.drafting,
            qa=l3_results.qa,
            safety=safe_result,
        )

    except Exception as exc:
        log_exception("workflow.fatal", exc)
        traceback.print_exc()
        raise

    finally:
        end_span(top_span)
