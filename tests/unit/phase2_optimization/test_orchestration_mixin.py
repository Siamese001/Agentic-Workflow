"""
Phase 2 Optimization Tests - Orchestration Mixin
Tests for shared orchestration workflow patterns.
"""

import pytest
from apps_shared.mixins.orchestration_mixin import (
    OrchestrationMixin,
    WorkflowStep,
    WorkflowStatus,
)


class MockAgent(OrchestrationMixin):
    """Mock agent for testing OrchestrationMixin."""

    def __init__(self):
        self.logs = []

    def log(self, message):
        self.logs.append(message)


class TestWorkflowStep:
    """Test WorkflowStep dataclass."""

    def test_workflow_step_creation(self):
        """Test creating WorkflowStep."""

        def test_func():
            return "result"

        step = WorkflowStep(name="test_step", func=test_func)

        assert step.name == "test_step"
        assert step.func == test_func
        assert step.status == WorkflowStatus.PENDING
        assert step.result is None
        assert step.error is None

    def test_workflow_step_with_args(self):
        """Test WorkflowStep with arguments."""

        def test_func(a, b, c=None):
            return a + b

        step = WorkflowStep(name="test", func=test_func, args=(1, 2), kwargs={"c": 3})

        assert step.args == (1, 2)
        assert step.kwargs == {"c": 3}


class TestOrchestrationMixin:
    """Test OrchestrationMixin functionality."""

    def test_execute_workflow_success(self):
        """Test successful workflow execution."""
        agent = MockAgent()

        def step1():
            return "result1"

        def step2():
            return "result2"

        steps = [WorkflowStep("step1", step1), WorkflowStep("step2", step2)]

        result = agent.execute_workflow(steps)

        assert result["status"] == "completed"
        assert len(result["steps"]) == 2
        assert len(result["errors"]) == 0
        assert steps[0].status == WorkflowStatus.COMPLETED
        assert steps[1].status == WorkflowStatus.COMPLETED

    def test_execute_workflow_with_failure(self):
        """Test workflow execution with failure."""
        agent = MockAgent()

        def step1():
            return "result1"

        def step2():
            raise ValueError("Step 2 failed")

        steps = [WorkflowStep("step1", step1), WorkflowStep("step2", step2)]

        result = agent.execute_workflow(steps, stop_on_failure=True)

        assert result["status"] == "failed"
        assert len(result["errors"]) == 1
        assert steps[0].status == WorkflowStatus.COMPLETED
        assert steps[1].status == WorkflowStatus.FAILED

    def test_execute_workflow_continue_on_failure(self):
        """Test workflow continuing after failure."""
        agent = MockAgent()

        def step1():
            raise ValueError("Step 1 failed")

        def step2():
            return "result2"

        steps = [WorkflowStep("step1", step1), WorkflowStep("step2", step2)]

        result = agent.execute_workflow(steps, stop_on_failure=False)

        assert result["status"] == "failed"
        assert len(result["steps"]) == 2
        assert steps[0].status == WorkflowStatus.FAILED
        assert steps[1].status == WorkflowStatus.COMPLETED

    def test_orchestrate_parallel_success(self):
        """Test parallel task orchestration."""
        agent = MockAgent()

        def task1():
            return "result1"

        def task2():
            return "result2"

        tasks = [("task1", task1, (), {}), ("task2", task2, (), {})]

        result = agent.orchestrate_parallel(tasks)

        assert result["status"] == "completed"
        assert len(result["tasks"]) == 2
        assert result["tasks"]["task1"]["status"] == "completed"
        assert result["tasks"]["task2"]["status"] == "completed"

    def test_orchestrate_parallel_with_failure(self):
        """Test parallel orchestration with failure."""
        agent = MockAgent()

        def task1():
            return "result1"

        def task2():
            raise ValueError("Task 2 failed")

        tasks = [("task1", task1, (), {}), ("task2", task2, (), {})]

        result = agent.orchestrate_parallel(tasks)

        assert result["status"] == "partial"
        assert len(result["errors"]) == 1
        assert result["tasks"]["task1"]["status"] == "completed"
        assert result["tasks"]["task2"]["status"] == "failed"

    def test_coordinate_agents_no_dependencies(self):
        """Test agent coordination without dependencies."""
        agent = MockAgent()

        def agent1():
            return "result1"

        def agent2():
            return "result2"

        agent_tasks = {"agent1": agent1, "agent2": agent2}

        result = agent.coordinate_agents(agent_tasks)

        assert len(result["completed"]) == 2
        assert "agent1" in result["completed"]
        assert "agent2" in result["completed"]

    def test_coordinate_agents_with_dependencies(self):
        """Test agent coordination with dependencies."""
        agent = MockAgent()
        execution_order = []

        def agent1():
            execution_order.append("agent1")
            return "result1"

        def agent2():
            execution_order.append("agent2")
            return "result2"

        agent_tasks = {"agent1": agent1, "agent2": agent2}
        dependencies = {"agent2": ["agent1"]}  # agent2 depends on agent1

        result = agent.coordinate_agents(agent_tasks, dependencies)

        assert len(result["completed"]) == 2
        assert execution_order == ["agent1", "agent2"]  # Correct order

    def test_coordinate_agents_with_failure(self):
        """Test agent coordination with failure."""
        agent = MockAgent()

        def agent1():
            raise ValueError("Agent 1 failed")

        def agent2():
            return "result2"

        agent_tasks = {"agent1": agent1, "agent2": agent2}

        result = agent.coordinate_agents(agent_tasks)

        assert len(result["errors"]) == 1
        assert len(result["completed"]) == 2  # Both processed

    def test_create_checkpoint(self):
        """Test checkpoint creation."""
        agent = MockAgent()
        state = {"key1": "value1", "key2": "value2"}

        agent.create_checkpoint(state, "checkpoint1")

        assert hasattr(agent, "_checkpoints")
        assert "checkpoint1" in agent._checkpoints
        assert agent._checkpoints["checkpoint1"] == state

    def test_restore_checkpoint(self):
        """Test checkpoint restoration."""
        agent = MockAgent()
        state = {"key1": "value1", "key2": "value2"}

        agent.create_checkpoint(state, "checkpoint1")
        restored = agent.restore_checkpoint("checkpoint1")

        assert restored == state

    def test_restore_nonexistent_checkpoint(self):
        """Test restoring nonexistent checkpoint."""
        agent = MockAgent()

        restored = agent.restore_checkpoint("nonexistent")

        assert restored is None

    def test_checkpoint_isolation(self):
        """Test that checkpoint creates copy of state."""
        agent = MockAgent()
        state = {"key1": "value1"}

        agent.create_checkpoint(state, "checkpoint1")
        state["key1"] = "modified"

        restored = agent.restore_checkpoint("checkpoint1")

        assert restored["key1"] == "value1"  # Original value preserved


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
