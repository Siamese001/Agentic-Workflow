from __future__ import annotations
"""
Unit Tests for Proactive Scheduling and Predictive Handoff

Tests L4.5 autonomy enhancements:
- ProactiveScheduler
- PredictiveHandoff
- CapabilityMonitorAgent
- ProactiveAgent
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from apps_rg.resume_engine.autonomous.context import ResumeEngineContext
from apps_rg.resume_engine.autonomous.proactive import (
    CapabilityMonitorAgent,
    CapabilityProfile,
    HandoffReason,
    PredictiveHandoff,
    ProactiveAgent,
    ProactiveScheduler,
    TaskPriority,
)


@pytest.fixture
def ctx():
    """Create a fresh context."""
    return ResumeEngineContext()


@pytest.fixture
def valid_resume():
    """Create a valid resume."""
    return {
        "name": "John Doe",
        "summary": "Experienced developer",
        "skills": ["Python", "JavaScript"],
        "experience": [{"title": "Developer", "company": "Tech Corp"}],
    }


class TestTaskPriority:
    """Tests for TaskPriority enum."""

    def test_priority_values(self):
        """Test priority values exist."""
        assert TaskPriority.CRITICAL.value == "critical"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.MEDIUM.value == "medium"
        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.BACKGROUND.value == "background"


class TestHandoffReason:
    """Tests for HandoffReason enum."""

    def test_reason_values(self):
        """Test reason values exist."""
        assert HandoffReason.CAPABILITY_LIMIT.value == "capability_limit"
        assert HandoffReason.CONFIDENCE_LOW.value == "confidence_low"
        assert HandoffReason.HIGH_RISK.value == "high_risk"


class TestProactiveScheduler:
    """Tests for ProactiveScheduler."""

    def test_init(self, ctx):
        """Test scheduler initialization."""
        scheduler = ProactiveScheduler(ctx)

        assert scheduler.ctx == ctx
        assert len(scheduler._tasks) == 0

    def test_identify_tasks_with_quality_signal(self, ctx):
        """Test Task identification with quality signal."""
        ctx.add_signal("QUALITY_ISSUE")
        scheduler = ProactiveScheduler(ctx)

        tasks = scheduler.identify_tasks()

        assert len(tasks) >= 1
        assert any(t.name == "Quality Remediation" for t in tasks)

    def test_identify_tasks_with_balance_signal(self, ctx):
        """Test Task identification with balance signal."""
        ctx.add_signal("BALANCE_ISSUE")
        scheduler = ProactiveScheduler(ctx)

        tasks = scheduler.identify_tasks()

        assert len(tasks) >= 1
        assert any(t.name == "Section Rebalancing" for t in tasks)

    def test_identify_tasks_missing_summary(self, ctx):
        """Test Task identification for Missing summary."""
        ctx.current_resume = {"name": "John", "skills": []}
        scheduler = ProactiveScheduler(ctx)

        tasks = scheduler.identify_tasks()

        assert any(t.name == "Generate Summary" for t in tasks)

    def test_get_pending_tasks_sorted(self, ctx):
        """Test pending tasks are sorted by priority."""
        scheduler = ProactiveScheduler(ctx)

        # Add tasks with different priorities
        ctx.add_signal("QUALITY_ISSUE")  # HIGH
        ctx.add_signal("BALANCE_ISSUE")  # MEDIUM

        scheduler.identify_tasks()
        pending = scheduler.get_pending_tasks()

        # Higher priority should come first
        if len(pending) >= 2:
            assert pending[0].priority.value in ["critical", "high"]

    def test_mark_executed(self, ctx):
        """Test marking Task as executed."""
        ctx.add_signal("QUALITY_ISSUE")
        scheduler = ProactiveScheduler(ctx)

        tasks = scheduler.identify_tasks()
        task_id = tasks[0].task_id

        scheduler.mark_executed(task_id, "completed")

        assert tasks[0].executed is True
        assert tasks[0].result == "completed"

    def test_get_auto_executable_tasks(self, ctx):
        """Test getting auto-executable tasks."""
        ctx.add_signal("QUALITY_ISSUE")
        scheduler = ProactiveScheduler(ctx)

        scheduler.identify_tasks()
        auto_tasks = scheduler.get_auto_executable_tasks()

        assert all(t.auto_execute for t in auto_tasks)
        assert all(not t.requires_approval for t in auto_tasks)


class TestPredictiveHandoff:
    """Tests for PredictiveHandoff."""

    def test_init(self, ctx):
        """Test handoff initialization."""
        handoff = PredictiveHandoff(ctx)

        assert handoff.ctx == ctx
        assert len(handoff._handoff_requests) == 0

    def test_register_capability(self, ctx):
        """Test registering capability profile."""
        handoff = PredictiveHandoff(ctx)

        profile = CapabilityProfile(
            agent_name="TestAgent",
            supported_tasks=["task1", "task2"],
            confidence_threshold=0.7,
            max_complexity=5,
            known_limitations=["complex_math"],
        )

        handoff.register_capability(profile)

        assert "TestAgent" in handoff._capability_profiles

    def test_predict_handoff_complexity_exceeded(self, ctx):
        """Test handoff prediction when complexity exceeded."""
        handoff = PredictiveHandoff(ctx)

        profile = CapabilityProfile(
            agent_name="TestAgent",
            supported_tasks=[],
            confidence_threshold=0.7,
            max_complexity=5,
            known_limitations=[],
        )
        handoff.register_capability(profile)

        request = handoff.predict_handoff_need(
            agent_name="TestAgent",
            TaskComplexity=10,  # Exceeds max of 5
            confidence=0.8,
        )

        assert request is not None
        assert request.reason == HandoffReason.CAPABILITY_LIMIT

    def test_predict_handoff_low_confidence(self, ctx):
        """Test handoff prediction when confidence low."""
        handoff = PredictiveHandoff(ctx)

        profile = CapabilityProfile(
            agent_name="TestAgent",
            supported_tasks=[],
            confidence_threshold=0.7,
            max_complexity=10,
            known_limitations=[],
        )
        handoff.register_capability(profile)

        request = handoff.predict_handoff_need(
            agent_name="TestAgent",
            TaskComplexity=5,
            confidence=0.5,  # Below threshold of 0.7
        )

        assert request is not None
        assert request.reason == HandoffReason.CONFIDENCE_LOW

    def test_predict_handoff_high_risk_signal(self, ctx):
        """Test handoff prediction with high-risk signal."""
        ctx.add_signal("CRITICAL_ERROR")
        handoff = PredictiveHandoff(ctx)

        request = handoff.predict_handoff_need(
            agent_name="TestAgent",
            TaskComplexity=1,
            confidence=0.9,
        )

        assert request is not None
        assert request.reason == HandoffReason.HIGH_RISK

    def test_no_handoff_needed(self, ctx):
        """Test no handoff when everything is fine."""
        handoff = PredictiveHandoff(ctx)

        profile = CapabilityProfile(
            agent_name="TestAgent",
            supported_tasks=[],
            confidence_threshold=0.7,
            max_complexity=10,
            known_limitations=[],
        )
        handoff.register_capability(profile)

        request = handoff.predict_handoff_need(
            agent_name="TestAgent",
            TaskComplexity=5,
            confidence=0.9,
        )

        assert request is None

    def test_suggested_actions(self, ctx):
        """Test suggested actions are provided."""
        handoff = PredictiveHandoff(ctx)

        profile = CapabilityProfile(
            agent_name="TestAgent",
            supported_tasks=[],
            confidence_threshold=0.7,
            max_complexity=5,
            known_limitations=[],
        )
        handoff.register_capability(profile)

        request = handoff.predict_handoff_need(
            agent_name="TestAgent",
            TaskComplexity=10,
            confidence=0.8,
        )

        assert request is not None
        assert len(request.suggested_actions) > 0


class TestCapabilityMonitor:
    """Tests for CapabilityMonitorAgent."""

    def test_init(self, ctx):
        """Test monitor initialization."""
        monitor = CapabilityMonitorAgent(ctx)

        assert monitor.ctx == ctx
        assert len(monitor._execution_history) == 0

    def test_record_execution(self, ctx):
        """Test recording execution."""
        monitor = CapabilityMonitorAgent(ctx)

        monitor.record_execution(
            agent_name="TestAgent",
            TaskType="validation",
            success=True,
            duration_ms=100,
            complexity=3,
        )

        assert len(monitor._execution_history) == 1
        assert monitor._agent_stats["TestAgent"]["total_executions"] == 1

    def test_get_success_rate(self, ctx):
        """Test getting success rate."""
        monitor = CapabilityMonitorAgent(ctx)

        monitor.record_execution("TestAgent", "task1", True, 100)
        monitor.record_execution("TestAgent", "task2", True, 100)
        monitor.record_execution("TestAgent", "task3", False, 100)

        rate = monitor.get_success_rate("TestAgent")

        assert abs(rate - 0.67) < 0.1

    def test_get_capability_profile(self, ctx):
        """Test generating capability profile."""
        monitor = CapabilityMonitorAgent(ctx)

        monitor.record_execution("TestAgent", "task1", True, 100, complexity=3)
        monitor.record_execution("TestAgent", "task2", True, 100, complexity=5)

        profile = monitor.get_capability_profile("TestAgent")

        assert profile.agent_name == "TestAgent"
        assert profile.max_complexity == 5
        assert "task1" in profile.supported_tasks
        assert "task2" in profile.supported_tasks

    def test_get_all_stats(self, ctx):
        """Test getting all stats."""
        monitor = CapabilityMonitorAgent(ctx)

        monitor.record_execution("Agent1", "Task", True, 100)
        monitor.record_execution("Agent2", "Task", True, 100)

        stats = monitor.get_all_stats()

        assert "Agent1" in stats
        assert "Agent2" in stats


class TestProactiveAgent:
    """Tests for ProactiveAgent."""

    @pytest.mark.asyncio
    async def test_execute(self, ctx):
        """Test agent execution."""
        ctx.add_signal("QUALITY_ISSUE")
        agent = ProactiveAgent(ctx)

        await agent.execute()

        assert ctx.results.get("ProactiveAgent") is not None
        assert ctx.results["ProactiveAgent"]["passed"] is True

    @pytest.mark.asyncio
    async def test_execute_with_handoff(self, ctx):
        """Test agent execution with handoff Recommendation."""
        ctx.add_signal("CRITICAL_ERROR")
        agent = ProactiveAgent(ctx)

        await agent.execute()

        assert ctx.has_signal("HANDOFF_RECOMMENDED")

    @pytest.mark.asyncio
    async def test_auto_execute_tasks(self, ctx, valid_resume):
        """Test auto-execution of tasks."""
        ctx.current_resume = {"name": "John"}  # Missing summary and skills
        agent = ProactiveAgent(ctx)

        await agent.execute()

        # Should have executed some tasks
        result = ctx.results.get("ProactiveAgent", {})
        assert "Executed" in result.get("details", "")


class TestIntegration:
    """Integration tests for proactive components."""

    @pytest.mark.asyncio
    async def test_full_proactive_workflow(self, ctx):
        """Test full proactive workflow."""
        # Setup context with issues
        ctx.current_resume = {"name": "John"}
        ctx.add_signal("QUALITY_ISSUE")

        # Create components
        scheduler = ProactiveScheduler(ctx)
        handoff = PredictiveHandoff(ctx)
        monitor = CapabilityMonitorAgent(ctx)

        # Register capability
        profile = CapabilityProfile(
            agent_name="ProactiveAgent",
            supported_tasks=["validation", "generation"],
            confidence_threshold=0.7,
            max_complexity=10,
            known_limitations=[],
        )
        handoff.register_capability(profile)

        # Identify tasks
        tasks = scheduler.identify_tasks()
        assert len(tasks) >= 1

        # Check for handoff
        handoff_request = handoff.predict_handoff_need(
            agent_name="ProactiveAgent",
            TaskComplexity=len(tasks),
            confidence=0.8,
        )

        # Execute tasks
        for Task in scheduler.get_auto_executable_tasks():
            scheduler.mark_executed(Task.task_id)
            monitor.record_execution(
                agent_name="ProactiveAgent",
                TaskType=Task.name,
                success=True,
                duration_ms=100,
            )

        # Verify
        assert monitor.get_success_rate("ProactiveAgent") > 0


def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path = None):
    """Test file - operational stub only."""
    if _call_path is None:
        _call_path = set()
    agent_name = "TestProactive"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] Test file - operational stub only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
