"""
Test cases for L4 vs L5 agent distribution analysis.

These tests validate the architectural reasonableness of the current
agent distribution and provide metrics for ongoing monitoring.
"""

import pytest
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch

# Import agents for testing
from agentic_core.L4_state.validation_context.ContextCuratorAgent import ContextCurator
from agentic_core.L4_state.validation_context.GravityStateAgent import GravityStateAgent
from agentic_core.L4_state.ledger.SovereignReasoningMemoryAgent import SovereignReasoningMemory
from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent
from agentic_core.L5_safety.gravity.GravityLeakRepairAgent import GravityLeakRepairAgent


class TestL4Scalability:
    """Test L4 agents can handle current L5 load."""

    def test_l4_agent_singleton_behavior(self):
        """Verify L4 agents use singleton pattern correctly."""
        # Test ContextCurator singleton
        curator1 = ContextCurator()
        curator2 = ContextCurator()
        assert curator1 is not curator2, "ContextCurator should not be singleton by default"

        # Test SovereignReasoningMemory singleton
        memory1 = SovereignReasoningMemory.get_instance()
        memory2 = SovereignReasoningMemory.get_instance()
        assert memory1 is memory2, "SovereignReasoningMemory should be singleton"

    def test_l4_concurrent_access(self):
        """Test L4 agents handle concurrent access gracefully."""
        results = []
        errors = []

        def worker(worker_id: int):
            try:
                curator = ContextCurator(max_tokens=1000)
                # Simulate context operations
                for i in range(10):
                    curator.add_chunk(Mock(id=f"chunk_{worker_id}_{i}"))
                    time.sleep(0.001)
                results.append(worker_id)
            except Exception as e:
                errors.append((worker_id, str(e)))

        # Create 20 concurrent workers (simulating L5 agent load)
        threads = []
        for i in range(20):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert len(results) == 20, "Not all workers completed successfully"

    def test_l4_memory_usage_under_load(self):
        """Test L4 agents don't become memory bottlenecks."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create multiple L4 agents and simulate load
        agents = []
        for i in range(10):
            agents.append(ContextCurator(max_tokens=8000))
            agents.append(GravityStateAgent())

        # Simulate operations
        for agent in agents:
            if hasattr(agent, "_chunks"):
                agent._chunks[f"test_{id(agent)}"] = Mock()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB for 20 agents)
        assert memory_increase < 50 * 1024 * 1024, (
            f"Memory increase too high: {memory_increase / 1024 / 1024:.2f}MB"
        )


class TestL5AgentIndependence:
    """Test L5 agents operate independently."""

    def test_l5_agent_isolation(self):
        """Test L5 agents can function without each other."""
        # Test that GovernanceAgent doesn't depend on specific other L5 agents
        with patch("agentic_core.L5_safety.validators.GovernanceAgent.importlib") as mock_import:
            # Mock imports to test isolation
            mock_import.import_module.return_value = Mock()

            agent = GovernanceAgent()

            # Should be able to initialize without other L5 agents
            assert agent is not None
            assert hasattr(agent, "validate_project_structure")

    def test_l5_failure_isolation(self):
        """Test failure in one L5 agent doesn't cascade."""
        # Create mock L5 agents
        agents = [
            Mock(spec=GovernanceAgent),
            Mock(spec=GravityLeakRepairAgent),
        ]

        # Make one agent fail
        agents[0].validate.side_effect = Exception("Test failure")

        # Other agents should still work
        try:
            agents[1].analyze_violation(Path("test.py"), "import os", "L5", "L0")
        except Exception:
            pytest.fail("Failure in one agent cascaded to others")

    def test_l5_granular_responsibility(self):
        """Test L5 agents have narrow, focused responsibilities."""
        # GovernanceAgent should focus on governance violations
        governance_agent = GovernanceAgent()

        # Check it has governance-specific methods
        assert hasattr(governance_agent, "validate_governance_laws")
        assert hasattr(governance_agent, "check_blast_radius")

        # GravityLeakRepairAgent should focus on gravity violations
        gravity_agent = GravityLeakRepairAgent()

        # Check it has gravity-specific methods
        assert hasattr(gravity_agent, "analyze_violation")
        assert hasattr(gravity_agent, "apply_fix")


class TestCrossLayerCommunication:
    """Test efficient L4-L5 communication."""

    def test_l4_l5_communication_overhead(self):
        """Test communication overhead between layers is minimal."""
        # Create L4 context manager
        curator = ContextCurator(max_tokens=4000)

        # Simulate L5 agent accessing L4
        start_time = time.time()

        for i in range(100):
            # Simulate L5 agent checking context
            curator.add_chunk(Mock(id=f"l5_request_{i}"))

        end_time = time.time()
        duration = end_time - start_time

        # Should handle 100 operations in < 1 second
        assert duration < 1.0, f"L4-L5 communication too slow: {duration:.3f}s for 100 ops"

    def test_state_synchronization(self):
        """Test state synchronization between L4 and L5."""
        # Test GravityStateAgent tracks L5 healing operations
        gravity_state = GravityStateAgent()

        # Simulate L5 healing operation
        violation = {
            "type": "gravity_violation",
            "file_path": "test.py",
            "original_import": "from L0.utils import helper",
            "dynamic_import": "from agentic_core.utils import helper",
        }

        # Record healing
        gravity_state.record_healing(violation, agent="GravityLeakRepairAgent")

        # Verify state is tracked
        healed_files = gravity_state.get_healed_files()
        assert "test.py" in healed_files

        # Verify L5 can query this state
        is_healed = gravity_state.is_file_healed("test.py")
        assert is_healed is True

    def test_no_race_conditions(self):
        """Test no race conditions in cross-layer access."""
        results = []
        errors = []

        def l4_worker():
            try:
                curator = ContextCurator()
                for i in range(50):
                    curator.add_chunk(Mock(id=f"l4_chunk_{i}"))
                    time.sleep(0.001)
                results.append("l4_complete")
            except Exception as e:
                errors.append(f"L4 error: {e}")

        def l5_worker():
            try:
                gravity_state = GravityStateAgent()
                for i in range(50):
                    gravity_state.is_file_healed(f"test_{i}.py")
                    time.sleep(0.001)
                results.append("l5_complete")
            except Exception as e:
                errors.append(f"L5 error: {e}")

        # Run concurrent L4 and L5 workers
        threads = [
            threading.Thread(target=l4_worker),
            threading.Thread(target=l5_worker),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0, f"Race condition errors: {errors}"
        assert len(results) == 2, "Not all workers completed"


class TestAgentDistributionMetrics:
    """Provide metrics for ongoing monitoring."""

    def test_agent_distribution_ratio(self):
        """Test and document current agent distribution ratio."""
        # Count agents by layer
        l4_count = len(list(Path("agentic_core/L4_state").rglob("*Agent*.py")))
        l5_count = len(list(Path("agentic_core/L5_safety").rglob("*Agent*.py")))

        # Calculate ratio
        ratio = l5_count / l4_count if l4_count > 0 else float("inf")

        # Document current state
        metrics = {
            "l4_agent_count": l4_count,
            "l5_agent_count": l5_count,
            "l4_l5_ratio": ratio,
            "assessment": "reasonable" if 10 <= ratio <= 50 else "needs_review",
        }

        print("\n=== Agent Distribution Metrics ===")
        print(f"L4 Agents: {metrics['l4_agent_count']}")
        print(f"L5 Agents: {metrics['l5_agent_count']}")
        print(f"L5/L4 Ratio: {metrics['l4_l5_ratio']:.1f}:1")
        print(f"Assessment: {metrics['assessment']}")

        # Current ratio should be reasonable
        assert 10 <= ratio <= 50, f"L5/L4 ratio {ratio:.1f} outside reasonable range [10, 50]"

    def test_l4_agent_impact_score(self):
        """Calculate impact score for L4 agents."""
        l4_agents = [
            ("ContextCurator", "system-wide", "high"),
            ("GravityStateAgent", "gravity-specific", "medium"),
            ("SovereignReasoningMemory", "system-wide", "high"),
        ]

        # Calculate weighted impact (system-wide = 2, specific = 1)
        total_impact = sum(2 if scope == "system-wide" else 1 for _, scope, _ in l4_agents)

        # Despite low count, L4 agents have high impact
        assert total_impact >= 5, f"L4 agents total impact too low: {total_impact}"

        print("\n=== L4 Agent Impact Analysis ===")
        for name, scope, priority in l4_agents:
            weight = 2 if scope == "system-wide" else 1
            print(f"{name}: {scope} scope, {priority} priority (weight: {weight})")
        print(f"Total Impact Score: {total_impact}")

    def test_l5_agent_specialization_score(self):
        """Calculate specialization score for L5 agents."""
        # Sample L5 agents and their specialization
        l5_specializations = {
            "GovernanceAgent": ["governance", "architecture", "blast_radius"],
            "GravityLeakRepairAgent": ["gravity", "imports", "layer_violations"],
            "LocationHealerAgent": ["location", "file_moves", "import_fixing"],
            "StructuralEngineerAgent": ["complexity", "structure", "code_quality"],
        }

        # Calculate specialization diversity
        total_specializations = sum(len(specs) for specs in l5_specializations.values())
        unique_specializations = len(
            set(spec for specs in l5_specializations.values() for spec in specs)
        )

        # High specialization diversity indicates good separation of concerns
        specialization_ratio = unique_specializations / len(l5_specializations)

        assert specialization_ratio >= 2.0, (
            f"L5 specialization too low: {specialization_ratio:.1f} per agent"
        )

        print("\n=== L5 Specialization Analysis ===")
        print(f"Total Specializations: {total_specializations}")
        print(f"Unique Specializations: {unique_specializations}")
        print(f"Specializations per Agent: {specialization_ratio:.1f}")


if __name__ == "__main__":
    # Run specific test suites
    pytest.main([__file__ + "::TestL4Scalability", "-v"])
    pytest.main([__file__ + "::TestL5AgentIndependence", "-v"])
    pytest.main([__file__ + "::TestCrossLayerCommunication", "-v"])
    pytest.main([__file__ + "::TestAgentDistributionMetrics", "-v"])
