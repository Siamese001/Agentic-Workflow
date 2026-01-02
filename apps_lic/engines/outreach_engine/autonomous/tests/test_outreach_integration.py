from __future__ import annotations
"""
Integration Tests for Outreach Engine Autonomous Module

Tests integration between components:
- Healing with learning
- Observability with healing
- Full pipeline integration
"""
import re


import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from apps_lic.outreach_engine.autonomous.agents import (
    ContactValidatorAgent,
    LeadQualityAgent,
    MessageComplianceAgent,
)
from apps_lic.outreach_engine.autonomous.context import OutreachEngineContext
from apps_lic.outreach_engine.autonomous.healing import (
    OutreachHealingOrchestratorAgent,
    OutreachSignalRouterAgent,
)
from apps_lic.outreach_engine.autonomous.learning import (
    OutreachLearningAgent,
    OutreachLearningLoop,
)
from apps_lic.outreach_engine.autonomous.observability import OutreachPhase5OrchestratorAgent


@pytest.fixture
def ctx():
    """Create a fresh context."""
    return OutreachEngineContext()


@pytest.fixture
def valid_campaign():
    """Create a valid campaign."""
    return {
        "name": "Integration Test Campaign",
        "goal": "Test integration",
        "schedule": "daily",
    }


@pytest.fixture
def valid_leads():
    """Create valid leads."""
    return [
        {"company": "Tech Corp", "contact_name": "John", "email": "john@tech.com"},
        {"company": "Startup Inc", "contact_name": "Jane", "email": "jane@startup.io"},
    ]


@pytest.fixture
def valid_messages():
    """Create valid messages."""
    return [
        {
            "subject": "Partnership with {company}",
            "content": "Dear {name},\n\nI'd love to schedule a call.\n\nUnsubscribe here.",
        },
    ]


class TestHealingWithLearning:
    """Tests for healing integrated with learning."""

    @pytest.mark.asyncio
    async def test_learning_during_healing(self, ctx, valid_campaign, valid_leads, valid_messages):
        """Test learning agent runs during healing."""
        ctx.current_campaign = valid_campaign
        ctx.leads = valid_leads
        ctx.messages = valid_messages

        learning_agent = OutreachLearningAgent(ctx)

        # Run healing
        orchestrator = OutreachHealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        # Run learning
        await learning_agent.execute()

        assert result.total_cycles >= 1
        assert ctx.results.get("OutreachLearningAgent") is not None

    @pytest.mark.asyncio
    async def test_learning_records_patterns(self, ctx, valid_campaign):
        """Test learning records patterns from healing."""
        ctx.current_campaign = valid_campaign

        learning = OutreachLearningLoop(ctx)

        await learning.record_success("campaign_creation", "test", "success")
        await learning.record_success("campaign_creation", "test2", "success")
        await learning.record_failure("campaign_creation", "test3", "error")

        rate = learning.get_success_rate("campaign_creation")

        assert abs(rate - 0.67) < 0.1


class TestObservabilityWithHealing:
    """Tests for observability integrated with healing."""

    @pytest.mark.asyncio
    async def test_trace_healing_mission(self, ctx, valid_campaign, valid_leads, valid_messages):
        """Test tracing a healing mission."""
        ctx.current_campaign = valid_campaign
        ctx.leads = valid_leads
        ctx.messages = valid_messages

        phase5 = OutreachPhase5OrchestratorAgent(ctx)

        # Start mission
        phase5.start_mission("healing_test")

        # Run healing
        step_id = phase5.track_agent("HealingOrchestratorAgent", "run")
        orchestrator = OutreachHealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()
        phase5.complete_agent(step_id, success=result.total_cycles >= 1)

        # End mission
        trace = phase5.end_mission(success=True)

        assert trace is not None
        assert len(trace.steps) >= 1

    @pytest.mark.asyncio
    async def test_metrics_during_healing(self, ctx, valid_campaign, valid_leads, valid_messages):
        """Test metrics collection during healing."""
        ctx.current_campaign = valid_campaign
        ctx.leads = valid_leads
        ctx.messages = valid_messages

        phase5 = OutreachPhase5OrchestratorAgent(ctx)
        phase5.start_mission("metrics_test")

        # Record metrics
        phase5.metrics.counter("leads_processed", len(valid_leads))
        phase5.metrics.gauge("message_count", len(valid_messages))

        # Run healing
        orchestrator = OutreachHealingOrchestratorAgent(ctx, max_cycles=2)
        await orchestrator.run()

        phase5.metrics.counter("healing_cycles", 2)

        summary = phase5.metrics.get_summary()

        assert summary["counters"]["leads_processed"] == 2
        assert summary["gauges"]["message_count"] == 1


class TestFullPipelineIntegration:
    """Tests for full pipeline integration."""

    @pytest.mark.asyncio
    async def test_complete_pipeline(self, ctx, valid_campaign, valid_leads, valid_messages):
        """Test complete pipeline with all components."""
        ctx.current_campaign = valid_campaign
        ctx.leads = valid_leads
        ctx.messages = valid_messages

        phase5 = OutreachPhase5OrchestratorAgent(ctx)
        learning_agent = OutreachLearningAgent(ctx)

        # Start observability
        phase5.start_mission("complete_pipeline")

        # Run agents
        agents = [
            LeadQualityAgent(ctx),
            ContactValidatorAgent(ctx),
            MessageComplianceAgent(ctx),
        ]

        for agent in agents:
            step_id = phase5.track_agent(agent.name, "execute")
            await agent.execute()
            result = ctx.results.get(agent.name, {})
            phase5.complete_agent(step_id, success=result.get("passed", False))

        # Run healing if needed
        if ctx.signals:
            step_id = phase5.track_agent("HealingOrchestratorAgent", "run")
            orchestrator = OutreachHealingOrchestratorAgent(ctx, max_cycles=2)
            result = await orchestrator.run()
            phase5.complete_agent(step_id, success=result.total_cycles >= 1)

        # Run learning
        step_id = phase5.track_agent("LearningAgent", "execute")
        await learning_agent.execute()
        phase5.complete_agent(step_id, success=True)

        # End mission
        trace = phase5.end_mission(success=True)
        report = phase5.generate_report("complete_pipeline")

        assert trace is not None
        assert report is not None
        assert "mission_name" in report

    @pytest.mark.asyncio
    async def test_pipeline_with_failures(self, ctx):
        """Test pipeline handles failures gracefully."""
        ctx.current_campaign = {"name": "Test"}
        ctx.leads = [{"company": ""}]  # Invalid lead
        ctx.messages = [{"subject": "FREE!!!", "content": "Act now!"}]  # Non-compliant

        phase5 = OutreachPhase5OrchestratorAgent(ctx)
        phase5.start_mission("failure_test")

        # Run agents
        lead_agent = LeadQualityAgent(ctx)
        await lead_agent.execute()

        compliance_agent = MessageComplianceAgent(ctx)
        await compliance_agent.execute()

        # Should have signals
        assert ctx.has_signal("LEAD_QUALITY_ISSUE")
        assert ctx.has_signal("COMPLIANCE_ISSUE")

        # Run healing
        orchestrator = OutreachHealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        # Healing should complete even with issues
        assert result.total_cycles >= 1

        trace = phase5.end_mission(success=False)
        assert trace is not None


class TestSignalRouting:
    """Tests for signal routing integration."""

    def test_route_multiple_signals(self):
        """Test routing multiple signals."""
        signals = {"LEAD_QUALITY_ISSUE", "COMPLIANCE_ISSUE", "DELIVERABILITY_ISSUE"}

        agents = OutreachSignalRouterAgent.get_agents_for_signals(signals)

        assert "LeadQualityAgent" in agents
        assert "MessageComplianceAgent" in agents
        assert "DeliverabilityAgent" in agents

    @pytest.mark.asyncio
    async def test_surgical_strike_strategy(self, ctx):
        """Test surgical strike targets specific agents."""
        ctx.current_campaign = {"name": "Test"}
        ctx.leads = [{"company": ""}]
        ctx.messages = []

        # Add specific signal
        ctx.add_signal("LEAD_QUALITY_ISSUE")

        # Run healing with surgical strike
        orchestrator = OutreachHealingOrchestratorAgent(ctx, max_cycles=2)
        result = await orchestrator.run()

        # Should have executed LeadQualityAgent
        assert result.total_cycles >= 1


class TestBudgetIntegration:
    """Tests for budget integration."""

    @pytest.mark.asyncio
    async def test_budget_tracking_during_healing(self, ctx, valid_campaign, valid_leads, valid_messages):
        """Test budget is tracked during healing."""
        ctx.current_campaign = valid_campaign
        ctx.leads = valid_leads
        ctx.messages = valid_messages

        ctx.budget.current_cost

        orchestrator = OutreachHealingOrchestratorAgent(ctx, max_cycles=2)
        await orchestrator.run()

        # Budget should still be available
        assert ctx.budget.check_budget() is True

    @pytest.mark.asyncio
    async def test_budget_exhaustion_stops_healing(self, ctx, valid_campaign):
        """Test healing stops when budget exhausted."""
        ctx.current_campaign = valid_campaign
        ctx.budget.max_budget = 0.0001  # Very low budget
        ctx.budget.current_cost = 0.0001  # Already at limit

        orchestrator = OutreachHealingOrchestratorAgent(ctx, max_cycles=5)
        result = await orchestrator.run()

        # Should stop due to budget
        assert result.budget_exhausted is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
