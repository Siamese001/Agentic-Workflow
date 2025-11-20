# FILE: 10_10/l3.py
"""
L3 Orchestration Layer (v10_10 · Phase 3)
=========================================

Responsibilities (strict L3-only):
    • DAG orchestration and scheduling.
    • Parallelization of retrieval nodes.
    • Fallback graph edges for retrieval failures.
    • Concurrency control and ordering.
    • Fan-out/fan-in of L2 tasks.
    • Zero LLM execution.
    • Zero retrieval logic.
    • Zero safety/state mutation.

This module must NOT:
    • Call any LLM agents (L2 only).
    • Perform any retrieval (L2 only).
    • Mutate state (L4 only).
    • Enforce safety or policy (L5 only).

Phase-3 Changes:
    • Retrieval node is explicitly parallelizable.
    • Adds fallback paths:
          – If retrieval fails → continue workflow with empty RAGResult.
    • Ensures retrieval spans do not block Strategy execution.
    • Ensures DAG emits typed node events for observability.
"""

from __future__ import annotations

import asyncio
from typing import Optional

from models import (
    ExecutionContext,
    WorkflowPlanBundle,
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
    log_exception,
    emit_node_event,
)
from l2 import (
    _execute_strategy,
    _execute_retrieval,
    _execute_drafting,
    _execute_qa,
    _execute_safety,
)


# ============================================================================
# L3 NODE ENUMS
# ============================================================================

class Node:
    """Typed DAG nodes for observability + determinism."""
    STRATEGY = "strategy"
    RETRIEVAL = "retrieval"
    DRAFTING = "drafting"
    QA = "qa"
    SAFETY = "safety"


# ============================================================================
# INTERNAL HELPERS FOR NODE EXECUTION
# ============================================================================

async def _run_node(name: str, ctx: ExecutionContext, fn, *args, **kwargs):
    """
    Wraps each L3 node execution in:
        • span(name)
        • node-level telemetry events
        • error capture (no throws to DAG)
    """
    span = start_span(f"l3.{name}", ctx=ctx.span_context())
    emit_node_event(node=name, status="start")

    try:
        result = await fn(*args, **kwargs)
        emit_node_event(node=name, status="success")
        return result
    except Exception as exc:
        log_exception(f"l3.{name}_error", exc)
        emit_node_event(node=name, status="error", details=str(exc))
        return None
    finally:
        end_span(span)


# ============================================================================
# L3 ORCHESTRATION GRAPH (Phase 3)
# ============================================================================

async def run_l3(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    PHASE-3 DAG:

        ┌────────────────────┐
        │    Strategy Node    │  <-- independent
        └─────────┬──────────┘
                  │
                  │ (parallel)
                  │
        ┌─────────▼──────────┐
        │   Retrieval Node    │  <-- independent
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │  Drafting Node      │  <-- fan-in: needs Strategy + RAG
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │     QA Node         │
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │    Safety Node      │
        └─────────────────────┘

    **Retrieval fallback rule:**
        - If retrieval fails, L3 MUST continue execution with:
              RAGResult(evidence=[], used_hyde=False)

    **Concurrency requirements:**
        - Strategy and Retrieval must run concurrently.
        - Following nodes run sequentially.

    **L3 never executes LLM or retrieval directly — only orchestrates L2 nodes.**
    """
    span = start_span("l3.run", ctx=ctx.span_context())
    try:
        # ---------------------------------------------------------------
        # 1. PARALLEL NODES: Strategy + Retrieval
        # ---------------------------------------------------------------

        strategy_task = asyncio.create_task(
            _run_node(Node.STRATEGY, ctx, _execute_strategy, plans, ctx)
        )
        retrieval_task = asyncio.create_task(
            _run_node(Node.RETRIEVAL, ctx, _execute_retrieval, plans, ctx)
        )

        strategy_result: Optional[StrategyResult]
        rag_result: Optional[RAGResult]
        strategy_result, rag_result = await asyncio.gather(strategy_task, retrieval_task)

        # Fallback if retrieval failed
        if rag_result is None:
            rag_result = RAGResult(evidence=[], used_hyde=False)

        # ---------------------------------------------------------------
        # 2. DRAFTING NODE (fan-in)
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
        # 3. QA NODE
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
        # 4. SAFETY NODE
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
        # RETURN CONSOLIDATED L2 RESULTS (L3 never mutates)
        # ---------------------------------------------------------------
        return L2ResultBundle(
            strategy=strategy_result,
            rag=rag_result,
            drafting=drafting_result,
            qa=qa_result,
            safety=safety_result,
        )

    except Exception as exc:
        log_exception("l3.run_fatal", exc)
        # L3 must NEVER crash the agent; return minimal bundle.
        empty = L2ResultBundle.empty_with_error(str(exc))
        return empty
    finally:
        end_span(span)

