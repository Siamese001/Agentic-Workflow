# FILE: 10_10/l3.py
"""
Unified L3 Orchestration Layer (v10_10 · Phase 1)
=================================================

Responsibilities:
    • Orchestrate L2 (execution), L5 (safety), and L4 (state patch) using a DAG.
    • Implement bounded retry / correction loop (G4, G8, G9, G36).
    • Use the shared WorkflowGraph substrate for DAG structure (G6, G7).
    • Remain PURE control flow:
        - No LLM calls (L2 only).
        - No tool calls (L2 only).
        - No persistent state mutation (L4 only constructs patches).
        - No policy enforcement (L5 only evaluates SafetyResult).

Non-Responsibilities:
    • Planning (L1).
    • Retrieval / ranking implementation details (L2, retrieval.py, ranking.py).
    • State mutation or I/O (L4 and outer caller).
    • Safety algorithms (L5, safety policies).

High-level flow per workflow:
    1. L1 builds WorkflowPlanBundle (Strategy/RAG/Drafting/QA/Safety plans).
    2. L3.run_dag():
         for attempt in [0..max_retries]:
             a. Build a simple L2+L5 DAG via WorkflowGraph.
             b. Run DAG synchronously (no LLM here).
             c. Compute correction signals from L2 results.
             d. If severe corrections and retries remain → loop.
             e. Else break.
         f. Build final state patch via L4.apply_state_patch().
         g. Return DAGResult to main_v10_10.

Note:
    The WorkflowGraph engine (workflow_graph.py) provides structured DAG
    representation and topological layering. L3 uses that for G6/G7 while
    keeping execution synchronous to remain compatible with main_v10_10.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from models import (
    ExecutionContext,
    WorkflowPlanBundle,
    L2ResultBundle,
    QAResult,
    SafetyResult,
)
from observability import start_span, end_span, record_exception, emit_telemetry_event
from workflow_graph import (
    WorkflowGraph,
    WorkflowNode,
    WorkflowEdge,
    ExecutionResult,
    NodeStatus,
)
from self_correction import CorrectionSignal
from l2 import execute_workflow_plans
from l4 import apply_state_patch
from l5 import safety_gate


# =============================================================================
# Result bundle returned by L3
# =============================================================================


@dataclass
class DAGResult:
    """
    Typed bundle returned by L3 after DAG execution.

    This preserves the v10_10 shape used by main_v10_10 while aligning
    with the Phase 0 models.
    """

    l2_results: Optional[L2ResultBundle]
    corrections: List[CorrectionSignal]
    corrected: bool
    safety_passed: bool
    final_state_patch: Dict[str, Any]


# =============================================================================
# Internal helpers — corrections and severity
# =============================================================================


def _has_qa_errors(qa: Optional[QAResult]) -> bool:
    if qa is None or not getattr(qa, "findings", None):
        return False
    return any((getattr(f, "status", "") or "").lower() == "error" for f in qa.findings)


def _has_blocking_safety(safety: Optional[SafetyResult]) -> bool:
    if safety is None or not getattr(safety, "findings", None):
        return False
    # SafetyFinding typically has status + maybe blocking flag; we treat any
    # "blocked" status as severe for Phase 1.
    for f in safety.findings:
        status = (getattr(f, "status", "") or "").lower()
        if status == "blocked":
            return True
    return False


def _compute_corrections(l2_results: L2ResultBundle) -> List[CorrectionSignal]:
    """
    Minimal, deterministic correction logic for Phase 1.

    This is intentionally conservative and only looks at:
        • QAResult findings
        • SafetyResult findings

    Future phases can move richer logic back into self_correction surfaces.
    """
    signals: List[CorrectionSignal] = []

    qa = l2_results.qa
    safety = l2_results.safety

    if _has_qa_errors(qa):
        signals.append(
            CorrectionSignal(
                surface="qa",
                severity=2,
                reason="QA findings contain one or more errors.",
                recommended_action="retry_qa",
            )
        )

    if _has_blocking_safety(safety):
        signals.append(
            CorrectionSignal(
                surface="safety",
                severity=3,
                reason="Safety findings contain blocking issues.",
                recommended_action="retry_safety",
            )
        )

    return signals


def _max_severity(signals: List[CorrectionSignal]) -> int:
    if not signals:
        return 0
    return max(int(getattr(s, "severity", 0) or 0) for s in signals)


# =============================================================================
# Internal helpers — DAG construction and execution
# =============================================================================


def _build_attempt_graph(
    ctx: ExecutionContext,
    plans: WorkflowPlanBundle,
) -> WorkflowGraph:
    """
    Build a simple DAG for a single L2+L5 attempt.

    Nodes:
        • l2_execute   – L2.execute_workflow_plans(plans, ctx)
        • safety_gate  – L5.safety_gate(l2_results.safety)

    Edges:
        • l2_execute → safety_gate

    L4.apply_state_patch() is invoked outside the DAG, after the attempt
    completes, so that corrections and final safety decision can be passed in
    cleanly.
    """

    def l2_executor(payload: Dict[str, Any]) -> ExecutionResult:
        span = start_span("l3.node.l2_execute", ctx=ctx.span_context())
        try:
            l2_results = execute_workflow_plans(plans, ctx)
            emit_telemetry_event(
                "l3.l2_completed",
                attributes={
                    "workflow_id": ctx.job.workflow_id if hasattr(ctx.job, "workflow_id") else "workflow_v10_10",
                },
                span_id=span.get("id") if isinstance(span, dict) else None,
            )
            return ExecutionResult(
                status=NodeStatus.SUCCESS,
                output={"l2_results": l2_results},
            )
        except Exception as exc:
            record_exception("l3.l2_execute_error", exc)
            return ExecutionResult(
                status=NodeStatus.FAILED,
                output=None,
                error=exc,
            )
        finally:
            end_span(span)

    def safety_executor(payload: Dict[str, Any]) -> ExecutionResult:
        span = start_span("l3.node.safety_gate", ctx=ctx.span_context())
        try:
            preds = payload.get("predecessor_outputs", {})
            l2_output = preds.get("l2_execute") or {}
            l2_results = l2_output.get("l2_results")

            if l2_results is None:
                # If L2 failed, safety cannot pass.
                return ExecutionResult(
                    status=NodeStatus.FAILED,
                    output={"safety_passed": False},
                    error=RuntimeError("L2 results missing; cannot run safety."),
                )

            safety_passed = safety_gate(l2_results.safety)

            emit_telemetry_event(
                "l3.safety_evaluated",
                attributes={"safety_passed": bool(safety_passed)},
                span_id=span.get("id") if isinstance(span, dict) else None,
            )

            return ExecutionResult(
                status=NodeStatus.SUCCESS,
                output={"safety_passed": bool(safety_passed)},
            )
        except Exception as exc:
            record_exception("l3.safety_gate_error", exc)
            return ExecutionResult(
                status=NodeStatus.FAILED,
                output={"safety_passed": False},
                error=exc,
            )
        finally:
            end_span(span)

    nodes = {
        "l2_execute": WorkflowNode(
            id="l2_execute",
            executor=l2_executor,
            parallelizable=False,
            description="L2 workflow execution (strategy + rag + drafting + qa + safety).",
        ),
        "safety_gate": WorkflowNode(
            id="safety_gate",
            executor=safety_executor,
            parallelizable=False,
            description="L5 safety gate based on SafetyResult.",
        ),
    }

    edges = [
        WorkflowEdge(src="l2_execute", dst="safety_gate"),
    ]

    return WorkflowGraph(nodes=nodes, edges=edges)


def _run_graph_sync(
    graph: WorkflowGraph,
    initial_payload: Dict[str, Any],
    l3_context: Dict[str, Any],
) -> Dict[str, ExecutionResult]:
    """
    Synchronous execution using WorkflowGraph topology (Kahn layers).

    We deliberately avoid async here to remain compatible with the existing
    main_v10_10 signature, while still leveraging WorkflowGraph's structural
    guarantees for G6/G7.
    """
    results: Dict[str, ExecutionResult] = {}

    for layer in graph.topological_layers():
        for node_id in layer:
            node = graph.nodes[node_id]

            payload = {
                "node_id": node_id,
                "initial_payload": initial_payload,
                "predecessor_outputs": {
                    pid: results[pid].output for pid in _predecessors_of(graph, node_id) if pid in results
                },
                "l3_context": l3_context,
                "node_config": node.config,
            }

            span = start_span(f"l3.node.{node_id}", ctx=l3_context.get("span_ctx"))
            try:
                res = node.executor(payload)
                if not isinstance(res, ExecutionResult):
                    raise ValueError(f"Executor for node {node_id} must return ExecutionResult.")
                results[node_id] = res
            except Exception as exc:
                record_exception(f"l3.{node_id}_unhandled_exception", exc)
                results[node_id] = ExecutionResult(
                    status=NodeStatus.FAILED,
                    output=None,
                    error=exc,
                )
            finally:
                end_span(span)

            if results[node_id].status in (NodeStatus.FAILED, NodeStatus.RETRY, NodeStatus.REPLAN, NodeStatus.ESCALATE):
                # Stop on any non-success signal; outer loop decides what to do.
                return results

    return results


def _predecessors_of(graph: WorkflowGraph, node_id: str) -> List[str]:
    preds: List[str] = []
    for src, dsts in graph.adjacency.items():
        if node_id in dsts:
            preds.append(src)
    return preds


# =============================================================================
# Public Orchestration Entrypoint
# =============================================================================


def run_dag(
    ctx: ExecutionContext,
    plans: WorkflowPlanBundle,
    max_retries: int = 2,
) -> DAGResult:
    """
    L3 DAG Execution Loop (Deterministic, Phase 1)

    Workflow:
        For up to max_retries:
            1. Run L2 (execute_workflow_plans) and L5 safety via WorkflowGraph.
            2. Compute correction signals from L2 results.
            3. If severe corrections and retries remain → retry.
            4. Else break.

        After loop:
            5. Build final state patch via L4.apply_state_patch.
            6. Return DAGResult (no state mutation here).

    Notes:
        • No LLM calls here (L2 only).
        • No direct state mutation (L4 only).
        • No safety policy logic (L5 only).
    """
    span = start_span("l3.run_dag", ctx=ctx.span_context())

    retries = 0
    corrected = False

    last_l2: Optional[L2ResultBundle] = None
    last_corrections: List[CorrectionSignal] = []
    last_safety_passed: bool = False
    last_state_patch: Dict[str, Any] = {}

    try:
        while True:
            attempt = retries + 1

            graph = _build_attempt_graph(ctx, plans)
            initial_payload: Dict[str, Any] = {
                "attempt": attempt,
            }
            l3_context: Dict[str, Any] = {
                "attempt": attempt,
                "max_retries": max_retries,
                "span_ctx": ctx.span_context(),
            }

            results = _run_graph_sync(graph, initial_payload, l3_context)

            l2_exec = results.get("l2_execute")
            safety_exec = results.get("safety_gate")

            if l2_exec is None or l2_exec.status is not NodeStatus.SUCCESS:
                # Hard failure; cannot proceed further.
                emit_telemetry_event(
                    "l3.l2_failed",
                    attributes={"attempt": attempt},
                )
                break

            l2_results = l2_exec.output.get("l2_results")
            if not isinstance(l2_results, L2ResultBundle):
                raise RuntimeError("Invalid L2ResultBundle returned from L2 executor.")

            last_l2 = l2_results

            safety_passed = False
            if safety_exec is not None and safety_exec.status is NodeStatus.SUCCESS:
                safety_passed = bool(safety_exec.output.get("safety_passed", False))
            last_safety_passed = safety_passed

            # ------------------------------
            # Corrections (Phase 1 minimal)
            # ------------------------------
            corrections = _compute_corrections(l2_results)
            last_corrections = corrections

            severity = _max_severity(corrections)

            emit_telemetry_event(
                "l3.corrections_evaluated",
                attributes={"attempt": attempt, "severity": severity, "num_corrections": len(corrections)},
            )

            if severity <= 0:
                # No correction needed; break loop.
                break

            retries += 1
            corrected = True

            if retries > max_retries:
                emit_telemetry_event(
                    "l3.max_retries_exceeded",
                    attributes={"max_retries": max_retries},
                )
                break

            # Otherwise → retry with same plans (Phase 1).
            # Future phases may adjust plans (replan) based on corrections.

        # ------------------------------
        # Final state patch via L4
        # ------------------------------
        if last_l2 is not None:
            last_state_patch = apply_state_patch(
                l2_results=last_l2,
                corrections=last_corrections,
                ctx=ctx,
                safety_passed=last_safety_passed,
            )

        return DAGResult(
            l2_results=last_l2,
            corrections=last_corrections,
            corrected=corrected,
            safety_passed=last_safety_passed,
            final_state_patch=last_state_patch,
        )

    except Exception as exc:
        record_exception("l3.dag_failure", exc)
        raise
    finally:
        end_span(span)
