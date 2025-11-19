# FILE: l3.py
"""
Unified L3 Orchestration Layer (v10_9) — PURE CONTROL FLOW (RESTORED)

This module provides the complete orchestration logic for the v10_9
agentic architecture. It restores orchestration capabilities that were
present in v10_8 but simplified in v10_9, while preserving strict
L1–L5 separation:

    • L1: planning only (PlanObject).
    • L2: execution only (ExecutionResult).
    • L3: control flow / orchestration only.
    • L4: state management only (StateAdapter).
    • L5: safety & policy only (SafetyEngine, PolicyEngine, ArbitrationEngine).
    • META: self_correction, multi-agent councils (no state writes, no tools).

Key responsibilities of L3:

    • Model workflows as DAGs with:
        - parallel nodes
        - conditional edges
        - fallback edges (multi-path fallbacks)
    • Coordinate L2 executors via route_executor(plan, state).
    • Attach predictive caching & optimization hints (metadata-only).
    • Emit NodeResult metadata for each node (status, timings, payload refs).
    • Emit route traces and correction journal entries as telemetry.
    • Propagate escalation actions ("escalate") for L5/HIL handling.

Non-responsibilities (to preserve purity):

    • NO business reasoning (L1).
    • NO direct tool/LLM/provider calls (L2).
    • NO durable state storage (L4).
    • NO safety/policy enforcement (L5).

Public entrypoint:

    • DAGExecutor.run(plan: PlanObject, initial_state: dict, state_adapter: StateAdapter) -> WorkflowState
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set, Tuple

from models import (
    PlanObject,
    ExecutionResult,
    WorkflowState,
    WorkflowPhase,
    NodeResult,
    NodeStatus,
    StatePatch,
    RouteTraceEntry,
    CorrectionJournalEntry,
    SelfCorrectionSurface,
)
from exceptions import ValidationError, WorkflowTimeoutError, ToolExecutionError
from state_adapter_stack import StateAdapter
from l2 import route_executor


# =============================================================================
# 1. ORCHESTRATION-SPECIFIC EXCEPTIONS
# =============================================================================


class DAGValidationError(ValidationError):
    """Raised when a DAG is structurally invalid (missing nodes, cycles, etc.)."""


class ControlFlowError(Exception):
    """Raised when orchestration cannot make progress due to misconfigured DAG."""


class NodeExecutionError(Exception):
    """Raised when a node fails irrecoverably after retries."""


# =============================================================================
# 2. DAG MODEL
# =============================================================================


@dataclass
class DAGNode:
    """
    Single node in the orchestration DAG.

    Restores and extends v10_8 behavior:

        • depends_on: upstream dependencies (for DAG edges).
        • fallback: list of node names to use if this node ultimately fails.
        • parallel_group: label to group nodes that may run concurrently.
        • max_retries: maximum retries before considering node failed.
        • predictive_cache_key: hint for external predictive caching layers.
        • surfaces: self-correction surfaces (RAG retry, draft retry, etc.).
    """

    name: str
    mode: str
    plan: PlanObject
    depends_on: List[str] = field(default_factory=list)
    fallback: List[str] = field(default_factory=list)
    parallel_group: Optional[str] = None
    max_retries: int = 0
    predictive_cache_key: Optional[Dict[str, Any]] = None
    surfaces: List[SelfCorrectionSurface] = field(default_factory=list)


@dataclass
class DAGModel:
    """
    In-memory representation of a workflow DAG.

    nodes: mapping of node_name -> DAGNode
    """

    nodes: Dict[str, DAGNode] = field(default_factory=dict)

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #

    def validate(self) -> None:
        """
        Validate basic DAG invariants:

            • Node keys must match node.name.
            • All dependencies and fallback targets must exist.
            • Graph must be acyclic.
        """
        # Names must match keys
        for node_name, node in self.nodes.items():
            if node_name != node.name:
                raise DAGValidationError(
                    f"Node key '{node_name}' does not match node name '{node.name}'."
                )

        # All deps and fallbacks must exist
        for node in self.nodes.values():
            for dep in node.depends_on:
                if dep not in self.nodes:
                    raise DAGValidationError(
                        f"Dependency '{dep}' for node '{node.name}' is not a defined node."
                    )
            for fb in node.fallback:
                if fb not in self.nodes:
                    raise DAGValidationError(
                        f"Fallback target '{fb}' for node '{node.name}' is not a defined node."
                    )

        # Cycle detection (Kahn's algorithm)
        self._ensure_acyclic()

    def _ensure_acyclic(self) -> None:
        indegree: Dict[str, int] = {name: 0 for name in self.nodes}
        for node in self.nodes.values():
            for dep in node.depends_on:
                indegree[node.name] += 1

        queue: List[str] = [n for n, deg in indegree.items() if deg == 0]
        visited_count = 0

        while queue:
            current = queue.pop()
            visited_count += 1
            for neighbor in self._dependents_of(current):
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        if visited_count != len(self.nodes):
            raise DAGValidationError("DAG contains at least one cycle.")

    def _dependents_of(self, node_name: str) -> List[str]:
        deps: List[str] = []
        for n in self.nodes.values():
            if node_name in n.depends_on:
                deps.append(n.name)
        return deps

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def root_nodes(self) -> List[DAGNode]:
        """Nodes with no dependencies."""
        return [n for n in self.nodes.values() if not n.depends_on]


# =============================================================================
# 3. DAG BUILDING FROM PLANOBJECT
# =============================================================================


def build_dag_from_plan(plan: PlanObject) -> DAGModel:
    """
    Construct a DAGModel from an L1 PlanObject.

    Expected plan structure for full workflows:

        plan["dag"] = {
            "nodes": [
                {
                    "name": "strategy",
                    "mode": "strategy",
                    "depends_on": [],
                    "fallback": [],
                    "parallel_group": null,
                    "max_retries": 0,
                    "predictive_cache_key": {...},
                    "surfaces": ["rag_retry", "draft_retry"]
                },
                ...
            ]
        }

    If no "dag" block is present, we construct a minimal single-node DAG
    representing the plan itself. This preserves backward compatibility
    with simpler usages.
    """
    dag_spec = plan.get("dag") or {}
    nodes_spec = dag_spec.get("nodes") or []

    if not nodes_spec:
        # Minimal fallback: single node for the plan itself.
        mode = plan.get("mode") or "unknown"
        node = DAGNode(
            name=str(plan.get("name", mode)),
            mode=str(mode),
            plan=plan,
            depends_on=[],
            fallback=[],
            parallel_group=None,
            max_retries=int(plan.get("max_retries", 0)),
            predictive_cache_key=plan.get("predictive_cache_key"),
            surfaces=[
                SelfCorrectionSurface.RAG_RETRY,
                SelfCorrectionSurface.DRAFT_RETRY,
            ],
        )
        dag = DAGModel(nodes={node.name: node})
        dag.validate()
        return dag

    nodes: Dict[str, DAGNode] = {}
    for ns in nodes_spec:
        name = str(ns.get("name", "")).strip()
        mode = str(ns.get("mode", "")).strip()
        if not name or not mode:
            raise DAGValidationError("Each DAG node must have non-empty 'name' and 'mode'.")

        # Per-node PlanObject may be provided; otherwise clone base plan with mode.
        node_plan_raw = ns.get("plan") or plan.to_dict()
        node_plan_raw["mode"] = mode
        node_plan = PlanObject(node_plan_raw)

        surfaces: List[SelfCorrectionSurface] = []
        for s in ns.get("surfaces", []):
            try:
                surfaces.append(SelfCorrectionSurface(str(s)))
            except ValueError:
                # Unknown surfaces are ignored but preserved in metadata if needed.
                continue

        node = DAGNode(
            name=name,
            mode=mode,
            plan=node_plan,
            depends_on=[str(d) for d in ns.get("depends_on", [])],
            fallback=[str(fb) for fb in ns.get("fallback", [])],
            parallel_group=str(ns["parallel_group"]) if ns.get("parallel_group") else None,
            max_retries=int(ns.get("max_retries", 0)),
            predictive_cache_key=ns.get("predictive_cache_key"),
            surfaces=surfaces,
        )
        nodes[node.name] = node

    dag = DAGModel(nodes=nodes)
    dag.validate()
    return dag


# =============================================================================
# 4. SIMPLE PHASE MACHINE & COST TRACKER (L3-LOCAL)
# =============================================================================


class PhaseMachine:
    """
    Minimal phase machine for WorkflowPhase transitions.

    This is intentionally simple; it is local to L3 and does not replace
    any richer PhaseMachine you may have elsewhere.
    """

    def __init__(self) -> None:
        self._phase = WorkflowPhase.INIT
        self.history: List[WorkflowPhase] = [self._phase]

    def set(self, phase: WorkflowPhase) -> None:
        self._phase = phase
        self.history.append(phase)

    def current_value(self) -> WorkflowPhase:
        return self._phase


class CostTracker:
    """
    Extremely simple cost tracker for L3-level accounting.

    Full cost/latency dashboards live elsewhere; this only aggregates
    per-node usage tokens and allows L3 to attach them to WorkflowState.
    """

    def __init__(self) -> None:
        self.total_tokens: int = 0
        self.per_node: Dict[str, int] = {}

    def record(self, node_name: str, usage: Dict[str, Any]) -> None:
        tokens = int(usage.get("tokens", 0))
        self.total_tokens += tokens
        self.per_node[node_name] = self.per_node.get(node_name, 0) + tokens


# =============================================================================
# 5. DAG EXECUTOR
# =============================================================================


class DAGExecutor:
    """
    Deterministic executor for DAG nodes with:

        • Parallel execution of independent nodes.
        • Fallback edges when nodes fail (multi-path).
        • Simple retry logic (per-node max_retries).
        • Predictive cache hinting (metadata only).
        • NodeResult metadata emission.
        • Route trace and correction journal surfaces.

    All durable state writes must go through the provided StateAdapter,
    which belongs to L4.
    """

    def __init__(
        self,
        state_adapter: StateAdapter,
        l2_executor: Callable[[PlanObject, Dict[str, Any]], Awaitable[ExecutionResult[Any]]] = route_executor,
    ) -> None:
        self.state_adapter = state_adapter
        self.l2_executor = l2_executor

        self.node_results: Dict[str, NodeResult] = {}
        self.route_trace: List[RouteTraceEntry] = []
        self.correction_journal: List[CorrectionJournalEntry] = []

    # ------------------------------------------------------------------ #
    # Helper: which nodes are ready to run?
    # ------------------------------------------------------------------ #

    def _ready_nodes(self, dag: DAGModel, completed: Set[str], running: Set[str]) -> List[DAGNode]:
        ready: List[DAGNode] = []
        for node in dag.nodes.values():
            if node.name in completed or node.name in running:
                continue
            if all(dep in completed for dep in node.depends_on):
                ready.append(node)
        return ready

    # ------------------------------------------------------------------ #
    # Helper: apply payload → state via StateAdapter
    # ------------------------------------------------------------------ #

    def _apply_payload_to_state(self, node: DAGNode, result: ExecutionResult[Any]) -> None:
        """
        Normalize payload from ExecutionResult into state using L4.StateAdapter.

        This mirrors and modernizes v10_8 behavior where L3 wrote specific
        results into state for later stages.
        """
        payload = result.payload

        # Normalize for objects with .to_dict
        if hasattr(payload, "to_dict"):
            pdict = payload.to_dict()  # type: ignore[assignment]
        else:
            pdict = payload if isinstance(payload, dict) else {"value": payload}

        norm_mode = str(node.mode).lower()

        if norm_mode == "strategy":
            self.state_adapter.apply_patch(StatePatch(key="strategy_result", value=pdict))
        elif norm_mode == "rag":
            self.state_adapter.apply_patch(StatePatch(key="rag_result", value=pdict))
        elif norm_mode == "drafting":
            self.state_adapter.apply_patch(StatePatch(key="draft_result", value=pdict))
        elif norm_mode == "bullets":
            self.state_adapter.apply_patch(StatePatch(key="bullet_result", value=pdict))
        elif norm_mode == "qa":
            self.state_adapter.apply_patch(StatePatch(key="qa_result", value=pdict))
        elif norm_mode == "safety":
            self.state_adapter.apply_patch(StatePatch(key="safety_result", value=pdict))
        elif norm_mode == "prompt_engineering":
            self.state_adapter.apply_patch(StatePatch(key="prompt_meta", value=pdict))
        elif norm_mode == "hil":
            self.state_adapter.apply_patch(StatePatch(key="hil_result", value=pdict))
        elif norm_mode == "meta_learning":
            self.state_adapter.apply_patch(StatePatch(key="meta_learning_result", value=pdict))
        else:
            # Unknown modes are stored under "last_execution"
            self.state_adapter.apply_patch(
                StatePatch(key="last_execution", value={"mode": norm_mode, "payload": pdict})
            )

    # ------------------------------------------------------------------ #
    # Helper: record route trace and correction journal
    # ------------------------------------------------------------------ #

    def _record_route(self, node: DAGNode, result: ExecutionResult[Any]) -> None:
        self.route_trace.append(
            RouteTraceEntry(
                step=node.name,
                model=result.model,
                endpoint=None,
                rationale=f"Executed mode={node.mode}",
                metadata={"status": result.status},
            )
        )

    def _record_corrections(
        self,
        node: DAGNode,
        result: ExecutionResult[Any],
        attempt: int,
    ) -> None:
        if result.ok:
            return
        # Map surfaces to journal entries
        now = time.time()
        for surface in node.surfaces or [SelfCorrectionSurface.UNKNOWN]:
            self.correction_journal.append(
                CorrectionJournalEntry(
                    event_id=f"{node.name}:{attempt}:{surface.value}",
                    surface=surface,
                    message=f"L2 execution failed for node '{node.name}' on surface '{surface.value}'.",
                    created_at=now,
                    metadata={"errors": result.errors, "status": result.status},
                )
            )

    # ------------------------------------------------------------------ #
    # Core: execute a single node with retries
    # ------------------------------------------------------------------ #

    async def _execute_node(
        self,
        node: DAGNode,
        state: Dict[str, Any],
        cost_tracker: CostTracker,
    ) -> NodeResult:
        started_at = time.time()
        attempts = 0
        last_result: Optional[ExecutionResult[Any]] = None

        while True:
            attempts += 1
            try:
                result = await self.l2_executor(node.plan, state)
            except WorkflowTimeoutError as exc:
                # Hard failure; no retry at L3 for timeouts.
                raise NodeExecutionError(f"Timeout executing node '{node.name}': {exc}") from exc
            except ToolExecutionError as exc:
                # counted as error; may still retry depending on max_retries
                result = ExecutionResult(
                    status="error",
                    payload=None,
                    errors=[str(exc)],
                    model="l2-executor-error",
                    usage={},
                    metadata={},
                )

            last_result = result
            cost_tracker.record(node.name, result.usage)
            self._record_route(node, result)
            self._record_corrections(node, result, attempts)

            if result.ok:
                # Apply payload to state via adapter.
                self._apply_payload_to_state(node, result)
                status = NodeStatus.SUCCESS
                break

            if attempts > node.max_retries:
                status = NodeStatus.ERROR
                break

        finished_at = time.time()
        nr = NodeResult(
            node_id=node.name,
            status=status,
            result=last_result,
            started_at=started_at,
            finished_at=finished_at,
            metadata={
                "mode": node.mode,
                "attempts": attempts,
                "predictive_cache_key": node.predictive_cache_key,
            },
        )
        self.node_results[node.name] = nr
        return nr

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def run(self, plan: PlanObject, initial_state: Dict[str, Any]) -> WorkflowState:
        """
        Execute full L3 orchestration for a single L1 PlanObject.

        This is a synchronous API; higher layers may wrap it with asyncio
        as needed. Internally, this uses asyncio.run to call the async L2
        route_executor.

        All state mutations are performed via L4.StateAdapter; the
        returned WorkflowState contains the final snapshot.
        """
        machine = PhaseMachine()
        cost_tracker = CostTracker()

        # Initialize adapter state.
        self.state_adapter.state = dict(initial_state)

        # Build and validate DAG from plan.
        dag = build_dag_from_plan(plan)

        async def _run_async() -> None:
            nonlocal machine, cost_tracker

            machine.set(WorkflowPhase.PLANNING)
            machine.set(WorkflowPhase.EXECUTING)

            completed: Set[str] = set()
            running: Set[str] = set()
            errors: List[str] = []

            # Basic parallel scheduler: run all ready nodes concurrently.
            while len(completed) < len(dag.nodes):
                ready_nodes = self._ready_nodes(dag, completed, running)

                if not ready_nodes and running:
                    # Wait for at least one running task to complete.
                    await asyncio.sleep(0.001)
                    continue

                if not ready_nodes and not running:
                    # No ready or running nodes → deadlock or all failed.
                    unresolved = set(dag.nodes) - completed
                    raise ControlFlowError(
                        f"No progress possible in DAG; unresolved nodes: {sorted(unresolved)}"
                    )

                # Run ready nodes in parallel.
                tasks: List[Tuple[DAGNode, Awaitable[NodeResult]]] = []
                for node in ready_nodes:
                    running.add(node.name)
                    tasks.append((node, self._execute_node(node, self.state_adapter.state, cost_tracker)))

                results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)

                for (node, _), res in zip(tasks, results):
                    running.discard(node.name)
                    if isinstance(res, Exception):
                        # Hard node failure
                        errors.append(str(res))
                        self.node_results[node.name] = NodeResult(
                            node_id=node.name,
                            status=NodeStatus.ERROR,
                            result=None,
                            started_at=None,
                            finished_at=None,
                            metadata={"exception": str(res)},
                        )
                        completed.add(node.name)
                        # Trigger fallbacks (they will become ready once deps satisfied).
                        continue

                    nr: NodeResult = res
                    if nr.status == NodeStatus.SUCCESS:
                        completed.add(node.name)
                    else:
                        errors.extend(nr.result.errors if nr.result else [])
                        completed.add(node.name)
                        # Fallback edges: mark dependents as satisfied via this failure;
                        # actual fallback nodes are part of DAG, and their deps will
                        # reference this node as a prerequisite, so they can run.
                        # Higher-level logic decides how to interpret.
                        continue

            # All nodes completed
            if errors:
                machine.set(WorkflowPhase.FAILED)
            else:
                machine.set(WorkflowPhase.COMPLETE)

        try:
            asyncio.run(_run_async())
        except Exception:
            # Any unexpected failure is considered a control-flow error.
            machine.set(WorkflowPhase.FAILED)
            raise

        final_state = self.state_adapter.state
        node_statuses: Dict[str, NodeStatus] = {
            node_id: nr.status for node_id, nr in self.node_results.items()
        }
        summary = "workflow_complete" if machine.current_value() == WorkflowPhase.COMPLETE else "workflow_failed"
        errors: List[str] = []
        for nr in self.node_results.values():
            if nr.status == NodeStatus.ERROR and nr.result and nr.result.errors:
                errors.extend(nr.result.errors)

        # Attach basic metadata including cost and traces.
        metadata: Dict[str, Any] = {
            "history": [p.value for p in machine.history],
            "total_tokens": cost_tracker.total_tokens,
            "per_node_tokens": cost_tracker.per_node,
            "route_trace": [rt.__dict__ for rt in self.route_trace],
            "correction_journal": [cj.__dict__ for cj in self.correction_journal],
        }

        return WorkflowState(
            workflow_id=str(plan.get("workflow_id", final_state.get("workflow_id", "workflow"))),
            phase=machine.current_value(),
            node_statuses=node_statuses,
            summary=summary,
            result=final_state,
            errors=errors,
            trace_id=str(final_state.get("trace_id", "")) or None,
            metadata=metadata,
        )
