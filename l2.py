# FILE: 10_10/l2.py
"""
Unified L2 Execution Layer (v10_10 · Phase 1)
=============================================

Responsibilities:
    • Execute StrategyPlan, RAGPlan, DraftingPlan, QAPlan, SafetyPlan.
    • Perform all LLM calls, tool calls, retrieval, ranking, evidence fusion.
    • Produce structured outputs:
          – StrategyResult
          – RAGResult
          – DraftingResult
          – QAResult
          – SafetyResult
    • Wrap all computation in deterministic observability spans.
    • NO state mutation (L4 only).
    • NO planning (L1).
    • NO DAG or retries (L3).
    • NO safety policy enforcement (L5).

Restores the full v10_8 / v10_9 functionality:
    • Async execution model
    • Hybrid dense + BM25 retrieval
    • RRF reciprocal rank fusion
    • Evidence fusion pipeline
    • Cognitive agent calls through cognitive_agents.py
    • Typed LLM/tool abstraction via registry.py
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Tuple

from models import (
    ExecutionContext,
    WorkflowPlanBundle,
    StrategyResult,
    RAGResult,
    DraftingResult,
    QAResult,
    SafetyResult,
    L2ResultBundle,
)
from observability import start_span, end_span, log_exception, emit_cost_snapshot
from registry import (
    get_llm_client,
    get_retriever,
    get_ranker,
    get_prompt,
    get_tool,
)
from cognitive_agents import (
    run_strategy_agent,
    run_drafting_agent,
    run_qa_agent,
    run_safety_agent,
)
from retrieval import (
    perform_dense_retrieval,
    perform_bm25_retrieval,
)
from ranking import (
    reciprocal_rank_fusion,
    hybrid_weighted_ranking,
    fuse_evidence,
)


# =============================================================================
# Strategy Execution
# =============================================================================

async def _execute_strategy(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> StrategyResult:
    """
    Run the strategy agent with the StrategyPlan.
    """
    span = start_span("l2.strategy", ctx=ctx.span_context())
    try:
        strategy_output = await run_strategy_agent(
            steps=plans.strategy.steps,
            complexity=plans.strategy.complexity,
            ctx=ctx,
        )
        return StrategyResult(
            steps=plans.strategy.steps,
            output=strategy_output,
        )
    except Exception as exc:
        log_exception("l2.strategy_error", exc)
        return StrategyResult(
            steps=plans.strategy.steps,
            output={"error": str(exc)},
        )
    finally:
        end_span(span)


# =============================================================================
# Retrieval Execution
# =============================================================================

async def _execute_retrieval(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> RAGResult:
    """
    Implements hybrid dense + BM25 retrieval, RRF fusion, and evidence merging.
    """
    span = start_span("l2.retrieval", ctx=ctx.span_context())

    try:
        rag_plan = plans.rag
        dense_results = []
        bm25_results = []

        # Run retrieval for each hint
        for hint in rag_plan.hints:
            if hint.focus in ("job", "resume", "hybrid"):
                # Dense retrieval
                dr = await perform_dense_retrieval(
                    focus=hint.focus,
                    max_chunks=hint.max_chunks,
                    ctx=ctx,
                )
                dense_results.append((hint, dr))

                # BM25 retrieval
                br = await perform_bm25_retrieval(
                    focus=hint.focus,
                    max_chunks=hint.max_chunks,
                    ctx=ctx,
                )
                bm25_results.append((hint, br))

        # RRF fusion
        rrf_fused = reciprocal_rank_fusion(
            dense_results=[dr for (_, dr) in dense_results],
            bm25_results=[br for (_, br) in bm25_results],
        )

        # Hybrid weighting
        hybrid_ranked = hybrid_weighted_ranking(
            fused_results=rrf_fused,
            hints=rag_plan.hints,
        )

        # Evidence fusion
        fused_evidence = fuse_evidence(hybrid_ranked)

        return RAGResult(
            raw_results={
                "dense": dense_results,
                "bm25": bm25_results,
            },
            ranked_results=hybrid_ranked,
            fused_evidence=fused_evidence,
        )

    except Exception as exc:
        log_exception("l2.retrieval_error", exc)
        return RAGResult(
            raw_results={},
            ranked_results=[],
            fused_evidence=[],
        )
    finally:
        end_span(span)


# =============================================================================
# Drafting Execution
# =============================================================================

async def _execute_drafting(
    plans: WorkflowPlanBundle,
    rag_result: RAGResult,
    ctx: ExecutionContext,
) -> DraftingResult:
    """
    Run the drafting agent with:
        - DraftingPlan
        - RAG fused evidence
    """
    span = start_span("l2.drafting", ctx=ctx.span_context())
    try:
        drafting_plan = plans.drafting

        drafting_output = await run_drafting_agent(
            sections=drafting_plan.sections,
            mode=drafting_plan.mode,
            fused_evidence=rag_result.fused_evidence,
            ctx=ctx,
            target_tone=drafting_plan.target_tone,
        )

        return DraftingResult(
            sections=drafting_plan.sections,
            mode=drafting_plan.mode,
            output=drafting_output,
        )

    except Exception as exc:
        log_exception("l2.drafting_error", exc)
        return DraftingResult(
            sections=plans.drafting.sections,
            mode=plans.drafting.mode,
            output={"error": str(exc)},
        )
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
        qa_output = await run_qa_agent(
            checks=plans.qa.checks,
            drafting_output=drafting_result.output,
            fused_evidence=rag_result.fused_evidence,
            ctx=ctx,
        )

        return QAResult(
            checks=plans.qa.checks,
            findings=qa_output,
        )
    except Exception as exc:
        log_exception("l2.qa_error", exc)
        return QAResult(
            checks=plans.qa.checks,
            findings=[{"error": str(exc)}],
        )
    finally:
        end_span(span)


# =============================================================================
# Safety Execution (L2 pre-pass only)
# =============================================================================

async def _execute_safety(
    plans: WorkflowPlanBundle,
    drafting_result: DraftingResult,
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
        safety_output = await run_safety_agent(
            checks=plans.safety.checks,
            content=drafting_result.output,
            ctx=ctx,
        )

        return SafetyResult(
            checks=plans.safety.checks,
            findings=safety_output,
        )

    except Exception as exc:
        log_exception("l2.safety_error", exc)
        return SafetyResult(
            checks=plans.safety.checks,
            findings=[{"error": str(exc)}],
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
    """

    # Strategy → RAG can be independent
    strategy_task = asyncio.create_task(_execute_strategy(plans, ctx))
    rag_task = asyncio.create_task(_execute_retrieval(plans, ctx))

    # Wait for RAG to complete before drafting
    strategy_result, rag_result = await asyncio.gather(strategy_task, rag_task)

    drafting_result = await _execute_drafting(plans, rag_result, ctx)
    qa_result = await _execute_qa(plans, drafting_result, rag_result, ctx)
    safety_result = await _execute_safety(plans, drafting_result, ctx)

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
