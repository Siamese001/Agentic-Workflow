# FILE: workflow_graph.py
# PHASE 3 — FULL ORCHESTRATION GRAPH RESTORE
#
# Strict L3 orchestration only:
#   • No LLM calls
#   • No retrieval logic
#   • No ranking logic
#   • No prompting
#   • No state mutation
#   • No safety evaluation
#
# Responsibilities:
#   • DAG construction
#   • Concurrency rules
#   • Typed node definitions
#   • Retrieval parallelization
#   • Retrieval fallback edges
#   • Checkpoint + span boundaries
#   • Orchestration-only failure-tolerance
#
# Inputs/Outputs:
#   • Input: WorkflowPlanBundle, ExecutionContext
#   • Output: L2ResultBundle (produced by invoking L2 nodes)
#
# Implements DAG for:
#   Strategy  ┐
#             ├── parallel
#   Retrieval ┘
#        ↓ (fan-in)
#   Drafting → QA → Safety
#
# No business logic lives here. Pure scheduling.

from __future__ import annotations

import asyncio
from typing import Optional, Callable, Dict

from models import (
    WorkflowPlanBundle,
    ExecutionContext,
    RAGResult,
    StrategyResult,
    DraftingResult,
    QAResult,
    SafetyResult,
    L2ResultBundle,
)
from observability import (
    start_span,
    end_span,
    emit_node_event,
    log_exception,
)

# L2 execution entrypoints (already Phase-3 compliant)
from l2 import (
    _execute_strategy,
    _execute_retrieval,
    _execute_drafting,
    _execute_qa,
    _execute_safety,
)


# ============================================================================
#  WORKFLOW NODE ENUMERATION
# ============================================================================

class Node:
    STRATEGY = "strategy"
    RETRIEVAL = "retrieval"
    DRAFTING = "drafting"
    QA = "qa"
    SAFETY = "safety"


# ============================================================================
#  TASK WRAPPER (Standardized execution wrapper for every DAG node)
# ============================================================================

async def _run_node(
    node_name: str,
    ctx: ExecutionContext,
    fn: Callable,
    *args,
    **kwargs,
):
    """
    Wraps each node call with:
        • deterministic spans
        • node lifecycle events
        • structured failure handling
        • typed node metadata

    Returns:
        - The result of fn() OR
        - None on failure (L3 never raises)
    """

    span = start_span(f"workflow.{node_name}", ctx=ctx.span_context())
    emit_node_event(node=node_name, status="start")

    try:
        result = await fn(*args, **kwargs)
        emit_node_event(node=node_name, status="success")
        return result

    except Exception as exc:
        log_exception(f"workflow.{node_name}.error", exc)
        emit_node_event(node=node_name, status="error", details=str(exc))
        return None

    finally:
        end_span(span)


# ============================================================================
#  WORKFLOW GRAPH EXECUTION (PHASE 3)
# ============================================================================

async def run_workflow_graph(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    Phase-3 canonical workflow graph:

          ┌───────────────┐
          │   STRATEGY    │
          └──────┬────────┘
                 │
                 │   (parallel)
                 │
          ┌──────▼────────┐
          │   RETRIEVAL   │
          └──────┬────────┘
                 │  (fan-in: waits for strategy + retrieval)
          ┌──────▼────────┐
          │   DRAFTING    │
          └──────┬────────┘
                 │
          ┌──────▼────────┐
          │      QA       │
          └──────┬────────┘
                 │
          ┌──────▼────────┐
          │    SAFETY     │
          └───────────────┘

    L3 responsibilities:
        • Schedule
        • Concurrency
        • Fallback from failures
        • Deterministic spans

    L3 does NOT:
        • run retrieval
        • run LLMs
        • run ranking
        • mutate state
        • enforce safety
        • build prompts
    """

    root_span = start_span("workflow.run", ctx=ctx.span_context())

    try:
        # ---------------------------------------------------------------
        # 1. PARALLEL EXECUTION: STRATEGY + RETRIEVAL
        # ---------------------------------------------------------------

        strategy_task = asyncio.create_task(
            _run_node(Node.STRATEGY, ctx, _execute_strategy, plans, ctx)
        )
        retrieval_task = asyncio.create_task(
            _run_node(Node.RETRIEVAL, ctx, _execute_retrieval, plans, ctx)
        )

        strategy_result: Optional[StrategyResult]
        rag_result: Optional[RAGResult]
        strategy_result, rag_result = await asyncio.gather(
            strategy_task, retrieval_task
        )

        # Retrieval fallback path
        if rag_result is None:
            rag_result = RAGResult(evidence=[], used_hyde=False)

        # Strategy fallback should *never* halt the pipeline
        if strategy_result is None:
            strategy_result = StrategyResult(
                branches=[],
                chosen_branch_id="error",
            )

        # ---------------------------------------------------------------
        # 2. DRAFTING (depends on Strategy + Retrieval)
        # ---------------------------------------------------------------
        drafting_result: Optional[DraftingResult] = await _run_node(
            Node.DRAFTING,
            ctx,
            _execute_drafting,
            plans,
            strategy_result,
            rag_result,
            ctx,
        )

        if drafting_result is None:
            drafting_result = DraftingResult(sections=[])

        # ---------------------------------------------------------------
        # 3. QA
        # ---------------------------------------------------------------
        qa_result: Optional[QAResult] = await _run_node(
            Node.QA,
            ctx,
            _execute_qa,
            plans,
            drafting_result,
            rag_result,
            ctx,
        )

        if qa_result is None:
            qa_result = QAResult(findings=[])

        # ---------------------------------------------------------------
        # 4. SAFETY
        # ---------------------------------------------------------------
        safety_result: Optional[SafetyResult] = await _run_node(
            Node.SAFETY,
            ctx,
            _execute_safety,
            plans,
            drafting_result,
            qa_result,
            ctx,
        )

        if safety_result is None:
            safety_result = SafetyResult(findings=[])

        # ---------------------------------------------------------------
        # Return results (L3 does not modify them)
        # ---------------------------------------------------------------
        return L2ResultBundle(
            strategy=strategy_result,
            rag=rag_result,
            drafting=drafting_result,
            qa=qa_result,
            safety=safety_result,
        )

    except Exception as exc:
        log_exception("workflow.run.fatal", exc)
        return L2ResultBundle.empty_with_error(str(exc))

    finally:
        end_span(root_span)
