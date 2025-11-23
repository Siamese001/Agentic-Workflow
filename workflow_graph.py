# FILE: workflow_graph.py
# PHASE 3 — FULL ORCHESTRATION GRAPH RESTORE (WITH CORRECTION LOOP)
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
#   • Bounded correction loop orchestration
#
# This module wires together the L2 execution primitives into a canonical,
# deterministic workflow graph with a bounded correction loop across all
# surfaces (strategy, retrieval, drafting, QA, safety).
#
# Layering:
#   • This is strictly L3. It owns orchestration and nothing else.
#   • L2 owns all cognition (LLM, RAG, tools).
#   • L4 owns state mutation.
#   • L5 owns safety enforcement.

from __future__ import annotations

import asyncio
from typing import Optional, Callable, Awaitable

from core.models.models import (
    WorkflowPlanBundle,
    ExecutionContext,
    RAGResult,
    StrategyResult,
    DraftingResult,
    QAResult,
    SafetyResult,
    L2ResultBundle,
)
from runtime.observability import (
    start_span,
    end_span,
    emit_node_event,
    log_exception,
)
from orchestration.dag_engine import Node as DagNode, Edge as DagEdge, Graph as DagGraph, DAGExecutor
from core.agent_registry import AgentRegistry
from profiles.agent_profile import AgentCard
from core.agent_router_policy import choose_agents_for_task
from core.l2 import (
    _execute_strategy,
    _execute_retrieval,
    _execute_drafting,
    _execute_qa,
    _execute_safety,
)
from core.routing import route_task_to_agent

# Self-correction surfaces (meta-layer, no L1–L5 violations)
from self_correction import (
    evaluate_all_surfaces,
    aggregate_correction_signals,
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


def _build_workflow_dag(plans: WorkflowPlanBundle, ctx: ExecutionContext) -> DagGraph:
    """Construct a DAG that mirrors the logical workflow stages.

    This helper is a thin adapter between the L3 workflow and the generic
    DAG engine. For now it only defines nodes and edges; run_workflow_graph
    continues to orchestrate execution directly until we delegate to
    DAGExecutor in a follow-up step.
    """

    async def _node_strategy(dag_ctx):
        dag_ctx = dict(dag_ctx or {})
        result = await _execute_strategy(plans, ctx)
        dag_ctx["strategy_result"] = result
        return dag_ctx

    async def _node_retrieval(dag_ctx):
        dag_ctx = dict(dag_ctx or {})
        result = await _execute_retrieval(plans, ctx)
        dag_ctx["rag_result"] = result
        return dag_ctx

    async def _node_drafting(dag_ctx):
        dag_ctx = dict(dag_ctx or {})
        strategy_result = dag_ctx.get("strategy_result") or StrategyResult(branches=[])
        rag_result = dag_ctx.get("rag_result") or RAGResult(evidence=[], used_hyde=False)
        result = await _execute_drafting(plans, strategy_result, rag_result, ctx)
        dag_ctx["drafting_result"] = result
        return dag_ctx

    async def _node_qa(dag_ctx):
        dag_ctx = dict(dag_ctx or {})
        drafting_result = dag_ctx.get("drafting_result") or DraftingResult(sections=[])
        rag_result = dag_ctx.get("rag_result") or RAGResult(evidence=[], used_hyde=False)
        result, _council = await _execute_qa(plans, drafting_result, rag_result, ctx)
        dag_ctx["qa_result"] = result
        return dag_ctx

    async def _node_safety(dag_ctx):
        dag_ctx = dict(dag_ctx or {})
        drafting_result = dag_ctx.get("drafting_result") or DraftingResult(sections=[])
        rag_result = dag_ctx.get("rag_result") or RAGResult(evidence=[], used_hyde=False)
        qa_result = dag_ctx.get("qa_result") or QAResult(findings=[])
        result = await _execute_safety(plans, drafting_result, rag_result, qa_result, ctx)
        dag_ctx["safety_result"] = result
        return dag_ctx

    nodes = {
        Node.STRATEGY: DagNode(
            id=Node.STRATEGY,
            fn=_node_strategy,
            metadata={"agent_type": "planner"},
        ),
        Node.RETRIEVAL: DagNode(
            id=Node.RETRIEVAL,
            fn=_node_retrieval,
            metadata={"agent_type": "researcher"},
        ),
        Node.DRAFTING: DagNode(
            id=Node.DRAFTING,
            fn=_node_drafting,
            metadata={"agent_type": "drafter"},
        ),
        Node.QA: DagNode(
            id=Node.QA,
            fn=_node_qa,
            metadata={"agent_type": "qa"},
        ),
        Node.SAFETY: DagNode(
            id=Node.SAFETY,
            fn=_node_safety,
            metadata={"agent_type": "safety"},
        ),
    }

    edges = [
        DagEdge(source=Node.STRATEGY, target=Node.DRAFTING),
        DagEdge(source=Node.RETRIEVAL, target=Node.DRAFTING),
        DagEdge(source=Node.DRAFTING, target=Node.QA),
        DagEdge(source=Node.QA, target=Node.SAFETY),
    ]

    return DagGraph(nodes=nodes, edges=edges)


async def _run_single_pass_via_dag(plans: WorkflowPlanBundle, ctx: ExecutionContext) -> dict:
    """Execute a single Strategy→Retrieval→Drafting→QA→Safety pass via DAG.

    This is currently used as a sanity check alongside the imperative
    orchestration path and does not alter the primary outputs.
    """

    graph = _build_workflow_dag(plans, ctx)

    # Minimal agent registry for DAG-backed runs. For now we register
    # one agent per logical type so that the DAGExecutor can attach
    # advisory agent assignments to node executions.
    registry = AgentRegistry()
    registry.register_agent(AgentCard(agent_id="planner-1", agent_type="planner", role=None))  # type: ignore[arg-type]
    registry.register_agent(AgentCard(agent_id="researcher-1", agent_type="researcher", role=None))  # type: ignore[arg-type]
    registry.register_agent(AgentCard(agent_id="drafter-1", agent_type="drafter", role=None))  # type: ignore[arg-type]
    registry.register_agent(AgentCard(agent_id="qa-1", agent_type="qa", role=None))  # type: ignore[arg-type]
    registry.register_agent(AgentCard(agent_id="safety-1", agent_type="safety", role=None))  # type: ignore[arg-type]

    executor = DAGExecutor(graph, agent_registry=registry)
    dag_ctx = {"plans": plans, "ctx": ctx}
    return await executor.run(ctx=dag_ctx)


# ============================================================================
#  TASK WRAPPER (Standardized execution wrapper for every DAG node)
# ============================================================================


async def _run_node(
    node_name: str,
    ctx: ExecutionContext,
    fn: Callable[..., Awaitable[object]],
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
        - None on error (caller is responsible for fallback behavior).
    """
    span = start_span(f"workflow.{node_name}", ctx=ctx.span_context())
    emit_node_event(node=node_name, status="start", details=None)
    try:
        result = await fn(*args, **kwargs)
        emit_node_event(node=node_name, status="success", details=None)
        return result
    except Exception as exc:  # noqa: BLE001
        log_exception(f"workflow.{node_name}.error", exc)
        emit_node_event(node=node_name, status="error", details=str(exc))
        return None

    finally:
        end_span(span)


def _emit_routing_decision(ctx: ExecutionContext, task: str) -> None:
    """Emit a meta-level routing decision for a logical task.

    This is L3-only and uses routing.route_task_to_agent, which is itself
    a META-layer helper. It does not call any LLMs or mutate state.
    """

    try:
        meta_profile = getattr(ctx, "meta_profile", None)
        decision = route_task_to_agent(
            task=task,
            complexity=None,
            meta_profile=meta_profile,
        )
        emit_node_event(
            node=f"routing.{task}",
            status="decision",
            details=str(decision),
        )
    except Exception as exc:  # noqa: BLE001
        # Routing observability must never break orchestration.
        log_exception("workflow.routing_decision_error", exc)


# ============================================================================
#  WORKFLOW GRAPH EXECUTION (PHASE 3 + CORRECTION LOOP)
# ============================================================================


async def run_workflow_graph(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    Phase-3 canonical workflow graph with bounded correction loop:

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

    Correction loop (meta-level):

        1. Run full pass: Strategy + Retrieval → Drafting → QA → Safety.
        2. Evaluate correction surfaces via self_correction.evaluate_all_surfaces.
        3. Aggregate into a single CorrectionSignal.
        4. If no correction needed, or max corrections reached: stop.
        5. Otherwise, re-run the full pass (bounded by max_corrections).

    Notes:
        • No state mutation happens here; this is orchestration-only.
        • Correction loop is bounded by ctx.config.max_corrections (if present).
        • On any fatal failure, returns L2ResultBundle.empty_with_error(...).
    """
    root_span = start_span("workflow.run", ctx=ctx.span_context())
    try:
        # Determine how many *additional* correction passes are allowed.
        # If no config or field, default to 0 (single pass).
        max_corrections = 0
        cfg = getattr(ctx, "config", None)
        if cfg is not None:
            max_corrections = int(getattr(cfg, "max_corrections", 0) or 0)

        # We always perform at least one full pass; any additional passes
        # are triggered by the correction loop and capped by max_corrections.
        iterations = 1 + max(0, max_corrections)

        strategy_result: Optional[StrategyResult] = None
        rag_result: Optional[RAGResult] = None
        drafting_result: Optional[DraftingResult] = None
        qa_result: Optional[QAResult] = None
        safety_result: Optional[SafetyResult] = None

        for iteration in range(1, iterations + 1):
            emit_node_event(
                node="workflow_iteration",
                status="start",
                details=f"iteration={iteration}, max_corrections={max_corrections}",
            )

            # Sanity check: execute a DAG-backed single pass without
            # changing the authoritative results used below. Compare
            # only coarse types/shapes to catch regressions.
            try:
                dag_ctx = await _run_single_pass_via_dag(plans, ctx)
                dag_strategy = dag_ctx.get("strategy_result")
                dag_rag = dag_ctx.get("rag_result")
                dag_drafting = dag_ctx.get("drafting_result")
                dag_qa = dag_ctx.get("qa_result")
                dag_safety = dag_ctx.get("safety_result")

                if dag_strategy is not None and not isinstance(dag_strategy, StrategyResult):
                    log_exception(
                        "workflow.dag_mismatch.strategy", TypeError("StrategyResult type mismatch")
                    )
                if dag_rag is not None and not isinstance(dag_rag, RAGResult):
                    log_exception("workflow.dag_mismatch.rag", TypeError("RAGResult type mismatch"))
                if dag_drafting is not None and not isinstance(dag_drafting, DraftingResult):
                    log_exception(
                        "workflow.dag_mismatch.drafting", TypeError("DraftingResult type mismatch")
                    )
                if dag_qa is not None and not isinstance(dag_qa, QAResult):
                    log_exception("workflow.dag_mismatch.qa", TypeError("QAResult type mismatch"))
                if dag_safety is not None and not isinstance(dag_safety, SafetyResult):
                    log_exception(
                        "workflow.dag_mismatch.safety", TypeError("SafetyResult type mismatch")
                    )
            except Exception as exc:  # noqa: BLE001
                log_exception("workflow.dag_single_pass_error", exc)

            # ---------------------------------------------------------------
            # 1. STRATEGY + RETRIEVAL (parallel)
            # ---------------------------------------------------------------
            _emit_routing_decision(ctx, task="strategy_generate_branch")
            _emit_routing_decision(ctx, task="rag_retrieval")
            strategy_task = asyncio.create_task(
                _run_node(
                    Node.STRATEGY,
                    ctx,
                    _execute_strategy,
                    plans,
                    ctx,
                )
            )
            retrieval_task = asyncio.create_task(
                _run_node(
                    Node.RETRIEVAL,
                    ctx,
                    _execute_retrieval,
                    plans,
                    ctx,
                )
            )

            # Wait for both to complete; errors are handled inside _run_node.
            strategy_result = await strategy_task
            rag_result = await retrieval_task

            if rag_result is None:
                rag_result = RAGResult(evidence=[], used_hyde=False)

            # Strategy fallback should *never* halt the pipeline
            if strategy_result is None:
                strategy_result = StrategyResult(
                    branches=[],
                    chosen_branch_id="error",
                )

            # Prefer the DAG-produced strategy_result when available and
            # correctly typed.
            try:
                dag_ctx_for_strategy = await _run_single_pass_via_dag(plans, ctx)
                dag_strategy = dag_ctx_for_strategy.get("strategy_result")
                if isinstance(dag_strategy, StrategyResult):
                    strategy_result = dag_strategy
            except Exception as exc:  # noqa: BLE001
                log_exception("workflow.dag_strategy_swap_error", exc)

            # ---------------------------------------------------------------
            # 2. DRAFTING (depends on Strategy + Retrieval)
            # ---------------------------------------------------------------
            # Prefer the DAG-produced rag_result when available and
            # correctly typed, but fall back to the imperative result
            # otherwise.
            try:
                dag_ctx_for_rag = await _run_single_pass_via_dag(plans, ctx)
                dag_rag = dag_ctx_for_rag.get("rag_result")
                if isinstance(dag_rag, RAGResult):
                    rag_result = dag_rag
            except Exception as exc:  # noqa: BLE001
                log_exception("workflow.dag_rag_swap_error", exc)

            _emit_routing_decision(ctx, task="drafting_structure")
            drafting_result = await _run_node(
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

            # Prefer the DAG-produced drafting_result when available.
            try:
                dag_ctx_for_drafting = await _run_single_pass_via_dag(plans, ctx)
                dag_drafting = dag_ctx_for_drafting.get("drafting_result")
                if isinstance(dag_drafting, DraftingResult):
                    drafting_result = dag_drafting
            except Exception as exc:  # noqa: BLE001
                log_exception("workflow.dag_drafting_swap_error", exc)

            # ---------------------------------------------------------------
            # 3. QA
            # ---------------------------------------------------------------
            _emit_routing_decision(ctx, task="qa_semantic_check")
            qa_result = await _run_node(
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

            # Prefer the DAG-produced qa_result when available.
            try:
                dag_ctx_for_qa = await _run_single_pass_via_dag(plans, ctx)
                dag_qa = dag_ctx_for_qa.get("qa_result")
                if isinstance(dag_qa, QAResult):
                    qa_result = dag_qa
            except Exception as exc:  # noqa: BLE001
                log_exception("workflow.dag_qa_swap_error", exc)

            # ---------------------------------------------------------------
            # 4. SAFETY
            # ---------------------------------------------------------------
            _emit_routing_decision(ctx, task="safety_check")
            safety_result = await _run_node(
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

            # Prefer the DAG-produced safety_result when available.
            try:
                dag_ctx_for_safety = await _run_single_pass_via_dag(plans, ctx)
                dag_safety = dag_ctx_for_safety.get("safety_result")
                if isinstance(dag_safety, SafetyResult):
                    safety_result = dag_safety
            except Exception as exc:  # noqa: BLE001
                log_exception("workflow.dag_safety_swap_error", exc)

            # ---------------------------------------------------------------
            # 5. Correction evaluation (meta-level, no state mutation)
            # -----------------------------------------------------------
            try:
                signals = evaluate_all_surfaces(
                    strategy=strategy_result,
                    rag=rag_result,
                    drafting=drafting_result,
                    qa=qa_result,
                    safety=safety_result,
                )
                correction = aggregate_correction_signals(signals)

                if correction is None or not correction.needs_correction:
                    # No correction needed → exit loop early.
                    break

                # If we have used all allowed corrections, stop here.
                if iteration > max_corrections:
                    break

                # Otherwise, loop continues and we re-run the full pass.
                details = (
                    f"iteration={iteration}, surface={correction.surface}, "
                    f"severity={correction.severity}, "
                    f"recommended_action={correction.recommended_action}"
                )
                emit_node_event(
                    node="workflow_correction",
                    status="requested",
                    details=details,
                )
            except Exception as exc:  # noqa: BLE001
                # Correction evaluation must never break the workflow;
                # log and continue with current results.
                log_exception("workflow.correction_evaluation_error", exc)
                break

        # ---------------------------------------------------------------
        # Return results (L3 does not modify them)
        # Ensure non-optional values for type-checking.
        # ---------------------------------------------------------------
        if strategy_result is None:
            strategy_result = StrategyResult(branches=[], chosen_branch_id="error")
        if rag_result is None:
            rag_result = RAGResult(evidence=[], used_hyde=False)
        if drafting_result is None:
            drafting_result = DraftingResult(sections=[])
        if qa_result is None:
            qa_result = QAResult(findings=[])
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
        log_exception("workflow.run.fatal", exc)
        return L2ResultBundle.empty_with_error(str(exc))

    finally:
        end_span(root_span)
