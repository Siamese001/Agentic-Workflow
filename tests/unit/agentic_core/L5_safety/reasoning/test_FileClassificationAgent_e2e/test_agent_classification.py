"""TC-AGENT-01 through TC-AGENT-05: AGENT Classification E2E Tests"""
import pytest
from pathlib import Path
import time


@pytest.mark.agent
class TestAgentClassification:
    """Test AGENT file type classification per spec."""

    def test_agent_pascal_case_detection(self, agent, repo_root):
        """TC-AGENT-01: Files with *Agent.py suffix in reasoning/ classified as AGENT."""
        # Test the classification agent itself
        target = repo_root / "agentic_core" / "L5_safety" / "reasoning" / "FileClassificationAgent.py"
        if target.exists():
            result = agent.classify_file(target)
            assert result == "AGENT", f"Expected AGENT, got {result}"

    def test_agent_inheritance_detection(self, agent, repo_root):
        """TC-AGENT-02: Files inheriting from *Agent base class classified as AGENT."""
        # Find files that inherit from Agent classes
        base_agents_dir = repo_root / "agentic_core" / "L5_safety" / "base_agents"
        if base_agents_dir.exists():
            for agent_file in base_agents_dir.glob("*.py"):
                result = agent.classify_file(agent_file)
                # Base agents should be AGENT or ORCHESTRATOR
                assert result in ["AGENT", "ORCHESTRATOR"], f"{agent_file}: Expected AGENT/ORCHESTRATOR, got {result}"

    def test_agent_reasoning_directory_placement(self, agent, repo_root):
        """TC-AGENT-03: AGENT files must be in reasoning/ directory."""
        reasoning_dir = repo_root / "agentic_core" / "L5_safety" / "reasoning"
        if reasoning_dir.exists():
            for agent_file in reasoning_dir.glob("*Agent.py"):
                result = agent.classify_file(agent_file)
                assert result in ["AGENT", "ORCHESTRATOR"], f"{agent_file}: Expected AGENT/ORCHESTRATOR, got {result}"

    def test_agent_class_structure(self, agent, repo_root):
        """TC-AGENT-04: AGENT files must contain a class definition."""
        target = repo_root / "agentic_core" / "L5_safety" / "reasoning" / "FileClassificationAgent.py"
        if target.exists():
            with open(target, 'r') as f:
                content = f.read()
            assert "class " in content, "AGENT file must contain a class definition"

    def test_agent_compliant_name_no_change(self, agent, repo_root):
        """TC-AGENT-05: Correctly named AGENT files need no renaming."""
        target = repo_root / "agentic_core" / "L5_safety" / "reasoning" / "FileClassificationAgent.py"
        if target.exists():
            result = agent.classify_file(target)
            compliant = agent.get_compliant_name(target, result)
            assert compliant is None, f"Correctly named file should not need rename: {compliant}"


@pytest.mark.agent
@pytest.mark.performance
class TestAgentPerformance:
    """Performance benchmarks for AGENT classification."""

    def test_agent_classification_performance(self, agent, repo_root):
        """TC-AGENT-PERF-01: AGENT classification should complete in <5ms."""
        target = repo_root / "agentic_core" / "L5_safety" / "reasoning" / "FileClassificationAgent.py"
        if not target.exists():
            pytest.skip("FileClassificationAgent.py not found")

        # Warmup
        _ = agent.classify_file(target)

        # Benchmark
        times = []
        for _ in range(10):
            start = time.perf_counter()
            result = agent.classify_file(target)
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # Assert performance target
        assert avg_time < 5, f"Average classification time {avg_time:.2f}ms exceeds 5ms target"
        assert max_time < 10, f"Max classification time {max_time:.2f}ms exceeds 10ms threshold"
