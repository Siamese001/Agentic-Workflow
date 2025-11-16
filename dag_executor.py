"""
Deterministic DAG execution engine for control-flow orchestrators.

This module executes DAG definitions produced by the control-flow
specification without embedding any higher-level orchestration logic.
Execution is deterministic and side-effect free: a new context object
is returned with execution trace metadata appended.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Set

from dag_spec import DAG
from errors_controlflow import NodeExecutionError
from node_result import NodeResult, NodeStatus


class DAGExecutor:
    """Deterministic executor for DAG nodes with retry and tracing."""

    def __init__(self, backoff_strategy: str = "exponential") -> None:
        self.backoff_strategy = backoff_strategy

    def run(self, dag: DAG, initial_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Execute the DAG and return a new context containing results and trace.

        The executor walks the DAG in a deterministic order, honoring retry
        policies, conditional routing, and failure fallbacks while preserving
        the original context from mutation.
        """

        dag.validate()
        context: Dict[str, Any] = deepcopy(initial_context) if initial_context else {}
        trace = context.setdefault("_trace", {}).setdefault("nodes", {})

        parents = self._build_parents_map(dag)
        ready: List[str] = sorted([name for name, deps in parents.items() if not deps])
        executed: Set[str] = set()

        while ready:
            node_name = ready.pop(0)
            if node_name in executed:
                continue

            node = dag.nodes[node_name]
            node_trace = {
                "start_time": None,
                "end_time": None,
                "status": None,
                "retries": 0,
            }
            attempts = 0
            start_time = datetime.utcnow().isoformat()

            while True:
                result = node.run(deepcopy(context))
                attempts += 1
                node_trace["status"] = result.status.value
                if result.status is NodeStatus.RETRY and self._should_retry(node, attempts):
                    node_trace["retries"] = attempts
                    self._deterministic_backoff(node, attempts)
                    continue
                break

            end_time = datetime.utcnow().isoformat()
            node_trace["start_time"] = start_time
            node_trace["end_time"] = end_time
            node_trace["retries"] = attempts - 1
            trace[node_name] = node_trace

            context = {**context, **result.output}
            executed.add(node_name)

            if result.status is NodeStatus.FAILURE:
                fallback_edges = (node.conditional_edges or {}).get(NodeStatus.FAILURE.value)
                if fallback_edges:
                    self._enqueue_targets(
                        dag, fallback_edges, parents, executed, ready
                    )
                else:
                    raise NodeExecutionError(f"Node '{node_name}' failed execution.")
                continue

            outgoing = self._determine_outgoing_edges(dag, node_name, node, result)
            self._enqueue_targets(dag, outgoing, parents, executed, ready)

        return context

    def _should_retry(self, node: Any, attempts: int) -> bool:
        policy = node.retry_policy or {}
        max_retries = int(policy.get("max_retries", 0))
        return attempts <= max_retries

    def _deterministic_backoff(self, node: Any, attempts: int) -> None:
        # Deterministic placeholder for retry backoff; intentionally no sleep.
        _ = (self.backoff_strategy, attempts, node.name)

    def _determine_outgoing_edges(
        self, dag: DAG, node_name: str, node: Any, result: NodeResult
    ) -> List[str]:
        if result.next_edges is not None:
            return result.next_edges
        if node.conditional_edges:
            status_key = result.status.value
            if status_key in node.conditional_edges:
                return node.conditional_edges[status_key]
        return dag.edges.get(node_name, [])

    def _build_parents_map(self, dag: DAG) -> Dict[str, Set[str]]:
        parents: Dict[str, Set[str]] = {name: set() for name in dag.nodes}
        for source, targets in dag.edges.items():
            for target in targets:
                parents[target].add(source)
        return parents

    def _enqueue_targets(
        self,
        dag: DAG,
        targets: List[str],
        parents: Dict[str, Set[str]],
        executed: Set[str],
        ready: List[str],
    ) -> None:
        for target in targets:
            if target not in dag.nodes:
                raise NodeExecutionError(
                    f"Edge target '{target}' is not a defined node in the DAG."
                )
            if parents[target].issubset(executed) and target not in ready:
                ready.append(target)
        ready.sort()
