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
        parallel_children = self._collect_parallel_children(dag)
        ready: List[str] = sorted(
            [name for name, deps in parents.items() if not deps and name not in parallel_children]
        )
        executed: Set[str] = set()

        while ready:
            node_name = ready.pop(0)
            if node_name in executed:
                continue

            node = dag.nodes[node_name]
            result, context, node_trace = self._execute_node(node_name, node, context)
            trace[node_name] = node_trace
            executed.add(node_name)

            if result.status is NodeStatus.FAILURE:
                policy = getattr(node, "on_failure", "halt")
                if policy == "fallback":
                    outgoing = [node.fallback_edge] if node.fallback_edge else []
                    self._enqueue_targets(dag, outgoing, parents, executed, ready)
                    continue
                if policy == "continue":
                    outgoing = self._determine_outgoing_edges(
                        dag, node_name, node, result, context
                    )
                    self._enqueue_targets(dag, outgoing, parents, executed, ready)
                    continue
                raise NodeExecutionError(f"Node '{node_name}' failed execution.")

            if node.parallel:
                context = self._execute_parallel_nodes(
                    dag, node, context, trace, executed
                )

            outgoing = self._determine_outgoing_edges(dag, node_name, node, result, context)
            self._enqueue_targets(dag, outgoing, parents, executed, ready)

        return context

    def _should_retry(self, node: Any, attempts: int) -> bool:
        max_retries = getattr(node, "retries", 0) or 0
        return attempts <= max_retries

    def _deterministic_backoff(self, node: Any, attempts: int) -> None:
        # Deterministic placeholder for retry backoff; intentionally no sleep.
        _ = (self.backoff_strategy, attempts, getattr(node, "retry_backoff", 0.0), node.name)

    def _determine_outgoing_edges(
        self,
        dag: DAG,
        node_name: str,
        node: Any,
        result: NodeResult,
        context: Dict[str, Any],
    ) -> List[str]:
        if result.next_edges is not None:
            return result.next_edges
        if getattr(node, "condition", None):
            try:
                condition_result = node.condition(context)
            except Exception:
                condition_result = False
            if condition_result and node.conditional_edges is not None:
                if isinstance(node.conditional_edges, dict):
                    override = node.conditional_edges.get("condition_true")
                else:
                    override = node.conditional_edges
                if override is not None:
                    return override
        if node.conditional_edges and isinstance(node.conditional_edges, dict):
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

    def _collect_parallel_children(self, dag: DAG) -> Set[str]:
        parallel_children: Set[str] = set()
        for node in dag.nodes.values():
            if node.parallel:
                parallel_children.update(node.parallel)
        return parallel_children

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

    def _execute_node(
        self, node_name: str, node: Any, context: Dict[str, Any]
    ) -> tuple[NodeResult, Dict[str, Any], Dict[str, Any]]:
        node_trace: Dict[str, Any] = {
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

        context = {**context, **result.output}
        return result, context, node_trace

    def _execute_parallel_nodes(
        self,
        dag: DAG,
        node: Any,
        context: Dict[str, Any],
        trace: Dict[str, Any],
        executed: Set[str],
    ) -> Dict[str, Any]:
        parallel_bucket = context.setdefault("_parallel", {}).setdefault(node.name, {})

        for child_name in node.parallel or []:
            if child_name not in dag.nodes:
                raise NodeExecutionError(
                    f"Parallel target '{child_name}' is not a defined node in the DAG."
                )

            child_node = dag.nodes[child_name]
            child_result, context, child_trace = self._execute_node(
                child_name, child_node, context
            )
            trace[child_name] = child_trace
            executed.add(child_name)
            parallel_bucket[child_name] = {
                "status": child_result.status.value,
                "output": child_result.output,
            }

            if child_result.status is NodeStatus.FAILURE:
                policy = getattr(child_node, "on_failure", "halt")
                if policy == "halt":
                    raise NodeExecutionError(
                        f"Parallel node '{child_name}' failed execution."
                    )
                if policy == "fallback":
                    fallback_target = getattr(child_node, "fallback_edge", None)
                    if fallback_target:
                        if fallback_target not in dag.nodes:
                            raise NodeExecutionError(
                                f"Fallback target '{fallback_target}' is not defined in the DAG."
                            )
                        fb_node = dag.nodes[fallback_target]
                        fallback_result, context, fallback_trace = self._execute_node(
                            fallback_target, fb_node, context
                        )
                        trace[fallback_target] = fallback_trace
                        executed.add(fallback_target)
                        parallel_bucket[fallback_target] = {
                            "status": fallback_result.status.value,
                            "output": fallback_result.output,
                        }
                # continue policy simply proceeds

        return context
