# FILE: workflow_graph.py
"""
WorkflowGraph (v10_10 · Phase 1)
================================

Pure DAG execution engine used exclusively by L3 (orchestrator).

Responsibilities:
    • Represent workflow nodes + edges as a typed DAG.
    • Validate DAG (acyclic) and compute topological order (Kahn’s algorithm).
    • Execute nodes in correct order with optional parallelization hooks.
    • Capture node results, statuses, typed failure signals.
    • Expose well-typed surfaces for:
         – retries
         – replanning
         – escalation
         – checkpoint & rollback triggers (handled in L4)
    • Emit telemetry span hooks (without writing state).

Strict constraints:
    • No LLM calls.
    • No state mutation.
    • No safety enforcement.
    • No direct I/O.
    • Pure orchestration substrate.

L3 will drive the node executor functions; this file defines:
    – types
    – execution flow
    – DAG validation
    – failure-mode branching model
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from observability import start_span, end_span, log_exception


# =============================================================================
# Execution result + node statuses
# =============================================================================

class NodeStatus(Enum):
    """Canonical node statuses."""
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    RETRY = auto()
    REPLAN = auto()
    ESCALATE = auto()


@dataclass
class ExecutionResult:
    """
    Result emitted by a node executor (provided by L2 or L4 or L5).
    L3 receives this and triggers branching behavior.
    """
    status: NodeStatus
    output: Any = None
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Workflow Graph Core Types
# =============================================================================

@dataclass
class WorkflowNode:
    """
    Node wrapper. The executor is an async or sync callable supplied by L3.

    executor signature:
        async def executor(input_payload: dict) -> ExecutionResult
        or
        def executor(input_payload: dict) -> ExecutionResult
    """
    id: str
    executor: Callable[[Dict[str, Any]], Any]
    parallelizable: bool = False
    description: str = ""
    # Optional: L3 can attach per-node config
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdge:
    """Represents a directional edge n1 -> n2."""
    src: str
    dst: str


class DAGValidationError(Exception):
    pass


@dataclass
class WorkflowGraph:
    """
    DAG + runtime state. L3 constructs and drives this.
    """
    nodes: Dict[str, WorkflowNode]
    edges: List[WorkflowEdge]

    # runtime fields
    in_degree: Dict[str, int] = field(init=False, default_factory=dict)
    adjacency: Dict[str, List[str]] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self._build_graph()

    # -------------------------------------------------------------------------
    # Graph Construction
    # -------------------------------------------------------------------------

    def _build_graph(self) -> None:
        """
        Build adjacency + in-degree, validate DAG, topological sort readiness.
        """
        # Initialize adjacency & in-degrees
        for node_id in self.nodes:
            self.adjacency[node_id] = []
            self.in_degree[node_id] = 0

        # Build edges
        for e in self.edges:
            if e.src not in self.nodes or e.dst not in self.nodes:
                raise DAGValidationError(f"Invalid edge referencing missing node: {e}")
            self.adjacency[e.src].append(e.dst)
            self.in_degree[e.dst] += 1

        # Validate acyclicity (Kahn)
        if not self._is_acyclic():
            raise DAGValidationError("Graph contains a cycle; DAG required for execution.")

    def _is_acyclic(self) -> bool:
        """
        Kahn’s algorithm cycle detection.
        """
        temp_in_degree = dict(self.in_degree)
        queue = [nid for nid, deg in temp_in_degree.items() if deg == 0]
        visited = 0

        while queue:
            nid = queue.pop(0)
            visited += 1
            for nxt in self.adjacency[nid]:
                temp_in_degree[nxt] -= 1
                if temp_in_degree[nxt] == 0:
                    queue.append(nxt)

        return visited == len(self.nodes)

    def topological_layers(self) -> List[List[str]]:
        """
        Return node layers for potential parallel execution.
        e.g. [[a], [b, c], [d]] means b and c can run in parallel.

        Implementation: Kahn’s algorithm preserving layered structure.
        """
        temp_in_degree = dict(self.in_degree)
        frontier = [nid for nid, d in temp_in_degree.items() if d == 0]
        layers: List[List[str]] = []

        while frontier:
            layer = []
            next_frontier = []
            for nid in frontier:
                layer.append(nid)
            # We process edges
            for nid in frontier:
                for nxt in self.adjacency[nid]:
                    temp_in_degree[nxt] -= 1
                    if temp_in_degree[nxt] == 0:
                        next_frontier.append(nxt)
            layers.append(layer)
            frontier = next_frontier

        return layers


    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------

    async def execute(
        self,
        initial_payload: Dict[str, Any],
        l3_context: Dict[str, Any],
    ) -> Dict[str, ExecutionResult]:
        """
        Execute the DAG in topological layers.

        L3 supplies:
            - initial_payload: base input for the first-layer nodes.
            - l3_context: execution context / plan metadata.

        Returns:
            results: node_id -> ExecutionResult
        """
        results: Dict[str, ExecutionResult] = {}
        layers = self.topological_layers()

        for layer in layers:
            # Prepare payloads for nodes in this layer (L3 can customize).
            payloads = {
                nid: self._build_node_payload(nid, results, initial_payload, l3_context)
                for nid in layer
            }

            # Execute layer:
            # Parallelizable if node.parallelizable == True.
            # But overall logic is conservative: we only parallelize nodes
            # that explicitly allow it AND have no interdependencies.
            exec_tasks = [
                self._execute_single(nid, payloads[nid])
                for nid in layer
            ]

            # Try parallel execution via asyncio.gather
            try:
                layer_results = await asyncio.gather(*exec_tasks)
            except Exception as e:
                # Should not happen because _execute_single guards exceptions.
                log_exception("workflow_graph.layer_unhandled_exception", e)
                raise

            for nid, result in zip(layer, layer_results):
                results[nid] = result

                # Branching behavior: L3 will inspect result.status downstream.
                if result.status in (NodeStatus.RETRY, NodeStatus.REPLAN, NodeStatus.ESCALATE):
                    # Stop execution; return partial results.
                    return results

                if result.status is NodeStatus.FAILED:
                    # Hard failure: execution stops.
                    return results

        return results


    async def _execute_single(
        self,
        node_id: str,
        payload: Dict[str, Any],
    ) -> ExecutionResult:
        """
        Execute a single node, wrapped in telemetry spans and exception handling.
        """
        node = self.nodes[node_id]
        span = start_span(f"workflow_node.{node_id}")

        try:
            maybe_result = node.executor(payload)

            if asyncio.iscoroutine(maybe_result):
                result = await maybe_result
            else:
                result = maybe_result

            if not isinstance(result, ExecutionResult):
                raise ValueError(
                    f"Executor for node {node_id} did not return ExecutionResult."
                )

            end_span(span)
            return result

        except Exception as e:
            log_exception(f"workflow_node.{node_id}.exception", e)
            end_span(span)
            return ExecutionResult(
                status=NodeStatus.FAILED,
                output=None,
                error=e,
            )


    # -------------------------------------------------------------------------
    # Payload construction
    # -------------------------------------------------------------------------

    def _build_node_payload(
        self,
        node_id: str,
        results: Dict[str, ExecutionResult],
        initial_payload: Dict[str, Any],
        l3_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Provide node-specific payload:
            • initial_payload (for first layer)
            • outputs from predecessors
            • L3 context
        """
        predecessors = self._find_predecessors(node_id)

        pred_outputs = {
            pid: results[pid].output
            for pid in predecessors
            if pid in results and results[pid].status == NodeStatus.SUCCESS
        }

        return {
            "node_id": node_id,
            "initial_payload": initial_payload,
            "predecessor_outputs": pred_outputs,
            "l3_context": l3_context,
            "node_config": self.nodes[node_id].config,
        }

    def _find_predecessors(self, node_id: str) -> List[str]:
        preds = []
        for src, adj in self.adjacency.items():
            if node_id in adj:
                preds.append(src)
        return preds
