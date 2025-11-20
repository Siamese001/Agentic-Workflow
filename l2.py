# FILE: 10_10/l2.py
"""
Unified L2 Execution Layer (v10_10)
===================================

Responsibilities:
    • Execute L1 plans using cognitive agents + deterministic modules.
    • Use StrategyLLMAgent, DraftingGuild, SemanticQAAgent,
      ConstitutionalSafetyAgent.
    • Run deterministic RAG pipeline.
    • Produce typed L2ResultBundle for L3.

Non-Responsibilities:
    • No planning (L1).
    • No orchestrating retries or DAG (L3).
    • No state mutation (L4).
    • No final gating (L5).

This file is purely a “single-pass executor”.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models import (
    WorkflowPlanBundle,
    ExecutionContext,
    StrategyResult,
    DraftingResult,
    RAGResult,
    QAResult,
    SafetyResult,
    L2ResultBundle,
)
from cognitive_agents import (
    StrategyLLMAgent,
    DraftingGuild,
    SemanticQAAgent,
    ConstitutionalSafetyAgent,
)
from runtime_utils import PredictiveCacheManager, SandboxConfig, get_sandbox
from retrieval import run_rag_retrieval
from ranking import rank_evidence
from observability import (
    start_span,
    end_span,
    record_event,
    record_exception,
)


# ==============================================================================
# L2 Environment (dependency injection)
# ==============================================================================

@dataclass
class L2Environment:
    cache: Optional[PredictiveCacheManager]
    sandbox: SandboxConfig
    agent_strategy: StrategyLLMAgent
    agent_drafting: DraftingGuild
    agent_qa: SemanticQAAgent
    agent_safety: ConstitutionalSafetyAgent


def build_l2_environment(ctx: ExecutionContext) -> L2Environment:
    """
    Construct cognitive agents + sandbox for this run.
    """
    sandbox = get_sandbox(ctx.sandbox_config)

    agent_strategy = StrategyLLMAgent(
        routing_policy=ctx.routing_policy,
        meta_profile=ctx.meta_profile_snapshot,
        prompt_registry=ctx.prompt_registry,
        sandbox=sandbox,
    )

    agent_drafting = DraftingGuild(
        routing_policy=ctx.routing_policy,
        meta_profile=ctx.meta_profile_snapshot,
        prompt_registry=ctx.prompt_registry,
        sandbox=sandbox,
    )

    agent_qa = SemanticQAAgent(
        routing_policy=ctx.routing_policy,
        meta_profile=ctx.meta_profile_snapshot,
        prompt_registry=ctx.prompt_registry,
        sandbox=sandbox,
    )

    agent_safety = ConstitutionalSafetyAgent(
        routing_policy=ctx.routing_policy,
        meta_profile=ctx.meta_profile_snapshot,
        prompt_registry=ctx.prompt_registry,
        sandbox=sandbox,
    )

    return L2Environment(
        cache=ctx.cache_manager,
        sandbox=sandbox,
        agent_strategy=agent_strategy,
        agent_drafting=agent_drafting,
        agent_qa=agent_qa,
        agent_safety=agent_safety,
    )


# ==============================================================================
# Strategy Execution
# ==============================================================================

def run_strategy(plans: WorkflowPlanBundle, ctx: ExecutionContext, env: L2Environment) -> StrategyResult:
    span = start_span("l2.strategy", ctx=ctx.span_context())
    try:
        result = env.agent_strategy.run_strategy(plans.strategy, ctx)
        record_event("strategy_done", {"chosen": result.chosen_branch_id})
        return result
    except Exception as exc:
        record_exception("l2_strategy_error", exc)
        raise
    finally:
        end_span(span)


# ==============================================================================
# Deterministic RAG
# ==============================================================================

def run_rag(plans: WorkflowPlanBundle, ctx: ExecutionContext, env: L2Environment, strategy_result: StrategyResult) -> RAGResult:
    span = start_span("l2.rag", ctx=ctx.span_context())
    try:
        cache_key = None
        if env.cache:
            cache_key = env.cache.make_key("rag", plans.rag, ctx)
            cached = env.cache.get(cache_key)
            if cached:
                record_event("rag_cache_hit", {"key": cache_key})
                return cached

        # Deterministic retrieval
        hits = run_rag_retrieval(
            rag_plan=plans.rag,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
            strategy_hint=strategy_result,
            sandbox=env.sandbox,
        )

        ranked = rank_evidence(hits, plans.rag, ctx)
        result = RAGResult(evidence=ranked, used_hyde=plans.rag.allow_hyde)

        if env.cache and cache_key:
            env.cache.set(cache_key, result)

        return result
    except Exception as exc:
        record_exception("l2_rag_error", exc)
        raise
    finally:
        end_span(span)


# ==============================================================================
# Drafting Execution
# ==============================================================================

def run_drafting(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
    env: L2Environment,
    strategy_result: StrategyResult,
    rag_result: RAGResult,
) -> DraftingResult:
    span = start_span("l2.drafting", ctx=ctx.span_context())
    try:
        result = env.agent_drafting.run_drafting(
            drafting_plan=plans.drafting,
            job=ctx.job,
            resume=ctx.resume,
            strategy_result=strategy_result,
            rag_result=rag_result,
            config=ctx.config,
        )
        record_event("drafting_done", {"num_sections": len(result.sections)})
        return result
    except Exception as exc:
        record_exception("l2_drafting_error", exc)
        raise
    finally:
        end_span(span)


# ==============================================================================
# QA Execution
# ==============================================================================

def run_qa(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
    env: L2Environment,
    draft_result: DraftingResult,
    rag_result: RAGResult,
) -> QAResult:
    span = start_span("l2.qa", ctx=ctx.span_context())
    try:
        result = env.agent_qa.run_qa(
            qa_plan=plans.qa,
            draft=draft_result,
            rag=rag_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        record_event("qa_done", {"failed": sum(1 for c in result.checks if not c.passed)})
        return result
    except Exception as exc:
        record_exception("l2_qa_error", exc)
        raise
    finally:
        end_span(span)


# ==============================================================================
# Safety Execution
# ==============================================================================

def run_safety(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
    env: L2Environment,
    draft_result: DraftingResult,
    qa_result: QAResult,
) -> SafetyResult:
    span = start_span("l2.safety", ctx=ctx.span_context())
    try:
        result = env.agent_safety.run_safety(
            safety_plan=plans.safety,
            draft=draft_result,
            qa_result=qa_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        record_event("safety_done", {"blocking": sum(1 for f in result.findings if f.blocking)})
        return result
    except Exception as exc:
        record_exception("l2_safety_error", exc)
        raise
    finally:
        end_span(span)


# ==============================================================================
# Top-Level L2 Executor
# ==============================================================================

def execute_workflow_plans(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
    env: Optional[L2Environment] = None,
) -> L2ResultBundle:
    """
    The SINGLE L2 entrypoint used by L3 orchestrator.

    Performs:
        1. Strategy (LLM)
        2. RAG (deterministic)
        3. Drafting (LLM)
        4. QA (LLM)
        5. Safety (LLM)

    No retries — L3 handles correction loops.
    """
    if env is None:
        env = build_l2_environment(ctx)

    span = start_span("l2.execute", ctx=ctx.span_context())

    try:
        strategy = run_strategy(plans, ctx, env)
        rag = run_rag(plans, ctx, env, strategy)
        draft = run_drafting(plans, ctx, env, strategy, rag)
        qa = run_qa(plans, ctx, env, draft, rag)
        safety = run_safety(plans, ctx, env, draft, qa)

        return L2ResultBundle(
            strategy=strategy,
            rag=rag,
            drafting=draft,
            qa=qa,
            safety=safety,
        )
    except Exception as exc:
        record_exception("l2_execute_error", exc)
        raise
    finally:
        end_span(span)

