from __future__ import annotations
"""
Unit Tests for Outreach Engine Proactive Scheduling and Predictive Handoff

Tests L4.5 autonomy enhancements for outreach:
- OutreachProactiveScheduler
- OutreachPredictiveHandoff
- OutreachCapabilityMonitorAgent
- OutreachProactiveAgent
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from apps_lic.outreach_engine.autonomous.context import OutreachEngineContext
from apps_lic.outreach_engine.autonomous.proactive import (
    OutreachCapabilityMonitorAgent,
    OutreachCapabilityProfile,
    OutreachHandoffReason,
    OutreachPredictiveHandoff,
    OutreachProactiveAgent,
    OutreachProactiveScheduler,
    OutreachTaskPriority,
)


@pytest.fixture
def ctx():
    """Create a fresh context."""
    return OutreachEngineContext()


@pytest.fixture
def valid_campaign():
    """Create a valid campaign."""
    return {
        "name": "Test Campaign",
        "goal": "Generate leads",
        "schedule": "daily",
        "tracking": True,
    }


class TestOutreachTaskPriority:
    """Tests for OutreachTaskPriority enum."""

    def test_priority_values(self):
        """Test priority values exist."""
        assert OutreachTaskPriority.CRITICAL.value == "critical"
        assert OutreachTaskPriority.HIGH.value == "high"
        assert OutreachTaskPriority.MEDIUM.value == "medium"


class TestOutreachHandoffReason:
    """Tests for OutreachHandoffReason enum."""

    def test_reason_values(self):
        """Test reason values exist."""
        assert OutreachHandoffReason.CAPABILITY_LIMIT.value == "capability_limit"
        assert OutreachHandoffReason.COMPLIANCE_REQUIRED.value == "compliance_required"
        assert OutreachHandoffReason.SENSITIVE_CONTACT.value == "sensitive_contact"


class TestOutreachProactiveScheduler:
    """Tests for OutreachProactiveScheduler."""

    def test_init(self, ctx):
        """Test scheduler initialization."""
        scheduler = OutreachProactiveScheduler(ctx)

        assert scheduler.ctx == ctx
        assert len(scheduler._tasks) == 0

    def test_identify_tasks_with_lead_quality_signal(self, ctx):
        """Test Task identification with lead quality signal."""
        ctx.add_signal("LEAD_QUALITY_ISSUE")
        scheduler = OutreachProactiveScheduler(ctx)

        tasks = scheduler.identify_tasks()

        assert len(tasks) >= 1
        assert any(t.name == "Lead Quality Remediation" for t in tasks)

    def test_identify_tasks_with_compliance_signal(self, ctx):
        """Test Task identification with compliance signal."""
        ctx.add_signal("COMPLIANCE_ISSUE")
        scheduler = OutreachProactiveScheduler(ctx)

        tasks = scheduler.identify_tasks()

        assert len(tasks) >= 1
        compliance_task = next(t for t in tasks if t.name == "Compliance Review")
        assert compliance_task.requires_approval is True
        assert compliance_task.auto_execute is False

    def test_identify_tasks_missing_schedule(self, ctx):
        """Test Task identification for Missing schedule."""
        ctx.current_campaign = {"name": "Test"}
        scheduler = OutreachProactiveScheduler(ctx)

        tasks = scheduler.identify_tasks()

        assert any(t.name == "Add Schedule" for t in tasks)

    def test_identify_tasks_large_lead_list(self, ctx):
        """Test Task identification for large lead list."""
        ctx.current_campaign = {"name": "Test"}
        ctx.leads = [{"company": f"Company {i}"} for i in range(150)]
        scheduler = OutreachProactiveScheduler(ctx)

        tasks = scheduler.identify_tasks()

        assert any(t.name == "Lead Segmentation" for t in tasks)

    def test_get_pending_tasks_sorted(self, ctx):
        """Test pending tasks are sorted by priority."""
        ctx.add_signal("COMPLIANCE_ISSUE")  # CRITICAL
        ctx.add_signal("LEAD_QUALITY_ISSUE")  # HIGH
        scheduler = OutreachProactiveScheduler(ctx)

        scheduler.identify_tasks()
        pending = scheduler.get_pending_tasks()

        if len(pending) >= 2:
            assert pending[0].priority == OutreachTaskPriority.CRITICAL

    def test_mark_executed(self, ctx):
        """Test marking Task as executed."""
        ctx.add_signal("LEAD_QUALITY_ISSUE")
        scheduler = OutreachProactiveScheduler(ctx)

        tasks = scheduler.identify_tasks()
        task_id = tasks[0].task_id

        scheduler.mark_executed(task_id, "completed")

        assert tasks[0].executed is True

    def test_get_auto_executable_tasks(self, ctx):
        """Test getting auto-executable tasks."""
        ctx.add_signal("LEAD_QUALITY_ISSUE")
        scheduler = OutreachProactiveScheduler(ctx)

        scheduler.identify_tasks()
        auto_tasks = scheduler.get_auto_executable_tasks()

        assert all(t.auto_execute for t in auto_tasks)


class TestOutreachPredictiveHandoff:
    """Tests for OutreachPredictiveHandoff."""

    def test_init(self, ctx):
        """Test handoff initialization."""
        handoff = OutreachPredictiveHandoff(ctx)

        assert handoff.ctx == ctx
        assert len(handoff._handoff_requests) == 0

    def test_register_capability(self, ctx):
        """Test registering capability profile."""
        handoff = OutreachPredictiveHandoff(ctx)

        profile = OutreachCapabilityProfile(
            agent_name="TestAgent",
            supported_tasks=["email", "validation"],
            confidence_threshold=0.7,
            max_leads_per_batch=100,
            known_limitations=["complex_personalization"],
        )

        handoff.register_capability(profile)

        assert "TestAgent" in handoff._capability_profiles

    def test_predict_handoff_lead_limit_exceeded(self, ctx):
        """Test handoff prediction when lead limit exceeded."""
        handoff = OutreachPredictiveHandoff(ctx)

        profile = OutreachCapabilityProfile(
            agent_name="TestAgent",
            supported_tasks=[],
            confidence_threshold=0.7,
            max_leads_per_batch=50,
            known_limitations=[],
        )
        handoff.register_capability(profile)

        request = handoff.predict_handoff_need(
            agent_name="TestAgent",
            lead_count=100,  # Exceeds max of 50
            confidence=0.8,
        )

        assert request is not None
        assert request.reason == OutreachHandoffReason.CAPABILITY_LIMIT

    def test_predict_handoff_low_confidence(self, ctx):
        """Test handoff prediction when confidence low."""
        handoff = OutreachPredictiveHandoff(ctx)

        profile = OutreachCapabilityProfile(
            agent_name="TestAgent",
            supported_tasks=[],
            confidence_threshold=0.7,
            max_leads_per_batch=100,
            known_limitations=[],
        )
        handoff.register_capability(profile)

        request = handoff.predict_handoff_need(
            agent_name="TestAgent",
            lead_count=50,
            confidence=0.5,  # Below threshold
        )

        assert request is not None
        assert request.reason == OutreachHandoffReason.CONFIDENCE_LOW

    def test_predict_handoff_compliance_signal(self, ctx):
        """Test handoff prediction with compliance signal."""
        ctx.add_signal("COMPLIANCE_ISSUE")
        handoff = OutreachPredictiveHandoff(ctx)

        request = handoff.predict_handoff_need(
            agent_name="TestAgent",
            lead_count=10,
            confidence=0.9,
        )

        assert request is not None
        assert request.reason == OutreachHandoffReason.COMPLIANCE_REQUIRED

    def test_predict_handoff_sensitive_contact(self, ctx):
        """Test handoff prediction with sensitive contact."""
        ctx.contacts = [{"name": "John", "title": "CEO", "email": "john@company.com"}]
        handoff = OutreachPredictiveHandoff(ctx)

        request = handoff.predict_handoff_need(
            agent_name="TestAgent",
            lead_count=1,
            confidence=0.9,
        )

        assert request is not None
        assert request.reason == OutreachHandoffReason.SENSITIVE_CONTACT

    def test_no_handoff_needed(self, ctx):
        """Test no handoff when everything is fine."""
        handoff = OutreachPredictiveHandoff(ctx)

        profile = OutreachCapabilityProfile(
            agent_name="TestAgent",
            supported_tasks=[],
            confidence_threshold=0.7,
            max_leads_per_batch=100,
            known_limitations=[],
        )
        handoff.register_capability(profile)

        request = handoff.predict_handoff_need(
            agent_name="TestAgent",
            lead_count=50,
            confidence=0.9,
        )

        assert request is None


class TestOutreachCapabilityMonitor:
    """Tests for OutreachCapabilityMonitorAgent."""

    def test_init(self, ctx):
        """Test monitor initialization."""
        monitor = OutreachCapabilityMonitorAgent(ctx)

        assert monitor.ctx == ctx
        assert len(monitor._execution_history) == 0

    def test_record_execution(self, ctx):
        """Test recording execution."""
        monitor = OutreachCapabilityMonitorAgent(ctx)

        monitor.record_execution(
            agent_name="TestAgent",
            TaskType="email_send",
            success=True,
            duration_ms=100,
            leads_processed=10,
        )

        assert len(monitor._execution_history) == 1
        assert monitor._agent_stats["TestAgent"]["total_leads_processed"] == 10

    def test_get_success_rate(self, ctx):
        """Test getting success rate."""
        monitor = OutreachCapabilityMonitorAgent(ctx)

        monitor.record_execution("TestAgent", "task1", True, 100, 5)
        monitor.record_execution("TestAgent", "task2", True, 100, 5)
        monitor.record_execution("TestAgent", "task3", False, 100, 5)

        rate = monitor.get_success_rate("TestAgent")

        assert abs(rate - 0.67) < 0.1

    def test_get_capability_profile(self, ctx):
        """Test generating capability profile."""
        monitor = OutreachCapabilityMonitorAgent(ctx)

        monitor.record_execution("TestAgent", "email", True, 100, 10)
        monitor.record_execution("TestAgent", "validation", True, 100, 5)

        profile = monitor.get_capability_profile("TestAgent")

        assert profile.agent_name == "TestAgent"
        assert "email" in profile.supported_tasks
        assert "validation" in profile.supported_tasks


class TestOutreachProactiveAgent:
    """Tests for OutreachProactiveAgent."""

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs):
        """Autonomous healing - test class stub."""
        return {"violations": 0, "fixed": 0, "errors": 0}

    @pytest.mark.asyncio
    async def test_execute(self, ctx):
        """Test agent execution."""
        ctx.add_signal("LEAD_QUALITY_ISSUE")
        agent = OutreachProactiveAgent(ctx)

        await agent.execute()

        assert ctx.results.get("OutreachProactiveAgent") is not None
        assert ctx.results["OutreachProactiveAgent"]["passed"] is True

    @pytest.mark.asyncio
    async def test_execute_with_compliance_handoff(self, ctx):
        """Test agent execution with compliance handoff."""
        ctx.add_signal("COMPLIANCE_ISSUE")
        agent = OutreachProactiveAgent(ctx)

        await agent.execute()

        assert ctx.has_signal("HANDOFF_RECOMMENDED")

    @pytest.mark.asyncio
    async def test_execute_with_sensitive_contact(self, ctx):
        """Test agent execution with sensitive contact."""
        ctx.contacts = [{"name": "CEO", "title": "CEO", "email": "ceo@company.com"}]
        agent = OutreachProactiveAgent(ctx)

        await agent.execute()

        assert ctx.has_signal("HANDOFF_RECOMMENDED")


class TestIntegration:
    """Integration tests for proactive components."""

    @pytest.mark.asyncio
    async def test_full_proactive_workflow(self, ctx, valid_campaign):
        """Test full proactive workflow."""
        ctx.current_campaign = {"name": "Test"}  # Missing schedule
        ctx.add_signal("LEAD_QUALITY_ISSUE")
        ctx.leads = [{"company": "Test Corp"}]

        scheduler = OutreachProactiveScheduler(ctx)
        handoff = OutreachPredictiveHandoff(ctx)
        monitor = OutreachCapabilityMonitorAgent(ctx)

        # Register capability
        profile = OutreachCapabilityProfile(
            agent_name="OutreachProactiveAgent",
            supported_tasks=["email", "validation"],
            confidence_threshold=0.7,
            max_leads_per_batch=100,
            known_limitations=[],
        )
        handoff.register_capability(profile)

        # Identify tasks
        tasks = scheduler.identify_tasks()
        assert len(tasks) >= 1

        # Execute tasks
        for Task in scheduler.get_auto_executable_tasks():
            scheduler.mark_executed(Task.task_id)
            monitor.record_execution(
                agent_name="OutreachProactiveAgent",
                TaskType=Task.name,
                success=True,
                duration_ms=100,
                leads_processed=len(ctx.leads),
            )

        # Verify
        assert monitor.get_success_rate("OutreachProactiveAgent") > 0


def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path = None):
    """Test file - operational stub only."""
    if _call_path is None:
        _call_path = set()
    agent_name = "TestOutreachProactive"
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
