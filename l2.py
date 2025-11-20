# FILE: 10_10/l2.py
"""
Unified L2 Execution Layer (v10_10)
===================================

Responsibilities:
    • Execute L1 plans (Strategy, RAG, Drafting, QA, Safety).
    • Delegate ALL cognition to cognitive_agents (LLM-based).
    • Perform deterministic RAG and ranking.
    • Integrate predictive caching & sandbox configuration.
    • Return fully typed L2ResultBundle to L3.

Non-responsibilities:
    • No planning (L1).
    • No orchestration or retries (L3).
    • No state mutation (L4).
    • No safety gating (L5).

This file is PURE EXECUTION for a single workflow pass.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models import (
    WorkflowPlanBundle,
    L2ResultBundle,
    ExecutionContext,
    StrategyResult,
    RAGResult,
    DraftingResult,
    QAResult,
    SafetyResult,
)
from runtime_utils import (
    PredictiveCacheManager,
    get_sandbox,
    SandboxConfig,
)
from retrieval import run_rag_retrieval
from ranking import rank_evidence
from observability import start_span, end_span, record_event, record_exception
from cognitive_agents import (
    StrategyLLMAgent,
    DraftingGuild,
    SemanticQAAgent,
    ConstitutionalSafetyAgent,
)


# =============================================================================
# Execution Environment (DI container for L2)
# =============================================================================

@dataclass
class L2Environment:
    """
    Execution wiring for L2.

    DI components:
        - cache_manager
        - sandbox
        - cognitive agents (Strategy, Drafting, QA, Safety)
    """

    cache_manager: Optional[PredictiveCacheManager]
    sandbox: SandboxConfig

    strategy_agent: StrategyLLMAgent
    drafting_agent: DraftingGuild
    qa_agent: SemanticQAAgent
    safety_agent: ConstitutionalSafetyAgent


def build_l2_environment(ctx: ExecutionContext) -> L2Environment:
    """
    Build the dependency-injected environment for L2 from ExecutionContext.
    """
    sandbox = get_sandbox(ctx.sandbox_config)

    strat = StrategyLLMAgent(
        routing_policy=ctx.routing_policy,
        meta_profile=ctx.meta_profile_snapshot,
        prompt_registry=ctx.prompt_registry,
        sandbox=sandbox,
    )

    draft = DraftingGuild(
        routing_policy=ctx.routing_policy,
        meta_profile=ctx.meta_profile_snapshot,
        prompt_registry=ctx.prompt_registry,
        sandbox=sandbox,
    )

    qa = SemanticQAAgent(
        routing_policy=ctx.routing_policy,
        meta_profile=ctx.meta_profile_snapshot,
        prompt_registry=ctx.prompt_registry,
        sandbox=sandbox,
    )

    safety = ConstitutionalSafetyAgent(
        routing_policy=ctx.routing_policy,
        meta_profile=ctx.meta_profile_snapshot,
        prompt_registry=ctx.prompt_registry,
        sandbox=sandbox,
    )

    return L2Environment(
        cache_manager=ctx.cache_manager,
        sandbox=sandbox,
        strategy_agent=strat,
        drafting_agent=draft,
        qa_agent=qa,
        safety_agent=safety,
    )


# =============================================================================
# STRATEGY EXECUTION
# =============================================================================

def execute_strategy(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
    env: L2Environment,
) -> StrategyResult:
    span = start_span("l2.execute_strategy", ctx=ctx.span_context())
    try:
        result = env.strategy_agent.run_strategy(plans.strategy, ctx)
        record_event(
            "l2.strategy_completed",
            {
                "num_branches": len(result.branches),
                "chosen_branch": result.chosen_branch_id,
            },
        )
        return result
    except Exception as exc:
        record_exception("l2.strategy_error", exc)
        raise
    finally:
        end_span(span)


# =============================================================================
# RAG EXECUTION (Deterministic)
# =============================================================================

def execute_rag(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
    env: L2Environment,
    strategy_result: StrategyResult,
) -> RAGResult:
    span = start_span("l2.execute_rag", ctx=ctx.span_context())
    try:
        cache_key = None
        if env.cache_manager:
            cache_key = env.cache_manager.make_key("rag", plans.rag, ctx)
            cached = env.cache_manager.get(cache_key)
            if cached is not None:
                record_event("l2.rag_cache_hit", {"key": cache_key})
                return cached

        # Deterministic retrieval
        raw_hits = run_rag_retrieval(
            rag_plan=plans.rag,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
            strategy_hint=strategy_result,
            sandbox=env.sandbox,
        )

        ranked = rank_evidence(raw_hits, plans.rag, ctx)
        rag_result = RAGResult(evidence=ranked, used_hyde=plans.rag.allow_hyde)

        if env.cache_manager and cache_key:
            env.cache_manager.set(cache_key, rag_result)

        record_event("l2.rag_completed", {"num_evidence": len(ranked)})
        return rag_result
    except Exception as exc:
        record_exception("l2.rag_error", exc)
        raise
    finally:
        end_span(span)


# =============================================================================
# DRAFTING EXECUTION
# =============================================================================

def execute_drafting(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
    env: L2Environment,
    strategy_result: StrategyResult,
    rag_result: RAGResult,
) -> DraftingResult:
    span = start_span("l2.execute_drafting", ctx=ctx.span_context())
    try:
        result = env.drafting_agent.run_drafting(
            drafting_plan=plans.drafting,
            job=ctx.job,
            resume=ctx.resume,
            strategy_result=strategy_result,
            rag_result=rag_result,
            config=ctx.config,
        )
        record_event(
            "l2.drafting_completed",
            {"num_sections": len(result.sections)},
        )
        return result
    except Exception as exc:
        record_exception("l2.drafting_error", exc)
        raise
    finally:
        end_span(span)


# =============================================================================
# QA EXECUTION
# =============================================================================

def execute_qa(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
    env: L2Environment,
    drafting_result: DraftingResult,
    rag_result: RAGResult,
) -> QAResult:
    span = start_span("l2.execute_qa", ctx=ctx.span_context())
    try:
        result = env.qa_agent.run_qa(
            qa_plan=plans.qa,
            draft=drafting_result,
            rag=rag_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        record_event(
            "l2.qa_completed",
            {"num_failed": sum(1 for c in result.checks if not c.passed)},
        )
        return result
    except Exception as exc:
        record_exception("l2.qa_error", exc)
        raise
    finally:
        end_span(span)


# =============================================================================
# SAFETY EXECUTION
# =============================================================================

def execute_safety(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
    env: L2Environment,
    drafting_result: DraftingResult,
    qa_result: QAResult,
) -> SafetyResult:
    span = start_span("l2.execute_safety", ctx=ctx.span_context())
    try:
        result = env.safety_agent.run_safety(
            safety_plan=plans.safety,
            draft=drafting_result,
            qa_result=qa_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        record_event(
            "l2.safety_completed",
            {
                "num_findings": len(result.findings),
                "num_blocking": sum(1 for f in result.findings if f.blocking),
            },
        )
        return result
    except Exception as exc:
        record_exception("l2.safety_error", exc)
        raise
    finally:
        end_span(span)


# =============================================================================
# L2 ENTRYPOINT
# =============================================================================

def execute_workflow_plans(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
    env: Optional[L2Environment] = None,
) -> L2ResultBundle:
    """
    The single entrypoint for L2 execution.

    L3 calls this once per DAG iteration.
    """
    if env is None:
        env = build_l2_environment(ctx)

    span = start_span("l2.execute_workflow_plans", ctx=ctx.span_context())
    try:
        strategy_res = execute_strategy(plans, ctx, env)
        rag_res = execute_rag(plans, ctx, env, strategy_res)
        drafting_res = execute_drafting(plans, ctx, env, strategy_res, rag_res)
        qa_res = execute_qa(plans, ctx, env, drafting_res, rag_res)
        safety_res = execute_safety(plans, ctx, env, drafting_res, qa_res)

        return L2ResultBundle(
            strategy=strategy_res,
            rag=rag_res,
            drafting=drafting_res,
            qa=qa_res,
            safety=safety_res,
        )
    except Exception as exc:
        record_exception("l2.workflow_error", exc)
        raise
    finally:
        end_span(span)

