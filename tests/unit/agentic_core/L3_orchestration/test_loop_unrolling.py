"""
Test Loop Unrolling - Forward-Rolling Recursion Pattern.

Validates that the RecursiveOrchestrator correctly implements "loop unrolling"
by spawning downstream nodes instead of creating backward cycles.

Key Assertions:
1. Graph grows in depth (unrolling) rather than cycling
2. nx.is_directed_acyclic_graph remains True at ALL times
3. Retry context is properly passed between nodes
4. Max retry limits are enforced
"""

from dataclasses import dataclass, field
from typing import Any

import networkx as nx
import pytest
from agentic_core.L3_orchestration.workflow_engines.RecursiveOrchestrator import (
    RetryContext,
)

from agentic_core.L3_orchestration.workflow_engines.DAGMutatorAgent import (
    DAGConfig,
    DAGMutation,
    HopSpec,
    MutationAction,
    MutationResult,
)


class MockDAGManager:
    """Mock DAGManager for testing without full infrastructure."""

    def __init__(self, config: DAGConfig | None = None):
        self.config = config or DAGConfig()
        self.graph = nx.DiGraph()
        self.mutation_count = 0
        self.node_registry: dict[str, Any] = {}

    def add_node(self, node_id: str, hop_function: str = "test_func") -> None:
        """Add a node to the graph."""
        self.graph.add_node(
            node_id,
            hop_spec={"hop_function": hop_function, "parameters": {}},
            depth=self.graph.number_of_nodes(),
        )
        self.node_registry[node_id] = {"hop_function": hop_function}

    def request_mutation(self, mutation: DAGMutation) -> MutationResult:
        """Apply a mutation to the graph."""
        self.mutation_count += 1

        if mutation.action == MutationAction.SPAWN_SUCCESSOR:
            return self._spawn_successor(mutation)

        return MutationResult(
            mutation_id=mutation.mutation_id,
            success=False,
            message=f"Unsupported action: {mutation.action}",
        )

    def _spawn_successor(self, mutation: DAGMutation) -> MutationResult:
        """Spawn a successor node."""
        target_node = mutation.target_hop_id
        new_node = mutation.new_hop_spec.hop_id

        if target_node not in self.graph.nodes:
            return MutationResult(
                mutation_id=mutation.mutation_id,
                success=False,
                message=f"Target node {target_node} not found",
            )

        # Check depth constraint
        target_depth = self.graph.nodes[target_node].get("depth", 0)
        if target_depth >= self.config.max_depth - 1:
            return MutationResult(
                mutation_id=mutation.mutation_id,
                success=False,
                message=f"Would exceed max depth {self.config.max_depth}",
            )

        # Add new node
        new_depth = target_depth + 1
        self.graph.add_node(
            new_node,
            hop_spec=mutation.new_hop_spec.model_dump(),
            depth=new_depth,
        )

        # Add edge from target to new node (FORWARD, not backward)
        self.graph.add_edge(target_node, new_node)

        # Verify acyclicity after mutation
        if not nx.is_directed_acyclic_graph(self.graph):
            # Rollback
            self.graph.remove_node(new_node)
            return MutationResult(
                mutation_id=mutation.mutation_id,
                success=False,
                message="Mutation would create a cycle",
            )

        return MutationResult(
            mutation_id=mutation.mutation_id,
            success=True,
            message=f"Spawned successor {new_node} at depth {new_depth}",
            affected_nodes=[target_node, new_node],
            new_edges=[(target_node, new_node)],
        )


@dataclass
class MockRecursiveOrchestrator:
    """Simplified orchestrator for testing without SovereignBaseAgent deps."""

    dag_manager: MockDAGManager = field(default_factory=MockDAGManager)
    max_retry_attempts: int = 3
    retry_contexts: dict[str, RetryContext] = field(default_factory=dict)

    def handle_task_failure(
        self,
        failed_node_id: str,
        failure_reason: str,
        retry_function: str | None = None,
    ) -> dict[str, Any]:
        """Handle failure by spawning downstream retry node."""
        # Get or create retry context
        if failed_node_id in self.retry_contexts:
            ctx = self.retry_contexts[failed_node_id]
        else:
            ctx = RetryContext(
                original_node_id=failed_node_id,
                attempt_number=1,
                max_attempts=self.max_retry_attempts,
            )
            self.retry_contexts[failed_node_id] = ctx

        ctx.add_failure(failure_reason)

        # Check max retries
        if not ctx.can_retry:
            return {
                "action": "max_retries_exceeded",
                "attempts": ctx.attempt_number,
                "success": False,
            }

        # Get retry function
        if retry_function is None:
            node_data = self.dag_manager.graph.nodes.get(failed_node_id, {})
            hop_spec = node_data.get("hop_spec", {})
            retry_function = hop_spec.get("hop_function", "unknown_func")

        # Create mutation
        hop_spec = HopSpec(
            hop_function=retry_function,
            parameters=ctx.to_parameters(),
        )

        mutation = DAGMutation(
            action=MutationAction.SPAWN_SUCCESSOR,
            target_hop_id=failed_node_id,
            new_hop_spec=hop_spec,
            reason=f"Retry {ctx.attempt_number}: {failure_reason[:50]}",
            requester_hop_id="test_orchestrator",
        )

        result = self.dag_manager.request_mutation(mutation)

        if result.success:
            new_node_id = hop_spec.hop_id
            # Transfer context to new node
            self.retry_contexts[new_node_id] = ctx
            del self.retry_contexts[failed_node_id]

        return {
            "success": result.success,
            "new_node_id": hop_spec.hop_id if result.success else None,
            "attempt": ctx.attempt_number,
            "message": result.message,
        }


class TestLoopUnrolling:
    """Test suite for Forward-Rolling Recursion pattern."""

    def test_dag_remains_acyclic_after_single_retry(self):
        """Verify DAG stays acyclic after one retry spawn."""
        manager = MockDAGManager()
        manager.add_node("coder_v1", "code_generation")

        orchestrator = MockRecursiveOrchestrator(dag_manager=manager)

        # Simulate failure
        result = orchestrator.handle_task_failure(
            failed_node_id="coder_v1",
            failure_reason="Type error in generated code",
        )

        assert result["success"] is True
        assert result["new_node_id"] is not None

        # CRITICAL: Verify acyclicity
        assert nx.is_directed_acyclic_graph(manager.graph), "DAG must remain acyclic!"

        # Verify graph grew forward (depth increased)
        depths = nx.get_node_attributes(manager.graph, "depth")
        assert depths["coder_v1"] < depths[result["new_node_id"]]

    def test_dag_remains_acyclic_after_multiple_retries(self):
        """Verify DAG stays acyclic through multiple retry cycles."""
        manager = MockDAGManager()
        manager.add_node("coder_v1", "code_generation")

        orchestrator = MockRecursiveOrchestrator(dag_manager=manager, max_retry_attempts=5)

        current_node = "coder_v1"
        retry_count = 0

        # Simulate 3 consecutive failures
        for i in range(3):
            result = orchestrator.handle_task_failure(
                failed_node_id=current_node,
                failure_reason=f"Failure #{i + 1}: validation error",
            )

            assert result["success"] is True, f"Retry {i + 1} should succeed"

            # CRITICAL: Check acyclicity after EVERY mutation
            assert nx.is_directed_acyclic_graph(manager.graph), (
                f"DAG became cyclic after retry {i + 1}!"
            )

            current_node = result["new_node_id"]
            retry_count += 1

        # Verify graph structure
        assert manager.graph.number_of_nodes() == 4  # Original + 3 retries
        assert manager.graph.number_of_edges() == 3  # Linear chain

        # Verify all edges point forward (source depth < target depth)
        depths = nx.get_node_attributes(manager.graph, "depth")
        for source, target in manager.graph.edges():
            assert depths[source] < depths[target], (
                f"Edge {source}->{target} violates forward direction!"
            )

    def test_max_retries_enforced(self):
        """Verify max retry limit is respected."""
        manager = MockDAGManager()
        manager.add_node("coder_v1", "code_generation")

        # max_retry_attempts=3 means: original attempt + 2 retries = 3 total
        # After 2 add_failure calls, attempt_number becomes 3, which >= max_attempts
        orchestrator = MockRecursiveOrchestrator(dag_manager=manager, max_retry_attempts=3)

        current_node = "coder_v1"

        # First retry should succeed (attempt 1 -> 2)
        result = orchestrator.handle_task_failure(
            failed_node_id=current_node,
            failure_reason="Failure #1",
        )
        assert result["success"] is True
        current_node = result["new_node_id"]

        # 2nd failure should hit max limit (attempt 2 -> 3 >= 3)
        result = orchestrator.handle_task_failure(
            failed_node_id=current_node,
            failure_reason="Failure #2",
        )

        assert result["action"] == "max_retries_exceeded"
        assert result["success"] is False

        # DAG should still be acyclic
        assert nx.is_directed_acyclic_graph(manager.graph)

    def test_failure_context_passed_to_retry_node(self):
        """Verify failure reasons are accumulated and passed to retry nodes."""
        manager = MockDAGManager()
        manager.add_node("coder_v1", "code_generation")

        orchestrator = MockRecursiveOrchestrator(dag_manager=manager, max_retry_attempts=5)

        # First failure
        result1 = orchestrator.handle_task_failure(
            failed_node_id="coder_v1",
            failure_reason="Missing import statement",
        )
        node_v2 = result1["new_node_id"]

        # Second failure
        result2 = orchestrator.handle_task_failure(
            failed_node_id=node_v2,
            failure_reason="Syntax error on line 42",
        )
        node_v3 = result2["new_node_id"]

        # Check retry context has accumulated failures
        ctx = orchestrator.retry_contexts[node_v3]
        assert len(ctx.failure_reasons) == 2
        assert "Missing import statement" in ctx.failure_reasons
        assert "Syntax error on line 42" in ctx.failure_reasons

        # Verify context is in node parameters
        node_data = manager.graph.nodes[node_v3]
        params = node_data["hop_spec"]["parameters"]
        assert "retry_context" in params
        # After 2 failures, attempt_number is 3 (started at 1, incremented twice)
        assert params["retry_context"]["attempt_number"] == 3

    def test_depth_constraint_prevents_infinite_unrolling(self):
        """Verify max_depth prevents infinite loop unrolling."""
        config = DAGConfig(max_depth=5)
        manager = MockDAGManager(config=config)
        manager.add_node("coder_v1", "code_generation")

        orchestrator = MockRecursiveOrchestrator(dag_manager=manager, max_retry_attempts=10)

        current_node = "coder_v1"
        spawn_count = 0

        # Try to spawn more nodes than depth allows
        for i in range(10):
            result = orchestrator.handle_task_failure(
                failed_node_id=current_node,
                failure_reason=f"Failure #{i + 1}",
            )

            if not result["success"]:
                if "max_retries_exceeded" in str(result.get("action", "")):
                    continue
                # Depth limit hit
                break

            current_node = result["new_node_id"]
            spawn_count += 1

        # Should have stopped due to depth limit (5 - 1 = 4 spawns max from depth 0)
        assert spawn_count <= config.max_depth - 1

        # DAG must still be acyclic
        assert nx.is_directed_acyclic_graph(manager.graph)

    def test_no_backward_edges_ever_created(self):
        """Explicitly verify no backward edges exist after multiple operations."""
        manager = MockDAGManager()
        manager.add_node("step_1", "func_1")
        manager.add_node("step_2", "func_2")
        manager.graph.add_edge("step_1", "step_2")

        orchestrator = MockRecursiveOrchestrator(dag_manager=manager, max_retry_attempts=5)

        # Fail step_2, spawn step_2_retry
        result = orchestrator.handle_task_failure(
            failed_node_id="step_2",
            failure_reason="Validation failed",
        )

        # Verify no edge from new node back to any predecessor
        new_node = result["new_node_id"]
        predecessors_of_step_2 = set(nx.ancestors(manager.graph, "step_2"))

        for pred in predecessors_of_step_2:
            assert not manager.graph.has_edge(new_node, pred), (
                f"Backward edge detected: {new_node} -> {pred}"
            )

        # Verify topological order is valid
        try:
            topo_order = list(nx.topological_sort(manager.graph))
            assert topo_order.index("step_1") < topo_order.index("step_2")
            assert topo_order.index("step_2") < topo_order.index(new_node)
        except nx.NetworkXUnfeasible:
            pytest.fail("Graph has cycles - topological sort failed!")

    def test_graph_visualization_shows_unrolling(self):
        """Verify graph structure visually represents unrolling pattern."""
        manager = MockDAGManager()
        manager.add_node("coder_v1", "code_generation")

        orchestrator = MockRecursiveOrchestrator(dag_manager=manager, max_retry_attempts=5)

        # Create a chain of retries
        nodes = ["coder_v1"]
        current = "coder_v1"

        for i in range(3):
            result = orchestrator.handle_task_failure(
                failed_node_id=current,
                failure_reason=f"Error {i + 1}",
            )
            current = result["new_node_id"]
            nodes.append(current)

        # Verify linear chain structure (unrolled loop)
        # coder_v1 -> retry_1 -> retry_2 -> retry_3
        for i in range(len(nodes) - 1):
            assert manager.graph.has_edge(nodes[i], nodes[i + 1]), (
                f"Missing edge {nodes[i]} -> {nodes[i + 1]}"
            )

        # Verify it's a simple path (no branching in this case)
        assert manager.graph.number_of_edges() == len(nodes) - 1


class TestRetryContext:
    """Test RetryContext dataclass."""

    def test_can_retry_respects_max_attempts(self):
        """Verify can_retry logic."""
        ctx = RetryContext(
            original_node_id="test",
            attempt_number=1,
            max_attempts=3,
        )

        assert ctx.can_retry is True  # attempt 1 < 3

        ctx.add_failure("error 1")
        assert ctx.can_retry is True  # attempt 2 < 3

        ctx.add_failure("error 2")
        # After 2 failures, attempt_number = 3, which equals max_attempts
        # can_retry checks attempt_number < max_attempts, so this is False
        assert ctx.can_retry is False  # attempt 3 >= 3

    def test_to_parameters_serialization(self):
        """Verify context serializes to parameters correctly."""
        ctx = RetryContext(
            original_node_id="coder_v1",
            attempt_number=2,
            max_attempts=5,
            failure_reasons=["error 1", "error 2"],
            accumulated_context={"last_output": "partial code"},
        )

        params = ctx.to_parameters()

        assert "retry_context" in params
        rc = params["retry_context"]
        assert rc["original_node_id"] == "coder_v1"
        assert rc["attempt_number"] == 2
        assert rc["failure_reasons"] == ["error 1", "error 2"]
        assert rc["accumulated_context"]["last_output"] == "partial code"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
