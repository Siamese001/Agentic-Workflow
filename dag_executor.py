"""Deterministic DAG execution engine for control-flow orchestrators."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Set

from l3_orchestration import DAG
from errors_controlflow import NodeExecutionError
from node_result import NodeResult, NodeStatus


class DAGExecutor:
    """Deterministic executor for DAG nodes with retry logic."""

    def run(self, dag: DAG, initial_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        dag.validate()
        context: Dict[str, Any] = deepcopy(initial_context) if initial_context else {}

        parents = self._build_parents_map(dag)
        ready: List[str] = sorted([name for name, deps in parents.items() if not deps])
        executed: Set[str] = set()

        while ready:
            node_name = ready.pop(0)
            if node_name in executed:
                continue

            node = dag.nodes[node_name]
            result, attempted_nodes = self._execute_with_retries(node_name, node, context)

            if result.status is NodeStatus.SUCCESS:
                context.update(result.payload)
                if node.parallel:
                    context = self._execute_parallel_nodes(dag, node.parallel, context, executed)
                outgoing = self._determine_edges(dag, node, context)
            else:
                outgoing = [node.fallback_edge] if node.fallback_edge else []

            executed.update(attempted_nodes)
            executed.add(node_name)
            self._enqueue_targets(outgoing, dag, parents, executed, ready)

        return context

    def _execute_with_retries(
        self, node_name: str, node: Any, context: Dict[str, Any]
    ) -> tuple[NodeResult, Set[str]]:
        attempted: Set[str] = set()
        attempts = node.retries + 1
        last_result: NodeResult | None = None
        for _ in range(attempts):
            last_result = node.run(deepcopy(context))
            attempted.add(node_name)
            if last_result.status is NodeStatus.SUCCESS:
                return last_result, attempted
        assert last_result is not None
        return NodeResult(NodeStatus.FAILURE, last_result.payload), attempted

    def _determine_edges(self, dag: DAG, node: Any, context: Dict[str, Any]) -> List[str]:
        if node.condition:
            try:
                condition_result = bool(node.condition(context))
            except Exception:
                condition_result = False
            if condition_result:
                return node.conditional_edges.get("condition_true", [])
        return dag.edges.get(node.name, [])

    def _build_parents_map(self, dag: DAG) -> Dict[str, Set[str]]:
        parents: Dict[str, Set[str]] = {name: set() for name in dag.nodes}
        for source, targets in dag.edges.items():
            for target in targets:
                parents[target].add(source)
        for node in dag.nodes.values():
            for conditional_targets in node.conditional_edges.values():
                for target in conditional_targets:
                    parents[target].add(node.name)
        return parents

    def _enqueue_targets(
        self,
        targets: List[str],
        dag: DAG,
        parents: Dict[str, Set[str]],
        executed: Set[str],
        ready: List[str],
    ) -> None:
        for target in targets:
            if target not in dag.nodes:
                raise NodeExecutionError(
                    f"Edge target '{target}' is not a defined node in the DAG."
                )
            if parents.get(target, set()).issubset(executed) and target not in ready:
                ready.append(target)
        ready.sort()

    def _execute_parallel_nodes(
        self, dag: DAG, parallel_nodes: List[str], context: Dict[str, Any], executed: Set[str]
    ) -> Dict[str, Any]:
        merged = deepcopy(context)
        for child_name in sorted(parallel_nodes):
            if child_name not in dag.nodes:
                raise NodeExecutionError(
                    f"Parallel target '{child_name}' is not a defined node in the DAG."
                )
            child_node = dag.nodes[child_name]
            child_result, _ = self._execute_with_retries(child_name, child_node, merged)
            merged.update(child_result.payload)
            executed.add(child_name)
        return merged
