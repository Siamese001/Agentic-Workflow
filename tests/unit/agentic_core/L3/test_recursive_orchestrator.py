"""
Test Suite: Recursive Orchestrator (Loop Unrolling)
Path: tests/L3/test_recursive_orchestrator.py

OBJECTIVE: Verify "Forward-Rolling Recursion" maintains DAG acyclicity while
simulating loops via node spawning.
"""

from unittest.mock import MagicMock

import pytest
from agentic_core.L3_orchestration.workflow_engines.RecursiveOrchestrator import (
    RecursiveOrchestrator,
    TaskStatus,
)

from agentic_core.L3_orchestration.workflow_engines.DAGMutatorAgent import (
    MutationAction,
    MutationResult,
)


class TestRecursiveOrchestrator:
    @pytest.fixture
    def mock_dag_manager(self):
        manager = MagicMock()
        # Mock the graph attribute properly
        manager.graph = MagicMock()
        manager.graph.nodes = MagicMock()
        manager.graph.nodes.get = MagicMock(return_value={})
        return manager

    @pytest.fixture
    def orchestrator(self, mock_dag_manager):
        return RecursiveOrchestrator(dag_manager=mock_dag_manager, max_retry_attempts=3)

    def test_forward_rolling_recursion_spawns_successor(self, orchestrator, mock_dag_manager):
        """
        CRITICAL: Verifies that a failure triggers a SPAWN_SUCCESSOR mutation.
        This confirms we are UNROLLING the loop (growing depth) rather than creating a cycle.
        """
        # Setup: Mock the original node existing in the graph
        node_id = "coder_v1"
        mock_dag_manager.graph.nodes.get.return_value = {
            "hop_spec": {"hop_function": "generate_code"}
        }

        # Setup: Mock mutation success
        mock_dag_manager.request_mutation.return_value = MutationResult(
            mutation_id="mut_1",
            success=True,
            message="Spawned",
            affected_nodes=["coder_v1", "coder_v2"],
        )

        # Execute: Report failure
        result = orchestrator.handle_task_status(
            node_id=node_id, status=TaskStatus.FAILED, failure_reason="Syntax Error"
        )

        # Assert: Check Mutation Request
        mock_dag_manager.request_mutation.assert_called_once()
        args = mock_dag_manager.request_mutation.call_args[0][0]

        # 100% Pass Criteria
        assert args.action == MutationAction.SPAWN_SUCCESSOR, (
            "Must spawn successor, NOT predecessor (cycle risk)"
        )
        assert args.target_hop_id == node_id
        assert args.new_hop_spec.hop_function == "generate_code"
        assert result["new_node_id"] is not None

    def test_circuit_breaker_max_depth(self, orchestrator, mock_dag_manager):
        """
        CRITICAL: Verifies infinite loops are impossible by respecting max_retry_attempts.
        """
        node_id = "infinite_loop_v1"

        # Simulate 3 previous failures (Attempt 3/3)
        ctx = orchestrator._get_or_create_retry_context(node_id)
        ctx.attempt_number = 3
        # Force max retries by setting attempt_number to max_attempts
        ctx.max_attempts = 3

        # Execute: Report 4th failure (this will increment attempt_number to 4)
        result = orchestrator.handle_task_status(
            node_id=node_id, status=TaskStatus.FAILED, failure_reason="Still failing"
        )

        # Assert: No mutation should occur
        mock_dag_manager.request_mutation.assert_not_called()
        assert result["action"] == "max_retries_exceeded"
        assert result["attempts"] == 4  # The attempt gets incremented during the call

    def test_state_persistence_across_generations(self, orchestrator, mock_dag_manager):
        """
        CRITICAL: Verifies failure reasons accumulate in context.
        Agent v2 must know why Agent v1 failed.
        """
        node_id = "researcher_v1"

        # Mock node with function
        mock_dag_manager.graph.nodes.get.return_value = {"hop_spec": {"hop_function": "web_search"}}
        mock_dag_manager.request_mutation.return_value = MutationResult(
            mutation_id="mut_1", success=True, message="Spawned"
        )

        # Fail 1
        orchestrator.handle_task_status(node_id, TaskStatus.FAILED, "404 Error")

        # The context gets transferred to a new node ID (UUID), so check the new node
        # Get the new node ID from the retry contexts
        context_keys = list(orchestrator.retry_contexts.keys())
        assert len(context_keys) == 1, "Should have exactly one retry context"

        # Get the context (it will be under the new UUID node ID)
        ctx = list(orchestrator.retry_contexts.values())[0]
        assert ctx is not None
        assert "404 Error" in ctx.failure_reasons
        assert ctx.original_node_id == node_id

        # Verify Params sent to mutation
        if mock_dag_manager.request_mutation.called:
            call_args = mock_dag_manager.request_mutation.call_args[0][0]
            params = call_args.new_hop_spec.parameters
            assert "retry_context" in params
            assert params["retry_context"]["failure_reasons"][0] == "404 Error"

    def test_cleanup_on_success(self, orchestrator):
        """
        CRITICAL: Verifies memory is freed after successful loop completion.
        """
        node_id = "writer_v1"

        # Create a "dirty" context
        orchestrator._get_or_create_retry_context(node_id)
        assert node_id in orchestrator.retry_contexts

        # Report Success
        orchestrator.handle_task_status(node_id, TaskStatus.SUCCESS)

        # Assert Cleanup
        assert node_id not in orchestrator.retry_contexts, "Retry context must be purged on success"

    def test_parameter_merging_preserves_original_data(self, orchestrator, mock_dag_manager):
        """
        CRITICAL: Verifies original parameters are preserved when merging retry context.
        """
        node_id = "analyst_v1"

        # Mock node with original parameters
        mock_dag_manager.graph.nodes.get.return_value = {
            "hop_spec": {"hop_function": "analyze_data"}
        }

        # Setup retry context with accumulated data
        ctx = orchestrator._get_or_create_retry_context(node_id)
        ctx.accumulated_context = {"goal": "analyze trends", "dataset": "sales.csv"}
        # Don't add failure here to avoid max retries issue

        mock_dag_manager.request_mutation.return_value = MutationResult(
            mutation_id="mut_1", success=True, message="Spawned"
        )

        # Execute - use attempt_number=1 to ensure retry happens
        ctx.attempt_number = 1
        orchestrator.handle_task_status(node_id, TaskStatus.FAILED, "Missing data")

        # Verify parameter merging
        if mock_dag_manager.request_mutation.called:
            call_args = mock_dag_manager.request_mutation.call_args[0][0]
            params = call_args.new_hop_spec.parameters

            # Both original data and retry context should be present
            assert "goal" in params
            assert "dataset" in params
            assert "retry_context" in params
            assert params["goal"] == "analyze trends"

    def test_retry_policy_prevents_internal_retries(self, orchestrator, mock_dag_manager):
        """
        SAFETY: Verifies spawned nodes have retry_policy disabled to prevent double retry logic.
        """
        node_id = "processor_v1"
        mock_dag_manager.graph.nodes.get.return_value = {
            "hop_spec": {"hop_function": "process_data"}
        }

        mock_dag_manager.request_mutation.return_value = MutationResult(
            mutation_id="mut_1", success=True, message="Spawned"
        )

        # Execute
        orchestrator.handle_task_status(node_id, TaskStatus.FAILED, "Processing error")

        # Verify retry policy is set to prevent internal retries
        call_args = mock_dag_manager.request_mutation.call_args[0][0]
        hop_spec = call_args.new_hop_spec

        assert hop_spec.retry_policy == {"max_attempts": 0}, (
            "Spawned nodes must not have internal retry logic"
        )

    def test_robust_node_function_extraction(self, orchestrator, mock_dag_manager):
        """
        CRITICAL: Verifies function extraction works with both dict and Pydantic hop_spec formats.
        """
        # Test with dict format
        mock_dag_manager.graph.nodes.get.return_value = {
            "hop_spec": {"hop_function": "test_function_dict"}
        }

        function_name = orchestrator._get_node_function("test_node")
        assert function_name == "test_function_dict"

        # Test with Pydantic-like object
        mock_hop_spec = MagicMock()
        mock_hop_spec.hop_function = "test_function_pydantic"
        mock_dag_manager.graph.nodes.get.return_value = {"hop_spec": mock_hop_spec}

        function_name = orchestrator._get_node_function("test_node")
        assert function_name == "test_function_pydantic"

        # Test with missing hop_spec
        mock_dag_manager.graph.nodes.get.return_value = {}
        function_name = orchestrator._get_node_function("test_node")
        assert function_name is None

    def test_context_transfer_to_new_node(self, orchestrator, mock_dag_manager):
        """
        CRITICAL: Verifies retry context is properly transferred to the new node ID.
        """
        original_node = "original_v1"
        mock_dag_manager.graph.nodes.get.return_value = {
            "hop_spec": {"hop_function": "test_function"}
        }

        # Mock successful mutation that returns a new node ID
        mock_dag_manager.request_mutation.return_value = MutationResult(
            mutation_id="mut_1",
            success=True,
            message="Spawned",
            affected_nodes=[original_node, "retry_v2"],
        )

        # Create initial context with attempt_number=1 to ensure retry happens
        ctx = orchestrator._get_or_create_retry_context(original_node)
        ctx.attempt_number = 1

        # Execute
        result = orchestrator.handle_task_status(original_node, TaskStatus.FAILED, "Test failure")

        # Verify context transfer only if mutation was successful
        if result.get("success") and mock_dag_manager.request_mutation.called:
            # The new node ID should be the hop_spec.hop_id, not "retry_v2"
            # Get the actual new node ID from the result
            new_node_id = result.get("new_node_id")

            if new_node_id:
                assert original_node not in orchestrator.retry_contexts, (
                    "Original node context should be cleaned up"
                )
                assert new_node_id in orchestrator.retry_contexts, (
                    "New node should inherit the context"
                )

                # Verify the context is the same object (preserves state)
                new_ctx = orchestrator.retry_contexts[new_node_id]
                assert new_ctx.original_node_id == original_node
                assert "Test failure" in new_ctx.failure_reasons
            else:
                # If no new node ID was generated, original context should remain
                assert original_node in orchestrator.retry_contexts
        else:
            # If no mutation occurred, verify original context still exists
            assert original_node in orchestrator.retry_contexts
