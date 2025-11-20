# FILE: 10_10/l2.py
"""
Unified L2 Execution Layer (v10_10 · Phase 2)
=============================================

Responsibilities:
    • Execute StrategyPlan, RAGPlan, DraftingPlan, QAPlan, SafetyPlan.
    • Perform all LLM calls (via cognitive_agents), plus retrieval hooks.
    • Produce structured outputs:
          – StrategyResult
          – RAGResult
          – DraftingResult
          – QAResult
          – SafetyResult
    • Wrap all computation in deterministic observability spans.
    • NO state mutation (L4 only).

Layering rules:
    • L2 is the ONLY layer allowed to:
          – call LLMs (through cognitive_agents)
          – perform retrieval / ranking (once wired)
    • L1 performs only planning.
    • L3 orchestrates control flow and retries.
    • L4 performs state mutation.
    • L5 performs safety enforcement and policy decisions.
"""

from __future__ import annotations

import asyncio
from typing import Any

from models import (
    ExecutionContext,
    WorkflowPlanBundle,
    StrategyResult,
    StrategyBranch,
    RAGResult,
    DraftingResult,
    QAResult,
    QACheckResult,
    SafetyResult,
    SafetyFinding,
    L2ResultBundle,
)
from observability import start_span, end_span, log_exception, emit_cost_snapshot
from cognitive_agents import (
    StrategyLLMAgent,
    DraftingGuild,
    SemanticQAAgent,
    ConstitutionalSafetyAgent,
)


# =============================================================================
# Strategy Execution
# =============================================================================


async def _execute_strategy(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> StrategyResult:
    """
    Run the strategy agent with the StrategyPlan using the Phase-2
    cognitive agent + prompt builder layer.
    """
    span = start_span("l2.strategy", ctx=ctx.span_context())
    try:
        agent = StrategyLLMAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )
        # Strategy agent returns a StrategyResult directly.
        result = agent.run_strategy(plans.strategy, ctx)
        return result
    except Exception as exc:
        log_exception("l2.strategy_error", exc)
        # Fallback: synthesize a minimal StrategyResult encoding the error.
        return StrategyResult(
            branches=[StrategyBranch(id="error", text=str(exc))],
            chosen_branch_id="error",
        )
    finally:
        end_span(span)


# =============================================================================
# Retrieval Execution (stub for Phase 2)
# =============================================================================


async def _execute_retrieval(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> RAGResult:
    """
    Phase-2 RAG execution stub.

    The full hybrid dense/BM25 retrieval + ranking stack lives in
    retrieval.py / ranking.py and will be fully re-wired in a later
    phase. For now, we return an empty RAGResult so that the rest of
    the pipeline (drafting, QA, safety) can execute deterministically
    with job/resume-only context.
    """
    span = start_span("l2.retrieval", ctx=ctx.span_context())
    try:
        # Placeholder: no evidence available yet.
        return RAGResult(evidence=[], used_hyde=False)
    except Exception as exc:
        log_exception("l2.retrieval_error", exc)
        return RAGResult(evidence=[], used_hyde=False)
    finally:
        end_span(span)


# =============================================================================
# Drafting Execution
# =============================================================================


async def _execute_drafting(
    plans: WorkflowPlanBundle,
    strategy_result: StrategyResult,
    rag_result: RAGResult,
    ctx: ExecutionContext,
) -> DraftingResult:
    """
    Run the drafting agent with:
        - DraftingPlan
        - StrategyResult
        - RAGResult (evidence, if any)
    """
    span = start_span("l2.drafting", ctx=ctx.span_context())
    try:
        agent = DraftingGuild(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )

        result = agent.run_drafting(
            drafting_plan=plans.drafting,
            job=ctx.job,
            resume=ctx.resume,
            strategy_result=strategy_result,
            rag_result=rag_result,
            config=ctx.config,
        )
        return result
    except Exception as exc:
        log_exception("l2.drafting_error", exc)
        # Fallback: empty DraftingResult in the configured mode.
        return DraftingResult(sections=[], mode=plans.drafting.mode)
    finally:
        end_span(span)


# =============================================================================
# QA Execution
# =============================================================================


async def _execute_qa(
    plans: WorkflowPlanBundle,
    drafting_result: DraftingResult,
    rag_result: RAGResult,
    ctx: ExecutionContext,
) -> QAResult:
    """
    QAAgent performs:
        - keyword coverage
        - job/resume alignment
        - hallucination checks
        - tone consistency
    """
    span = start_span("l2.qa", ctx=ctx.span_context())
    try:
        agent = SemanticQAAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )

        result = agent.run_qa(
            qa_plan=plans.qa,
            draft=drafting_result,
            rag=rag_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        return result
    except Exception as exc:
        log_exception("l2.qa_error", exc)
        # Fallback: single internal-error QA finding.
        return QAResult(
            findings=[
                QACheckResult(
                    check_id="qa_internal_error",
                    status="error",
                    message=str(exc),
                    details={},
                )
            ],
            summary="QA agent failed with an internal error.",
        )
    finally:
        end_span(span)


# =============================================================================
# Safety Execution (L2 pre-pass only)
# =============================================================================


async def _execute_safety(
    plans: WorkflowPlanBundle,
    drafting_result: DraftingResult,
    qa_result: QAResult,
    ctx: ExecutionContext,
) -> SafetyResult:
    """
    L2 performs a *pre-safety* analysis only.
    Full enforcement is performed in L5.

    The safety agent computes:
        - PII signal list
        - toxicity detection
        - high-risk phrasing
    """
    span = start_span("l2.safety", ctx=ctx.span_context())
    try:
        agent = ConstitutionalSafetyAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )

        result = agent.run_safety(
            safety_plan=plans.safety,
            draft=drafting_result,
            qa=qa_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        return result
    except Exception as exc:
        log_exception("l2.safety_error", exc)
        # Fallback: single blocked finding.
        return SafetyResult(
            findings=[
                SafetyFinding(
                    check_id="safety_internal_error",
                    category="internal",
                    status="blocked",
                    message=str(exc),
                    details={},
                )
            ],
            overall_status="blocked",
        )
    finally:
        end_span(span)


# =============================================================================
# Main L2 Execution
# =============================================================================


async def _run_l2_async(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    Full async L2 execution pipeline.

    Strategy and RAG are launched together; drafting, QA and safety
    then run sequentially using their results.
    """
    # Strategy → RAG can be independent
    strategy_task = asyncio.create_task(_execute_strategy(plans, ctx))
    rag_task = asyncio.create_task(_execute_retrieval(plans, ctx))

    # Wait for Strategy + RAG to complete before drafting
    strategy_result, rag_result = await asyncio.gather(strategy_task, rag_task)

    drafting_result = await _execute_drafting(plans, strategy_result, rag_result, ctx)
    qa_result = await _execute_qa(plans, drafting_result, rag_result, ctx)
    safety_result = await _execute_safety(plans, drafting_result, qa_result, ctx)

    return L2ResultBundle(
        strategy=strategy_result,
        rag=rag_result,
        drafting=drafting_result,
        qa=qa_result,
        safety=safety_result,
    )


# =============================================================================
# Public Entrypoint for L3
# =============================================================================


def execute_workflow_plans(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    Synchronous wrapper for L3.

    L3 is allowed to call *only this* L2 entrypoint.
    """
    span = start_span("l2.execute_workflow_plans", ctx=ctx.span_context())
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_run_l2_async(plans, ctx))
        emit_cost_snapshot(ctx.model_usage_snapshot())
        return result
    except Exception as exc:
        log_exception("l2.execute_error", exc)
        raise
    finally:
        end_span(span)
