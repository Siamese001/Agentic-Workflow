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
    • Call any LLM client.
    • Perform retrieval, ranking, or RAG reasoning.
    • Apply state patches or enforce safety.

L3 delegates:
    • L2 cognitive agents via l2.py
    • Correction loops and DAG wiring via workflow_graph.py
"""

from __future__ import annotations

import asyncio

from models import (
    WorkflowPlanBundle,
    ExecutionContext,
    L2ResultBundle,
    RAGResult,
    DraftingResult,
    QAResult,
    SafetyResult,
)
from observability import (
    start_span,
    end_span,
    emit_node_event,
    log_exception,
)
from l2 import (
    _execute_strategy,
    _execute_retrieval,
    _execute_drafting,
    _execute_qa,
    _execute_safety,
)


class Node:
    """Typed DAG nodes for observability + determinism."""
    STRATEGY = "strategy"
    RETRIEVAL = "retrieval"
    DRAFTING = "drafting"
    QA = "qa"
    SAFETY = "safety"


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
    except Exception as exc:  # noqa: BLE001
        log_exception(f"l3.{name}.error", exc)
        emit_node_event(node=name, status="error", details=str(exc))
        return None
    finally:
        end_span(span)


async def run_l3_workflow(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    Execute the core workflow graph at L3 using L2 nodes.
    """
    span = start_span("l3.run", ctx=ctx.span_context())
    try:
        strategy_task = asyncio.create_task(
            _run_node(Node.STRATEGY, ctx, _execute_strategy, plans, ctx)
        )
        retrieval_task = asyncio.create_task(
            _run_node(Node.RETRIEVAL, ctx, _execute_retrieval, plans, ctx)
        )

        strategy_result = await strategy_task
        rag_result = await retrieval_task

        if rag_result is None:
            rag_result = RAGResult(evidence=[], used_hyde=False)

        drafting_result: DraftingResult = await _run_node(
            Node.DRAFTING, ctx, _execute_drafting, plans, strategy_result, rag_result, ctx
        )
        if drafting_result is None:
            drafting_result = DraftingResult(sections=[])

        qa_result: QAResult = await _run_node(
            Node.QA, ctx, _execute_qa, plans, drafting_result, rag_result, ctx
        )
        if qa_result is None:
            qa_result = QAResult(findings=[])

        safety_result: SafetyResult = await _run_node(
            Node.SAFETY, ctx, _execute_safety, plans, drafting_result, qa_result, ctx
        )
        if safety_result is None:
            safety_result = SafetyResult(findings=[])

        return L2ResultBundle(
            strategy=strategy_result,
            rag=rag_result,
            drafting=drafting_result,
            qa=qa_result,
            safety=safety_result,
        )

    except Exception as exc:  # noqa: BLE001
        log_exception("l3.run_fatal", exc)
        empty = L2ResultBundle.empty_with_error(str(exc))
        return empty
    finally:
        end_span(span)
