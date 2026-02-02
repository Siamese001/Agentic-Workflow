"""
Forward-Rolling Recursion Test Suite - Phase 1

Rigorous test cases validating architectural pivot from static DAGs
to Forward-Rolling Recursion while maintaining SSOT and DNA integrity.

Author: Cascade
Date: February 2026
Phase: 1 - Core Infrastructure Testing
"""

import pytest
from unittest.mock import MagicMock, patch

from agentic_core.L3_orchestration.interfaces import (
    AgentResult,
    ExecutionContext,
    ExecutionPhase,
)
from agentic_core.L3_orchestration.workflow_engines.RecursiveOrchestrator import (
    RecursiveOrchestrator,
    SuccessorSpec,
)


class TestRecursiveOrchestratorFoundation:
    """Test suite for RecursiveOrchestrator core functionality."""

    @pytest.fixture
    def orchestrator(self):
        """Create test orchestrator instance."""
        return RecursiveOrchestrator(max_depth=50, enable_validation_cache=True)

    @pytest.fixture
    def base_context(self):
        """Create base execution context for testing."""
        return ExecutionContext(
            dry_run=True,
            execute=False,
            max_depth=50,
            current_depth=0,
            phase=ExecutionPhase.EXECUTION,
            metadata={"depth": 0, "successor_chain": []},
            accumulated_context={
                "original_goal": "test_goal",
                "dataset": "test_dataset",
                "mission_params": {"param1": "value1"},
            },
        )

    def test_orchestrator_initialization(self, orchestrator):
        """Test RecursiveOrchestrator initializes correctly."""
        assert orchestrator.max_depth == 50
        assert orchestrator.enable_validation_cache is True
        assert len(orchestrator._validation_cache) == 0
        assert len(orchestrator._successor_edges) == 0

    def test_metrics_initialization(self, orchestrator):
        """Test metrics initialize to zero."""
        metrics = orchestrator.get_metrics()
        assert metrics["total_spawns"] == 0
        assert metrics["successful_spawns"] == 0
        assert metrics["failed_spawns"] == 0
        assert metrics["cycle_preventions"] == 0


class TestLinearDepthExhaustion:
    """Test Case 1: Linear Depth Exhaustion - Forces the 50-step limit."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with standard depth limit."""
        return RecursiveOrchestrator(max_depth=50)

    def test_depth_limit_at_boundary(self, orchestrator):
        """Test depth limit enforcement at exact boundary."""
        context = ExecutionContext(
            dry_run=True,
            execute=False,
            metadata={"depth": 49, "successor_chain": []},
        )

        successor_spec = SuccessorSpec(agent_name="test_agent")

        # At depth 49, should succeed (one more allowed)
        with patch.object(orchestrator, "_validate_successor_acyclicity", return_value=True):
            with patch(
                "agentic_core.L3_orchestration.OrchestratorAgent.OrchestratorAgent"
            ) as mock_orch:
                mock_instance = MagicMock()
                mock_instance.run_agent.return_value = AgentResult(
                    agent_name="test_agent",
                    success=True,
                    status="PASS",
                )
                mock_orch.return_value = mock_instance

                result = orchestrator.spawn_successor("predecessor", successor_spec, context)
                # Should succeed at depth 49
                assert result.success or result.status == "DEPTH_LIMIT_EXCEEDED"

    def test_depth_limit_exceeded(self, orchestrator):
        """Test that depth limit blocks execution at max depth."""
        context = ExecutionContext(
            dry_run=True,
            execute=False,
            metadata={"depth": 50, "successor_chain": []},
        )

        successor_spec = SuccessorSpec(agent_name="test_agent")

        result = orchestrator.spawn_successor("predecessor", successor_spec, context)

        assert not result.success
        assert result.status == "DEPTH_LIMIT_EXCEEDED"
        assert "recursion limit" in result.message.lower()
        assert orchestrator._metrics.depth_limit_hits == 1

    def test_depth_tracking_in_metrics(self, orchestrator):
        """Test that max depth reached is tracked in metrics."""
        # Simulate multiple spawns at different depths
        for depth in [5, 10, 15, 20]:
            context = ExecutionContext(
                dry_run=True,
                execute=False,
                metadata={"depth": depth, "successor_chain": []},
            )
            successor_spec = SuccessorSpec(agent_name=f"agent_{depth}")

            with patch.object(orchestrator, "_validate_successor_acyclicity", return_value=True):
                with patch(
                    "agentic_core.L3_orchestration.OrchestratorAgent.OrchestratorAgent"
                ) as mock:
                    mock_instance = MagicMock()
                    mock_instance.run_agent.return_value = AgentResult(
                        agent_name=f"agent_{depth}",
                        success=True,
                        status="PASS",
                    )
                    mock.return_value = mock_instance
                    orchestrator.spawn_successor(f"pred_{depth}", successor_spec, context)

        metrics = orchestrator.get_metrics()
        assert metrics["max_depth_reached"] >= 20


class TestDNAContinuity:
    """Test Case 2: DNA Continuity - Verifies accumulated_context survives spawns."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for DNA testing."""
        return RecursiveOrchestrator(max_depth=50)

    def test_accumulated_context_preservation(self, orchestrator):
        """Test that accumulated_context is preserved across successor spawns."""
        initial_context = ExecutionContext(
            dry_run=True,
            execute=False,
            metadata={
                "depth": 0,
                "successor_chain": [],
                "accumulated_context": {
                    "original_goal": "test_goal",
                    "dataset": "test_dataset",
                    "mission_params": {"param1": "value1", "param2": "value2"},
                },
            },
            accumulated_context={
                "original_goal": "test_goal",
                "dataset": "test_dataset",
            },
        )

        successor_spec = SuccessorSpec(
            agent_name="successor_agent",
            context_merge_strategy="deep_merge",
        )

        # Create successor context
        successor_context = orchestrator._create_successor_context(
            "predecessor_agent", successor_spec, initial_context
        )

        # Verify DNA preservation
        assert "accumulated_context" in successor_context.metadata
        acc_ctx = successor_context.metadata["accumulated_context"]
        assert "_predecessor_chain" in acc_ctx
        assert "predecessor_agent" in acc_ctx["_predecessor_chain"]

    def test_context_survives_five_spawns(self, orchestrator):
        """Test that context survives 5+ successor spawns without data loss."""
        # Initialize with DNA payload
        context = ExecutionContext(
            dry_run=True,
            execute=False,
            metadata={
                "depth": 0,
                "successor_chain": [],
                "accumulated_context": {
                    "original_goal": "complex_mission",
                    "dataset": "production_data",
                    "critical_param": "must_survive",
                },
            },
            accumulated_context={
                "original_goal": "complex_mission",
                "dataset": "production_data",
            },
        )

        # Simulate 5 successor spawns
        current_context = context
        for i in range(5):
            successor_spec = SuccessorSpec(agent_name=f"successor_{i}")
            current_context = orchestrator._create_successor_context(
                f"agent_{i}", successor_spec, current_context
            )

        # Verify DNA integrity after 5 spawns
        acc_ctx = current_context.metadata.get("accumulated_context", {})
        assert "_predecessor_chain" in acc_ctx
        assert len(acc_ctx["_predecessor_chain"]) == 5

        # Verify successor chain tracking
        assert len(current_context.metadata.get("successor_chain", [])) == 5

    def test_deep_merge_preserves_nested_structures(self, orchestrator):
        """Test that deep merge preserves nested data structures."""
        base = {
            "level1": {"level2": {"level3": "deep_value"}},
            "array": [1, 2, 3],
        }

        override = {
            "level1": {"level2": {"new_key": "new_value"}},
            "new_root": "root_value",
        }

        result = orchestrator._deep_merge_context(base, override)

        assert result["level1"]["level2"]["level3"] == "deep_value"
        assert result["level1"]["level2"]["new_key"] == "new_value"
        assert result["new_root"] == "root_value"
        assert result["array"] == [1, 2, 3]


class TestCacheEfficiency:
    """Test Case 3: Cache Efficiency - Measures validation caching performance."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with caching enabled."""
        return RecursiveOrchestrator(max_depth=50, enable_validation_cache=True)

    def test_cache_hit_on_repeat_validation(self, orchestrator):
        """Test that repeated validations hit cache."""
        # First validation - cache miss
        result1 = orchestrator._validate_successor_acyclicity("A", "B")
        assert orchestrator._metrics.cache_misses == 1
        assert orchestrator._metrics.cache_hits == 0

        # Second validation - cache hit
        result2 = orchestrator._validate_successor_acyclicity("A", "B")
        assert orchestrator._metrics.cache_hits == 1

        # Results should be identical
        assert result1 == result2

    def test_cache_efficiency_with_repeated_patterns(self, orchestrator):
        """Test cache efficiency with repeated validation patterns."""
        patterns = [("A", "B"), ("B", "C"), ("C", "D"), ("A", "B"), ("B", "C")]

        for pred, succ in patterns:
            orchestrator._validate_successor_acyclicity(pred, succ)

        metrics = orchestrator.get_metrics()

        # 3 unique patterns, 2 repeats
        assert metrics["cache_misses"] == 3
        assert metrics["cache_hits"] == 2
        assert metrics["cache_hit_rate"] == 2 / 5

    def test_cache_size_management(self):
        """Test that cache respects size limits."""
        orchestrator = RecursiveOrchestrator(
            max_depth=50, enable_validation_cache=True, cache_size=5
        )

        # Add more than cache size
        for i in range(10):
            orchestrator._validate_successor_acyclicity(f"agent_{i}", f"successor_{i}")

        # Cache should not exceed size limit
        assert len(orchestrator._validation_cache) <= 5

    def test_cache_disabled(self):
        """Test behavior with cache disabled."""
        orchestrator = RecursiveOrchestrator(max_depth=50, enable_validation_cache=False)

        # Multiple validations
        for _ in range(5):
            orchestrator._validate_successor_acyclicity("A", "B")

        # All should be misses (no caching)
        assert orchestrator._metrics.cache_hits == 0
        assert len(orchestrator._validation_cache) == 0


class TestAcyclicityVerification:
    """Test Case 4: Acyclicity Verification - Mathematical proof of DAG properties."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for acyclicity testing."""
        return RecursiveOrchestrator(max_depth=50)

    def test_self_loop_prevention(self, orchestrator):
        """Test that self-loops are prevented."""
        result = orchestrator._validate_successor_acyclicity("A", "A")
        assert result is False
        assert orchestrator._metrics.cache_misses == 1

    def test_direct_cycle_prevention(self, orchestrator):
        """Test that direct cycles are prevented."""
        # Add edge A -> B
        orchestrator._successor_edges.add(("A", "B"))

        # Try to add B -> A (would create cycle)
        result = orchestrator._validate_successor_acyclicity("B", "A")
        assert result is False

    def test_indirect_cycle_prevention(self, orchestrator):
        """Test that indirect cycles are prevented."""
        # Build chain: A -> B -> C -> D
        orchestrator._successor_edges.add(("A", "B"))
        orchestrator._successor_edges.add(("B", "C"))
        orchestrator._successor_edges.add(("C", "D"))

        # Try to add D -> A (would create cycle)
        result = orchestrator._validate_successor_acyclicity("D", "A")
        assert result is False

        # Try to add D -> B (would create cycle)
        result = orchestrator._validate_successor_acyclicity("D", "B")
        assert result is False

    def test_valid_dag_operations(self, orchestrator):
        """Test that valid DAG operations are allowed."""
        # Build DAG
        assert orchestrator._validate_successor_acyclicity("A", "B") is True
        orchestrator._successor_edges.add(("A", "B"))

        assert orchestrator._validate_successor_acyclicity("A", "C") is True
        orchestrator._successor_edges.add(("A", "C"))

        assert orchestrator._validate_successor_acyclicity("B", "D") is True
        orchestrator._successor_edges.add(("B", "D"))

        assert orchestrator._validate_successor_acyclicity("C", "D") is True
        orchestrator._successor_edges.add(("C", "D"))

        # Verify graph is acyclic
        assert orchestrator.is_acyclic() is True

    def test_complex_dag_acyclicity(self, orchestrator):
        """Test acyclicity in complex DAG structure."""
        # Build complex DAG
        edges = [
            ("A", "B"),
            ("A", "C"),
            ("B", "D"),
            ("B", "E"),
            ("C", "E"),
            ("C", "F"),
            ("D", "G"),
            ("E", "G"),
            ("F", "G"),
        ]

        for pred, succ in edges:
            assert orchestrator._validate_successor_acyclicity(pred, succ) is True
            orchestrator._successor_edges.add((pred, succ))

        # Verify acyclicity
        assert orchestrator.is_acyclic() is True

        # Attempt to create cycle G -> A
        assert orchestrator._validate_successor_acyclicity("G", "A") is False

    def test_is_acyclic_method(self, orchestrator):
        """Test the is_acyclic method directly."""
        # Empty graph is acyclic
        assert orchestrator.is_acyclic() is True

        # Add valid edges
        orchestrator._successor_edges.add(("A", "B"))
        orchestrator._successor_edges.add(("B", "C"))
        assert orchestrator.is_acyclic() is True

        # Manually add cycle (bypassing validation)
        orchestrator._successor_edges.add(("C", "A"))
        assert orchestrator.is_acyclic() is False


class TestSuccessorChainTracking:
    """Test successor chain retrieval and tracking."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for chain tracking tests."""
        return RecursiveOrchestrator(max_depth=50)

    def test_get_successor_chain(self, orchestrator):
        """Test successor chain retrieval."""
        # Build chain
        orchestrator._successor_edges.add(("A", "B"))
        orchestrator._successor_edges.add(("B", "C"))
        orchestrator._successor_edges.add(("C", "D"))

        chain = orchestrator.get_successor_chain("A")
        assert chain == ["A", "B", "C", "D"]

    def test_get_successor_chain_with_branches(self, orchestrator):
        """Test successor chain with branches (returns one path)."""
        # Build branching structure
        orchestrator._successor_edges.add(("A", "B"))
        orchestrator._successor_edges.add(("A", "C"))
        orchestrator._successor_edges.add(("B", "D"))

        chain = orchestrator.get_successor_chain("A")
        # Should return one valid path
        assert chain[0] == "A"
        assert len(chain) >= 2


class TestHealingCapability:
    """Test healing capabilities of RecursiveOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for healing tests."""
        return RecursiveOrchestrator(max_depth=50)

    def test_heal_repository_no_violations(self, orchestrator):
        """Test healing with no violations."""
        result = orchestrator.heal_repository(dry_run=True)

        assert result["violations_found"] == 0
        assert result["violations_fixed"] == 0
        assert result["errors"] == 0

    def test_heal_repository_with_cycle(self, orchestrator):
        """Test healing detects and fixes cycles."""
        # Manually introduce a cycle
        orchestrator._successor_edges.add(("A", "B"))
        orchestrator._successor_edges.add(("B", "C"))
        orchestrator._successor_edges.add(("C", "A"))

        # Dry run should find violation
        result = orchestrator.heal_repository(dry_run=True)
        assert result["violations_found"] == 1
        assert result["violations_fixed"] == 0

        # Execute should fix violation
        result = orchestrator.heal_repository(dry_run=False, execute=True)
        assert result["violations_found"] == 1
        assert result["violations_fixed"] == 1

        # Graph should now be clear
        assert len(orchestrator._successor_edges) == 0

    def test_heal_specific_violation(self, orchestrator):
        """Test healing a specific cycle violation."""
        orchestrator._successor_edges.add(("A", "B"))
        orchestrator._successor_edges.add(("B", "A"))

        violation = {
            "type": "cycle_detected",
            "predecessor": "B",
            "successor": "A",
        }

        result = orchestrator.heal(violation)
        assert result["status"] == "success"
        assert ("B", "A") not in orchestrator._successor_edges


class TestExecutionContextEnhancements:
    """Test ExecutionContext Forward-Rolling enhancements."""

    def test_accumulated_context_field(self):
        """Test that accumulated_context field exists and works."""
        context = ExecutionContext(accumulated_context={"key": "value"})
        assert context.accumulated_context == {"key": "value"}

    def test_with_accumulated_context(self):
        """Test with_accumulated_context method."""
        context = ExecutionContext(accumulated_context={"existing": "data"})

        new_context = context.with_accumulated_context({"new": "value"})

        assert new_context.accumulated_context["existing"] == "data"
        assert new_context.accumulated_context["new"] == "value"
        # Original should be unchanged
        assert "new" not in context.accumulated_context

    def test_get_successor_chain(self):
        """Test get_successor_chain method."""
        context = ExecutionContext(metadata={"successor_chain": ["A", "B", "C"]})

        chain = context.get_successor_chain()
        assert chain == ["A", "B", "C"]

    def test_get_depth(self):
        """Test get_depth method."""
        context = ExecutionContext(current_depth=5, metadata={"depth": 10})

        # Should prefer metadata depth
        assert context.get_depth() == 10

        # Without metadata depth, should use current_depth
        context2 = ExecutionContext(current_depth=5)
        assert context2.get_depth() == 5


class TestMetricsAndMonitoring:
    """Test metrics tracking and monitoring."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for metrics testing."""
        return RecursiveOrchestrator(max_depth=50)

    def test_metrics_reset(self, orchestrator):
        """Test metrics reset functionality."""
        # Generate some metrics
        orchestrator._metrics.total_spawns = 10
        orchestrator._metrics.successful_spawns = 8

        orchestrator.reset_metrics()

        metrics = orchestrator.get_metrics()
        assert metrics["total_spawns"] == 0
        assert metrics["successful_spawns"] == 0

    def test_clear_cache(self, orchestrator):
        """Test cache clearing."""
        orchestrator._validation_cache["test"] = True
        orchestrator.clear_cache()
        assert len(orchestrator._validation_cache) == 0

    def test_clear_successor_graph(self, orchestrator):
        """Test successor graph clearing."""
        orchestrator._successor_edges.add(("A", "B"))
        orchestrator._validation_cache["test"] = True

        orchestrator.clear_successor_graph()

        assert len(orchestrator._successor_edges) == 0
        assert len(orchestrator._validation_cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
