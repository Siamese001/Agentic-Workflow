# FILE: 10_10/main_v10_10.py
"""
Main Pipeline Entrypoint (v10_10 · Phase 2)
===========================================

This file defines the *top-level* runtime API for executing the full
agentic workflow.

Responsibilities:
    • Construct the ExecutionContext (routing, sandbox, profiles, metadata)
    • Run L1 planning (pure, no LLMs)
    • Run L2 execution (LLMs + retrieval)
    • Run L3 orchestration (clean sequencing + retries if configured)
    • Run L4 mutation (state adapter; context writing)
    • Run L5 safety enforcement (policy outputs)
    • Return fully structured WorkflowOutput

NOT responsible for:
    • Prompt construction (Phase 2 → prompt_builder)
    • Prompt registry / ACLs (prompt_system_v10_10)
    • Agent-level LLM logic (cognitive_agents)
    • Detailed Retrieval/RAG logic (retrieval.py / ranking.py)

This file is the "public API" of the runtime. Everything outside should
import and call run_workflow() only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

from models import (
    JobInput,
    ResumeInput,
    WorkflowConfig,
    WorkflowPlanBundle,
    WorkflowOutput,
    ExecutionContext,
)

from l1 import plan_workflow
from l2 import execute_workflow_plans
from l3 import orchestrate_execution
from l4 import write_state
from l5 import enforce_safety

from routing import RoutingPolicy
from runtime_utils import SandboxConfig
from meta_profile import MetaProfileSnapshot
from observability import start_span, end_span, record_exception, emit_cost_snapshot
from config_profiles_v10_10 import EXECUTION_PROFILES


# =============================================================================
# High-level Orchestration
# =============================================================================


def _build_context(
    *,
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    profile_id: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> ExecutionContext:
    """
    Construct the ExecutionContext, the unified "environment"
    container passed across layers.

    Context contains:
        • job, resume, config
        • routing policy (model selection)
        • sandbox config
        • execution profile (model tier, safety tier)
        • meta-profile (behavioral nudge signals)
    """

    profile = (
        EXECUTION_PROFILES[profile_id]
        if profile_id and profile_id in EXECUTION_PROFILES
        else EXECUTION_PROFILES["default"]
    )

    routing_policy = RoutingPolicy(model_tier=profile.model_tier)
    sandbox = SandboxConfig(enable_network=False, strict_sandbox=True)
    meta_snapshot = MetaProfileSnapshot.from_dict(meta or {})

    return ExecutionContext(
        job=job,
        resume=resume,
        config=config,
        routing_policy=routing_policy,
        sandbox_config=sandbox,
        prompt_registry=None,
        cache_manager=None,
        meta_profile_snapshot=meta_snapshot,
    )


# =============================================================================
# Full Workflow Entrypoint
# =============================================================================


def run_workflow(
    *,
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    profile_id: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> WorkflowOutput:
    """
    Execute the full multi-layer workflow.

    This is the ONLY public API entrypoint for the runtime.
    External callers (API server, batch runner, notebook) must use this.

    Pipeline:
        L1 → L2 → L3 → L4 → L5
    """

    span = start_span("workflow.run", {"profile_id": profile_id})

    try:
        # ------------------------------------------------------------------
        # Build execution context
        # ------------------------------------------------------------------
        ctx = _build_context(
            job=job,
            resume=resume,
            config=config,
            profile_id=profile_id,
            meta=meta,
        )

        # ------------------------------------------------------------------
        # L1: Planning (pure, no LLM)
        # ------------------------------------------------------------------
        plan_span = start_span("workflow.l1.plan", {})
        try:
            plan_bundle: WorkflowPlanBundle = plan_workflow(job, resume, config, ctx)
        finally:
            end_span(plan_span)

        # ------------------------------------------------------------------
        # L2: Execution (LLMs + retrievers)
        # ------------------------------------------------------------------
        l2_span = start_span("workflow.l2.execute", {})
        try:
            l2_results = execute_workflow_plans(plan_bundle, ctx)
        finally:
            end_span(l2_span)

        # ------------------------------------------------------------------
        # L3: Orchestration (flow-level consistency)
        #      - May apply retries, repair logic, cross-agent arbitration
        # ------------------------------------------------------------------
        l3_span = start_span("workflow.l3.orchestrate", {})
        try:
            l3_results = orchestrate_execution(l2_results, plan_bundle, ctx)
        finally:
            end_span(l3_span)

        # ------------------------------------------------------------------
        # L4: State mutation (allowed surface only)
        #      - Saves intermediate artifacts into context state adapter
        # ------------------------------------------------------------------
        l4_span = start_span("workflow.l4.write_state", {})
        try:
            write_state(l3_results, plan_bundle, ctx)
        finally:
            end_span(l4_span)

        # ------------------------------------------------------------------
        # L5: Safety enforcement (final policy pass)
        # ------------------------------------------------------------------
        l5_span = start_span("workflow.l5.enforce_safety", {})
        try:
            final_output: WorkflowOutput = enforce_safety(l3_results, plan_bundle, ctx)
        finally:
            end_span(l5_span)

        emit_cost_snapshot(ctx.model_usage_snapshot())

        return final_output

    except Exception as exc:
        record_exception("workflow.run.error", exc)
        raise

    finally:
        end_span(span)


# =============================================================================
# CLI / Script Utility Entrypoint
# =============================================================================


def main():
    """
    Simple CLI stub for running the workflow via Python.

    This is intentionally minimal; the real ingestion (JSON, API, CLI)
    would wrap `run_workflow`.
    """
    print("This module is not intended to be executed directly.")
    print("Use run_workflow() as the public API.")


if __name__ == "__main__":
    main()
