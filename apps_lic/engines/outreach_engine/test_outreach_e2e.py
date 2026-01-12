from __future__ import annotations
"""
End-to-End Tests for Outreach Engine Autonomous Module

Tests complete workflows:
- Full campaign lifecycle
- Multi-phase orchestration
- Real-world scenarios
"""
import re


import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from apps_lic.outreach_engine.autonomous.agents import (
    CampaignBalanceAgent,
    CampaignPlannerAgent,
    ContactValidatorAgent,
    DeliverabilityAgent,
    LeadQualityAgent,
    MessageComplianceAgent,
    OutreachReflectionAgent,
    OutreachTestPilot,
    TemplateOptimizerAgent,
)
from apps_lic.outreach_engine.autonomous.context import OutreachEngineContext
from apps_lic.outreach_engine.autonomous.healing import (
    OutreachHealingOrchestratorAgent,
    OutreachHealingResult,
    run_outreach_healing_mission,
)
from apps_lic.outreach_engine.autonomous.learning import (
    OutreachLearningAgent,
    OutreachMemoryPersistence,
)
from apps_lic.outreach_engine.autonomous.observability import OutreachPhase5OrchestratorAgent


@pytest.fixture
def ctx():
    """Create a fresh context."""
    return OutreachEngineContext()


@pytest.fixture
def complete_campaign():
    """Create a complete campaign configuration."""
    return {
        "name": "Q4 Enterprise Outreach",
        "goal": "Generate 50 qualified leads",
        "schedule": "weekdays_9am",
        "follow_up_sequence": ["day_1", "day_3", "day_7"],
        "tracking": True,
        "segmentation": "by_industry",
    }


@pytest.fixture
def enterprise_leads():
    """Create enterprise-quality leads."""
    return [
        {
            "company": "Microsoft",
            "contact_name": "Sarah Johnson",
            "email": "sarah.johnson@microsoft.com",
            "title": "VP of Engineering",
            "linkedin": "linkedin.com/in/sarahjohnson",
            "industry": "Technology",
        },
        {
            "company": "Google",
            "contact_name": "Michael Chen",
            "email": "michael.chen@google.com",
            "title": "Director of Product",
            "linkedin": "linkedin.com/in/michaelchen",
            "industry": "Technology",
        },
        {
            "company": "Amazon",
            "contact_name": "Emily Davis",
            "email": "emily.davis@amazon.com",
            "title": "Senior Manager",
            "linkedin": "linkedin.com/in/emilydavis",
            "industry": "E-commerce",
        },
    ]


@pytest.fixture
def professional_messages():
    """Create professional message templates."""
    return [
        {
            "subject": "Partnership Opportunity with {company}",
            "content": """Dear {name},

I hope this message finds you well. I recently came across {company}'s impressive work in the industry and wanted to reach out.

Given your role as {title}, I believe there could be valuable synergies between our organizations. I would love to schedule a brief call to discuss potential collaboration opportunities.

Would you be available for a 15-minute call next week?

Best regards,
John Smith

---
To unsubscribe from future communications, click here.
""",
        },
        {
            "subject": "Following up on my previous message",
            "content": """Hi {name},

I wanted to follow up on my previous email regarding potential collaboration between our companies.

I understand you're busy, but I believe a quick conversation could be mutually beneficial. Would you have 10 minutes this week?

Looking forward to connecting.

Best,
John Smith

---
Unsubscribe here.
""",
        },
    ]


class TestCompleteCampaignLifecycle:
    """Tests for complete campaign lifecycle."""

    @pytest.mark.asyncio
    async def test_full_campaign_setup_and_validation(
        self, ctx, complete_campaign, enterprise_leads, professional_messages
    ):
        """Test complete campaign setup and validation."""
        # Setup
        ctx.current_campaign = complete_campaign
        ctx.leads = enterprise_leads
        ctx.messages = professional_messages
        ctx.target_company = "Enterprise Clients"

        # Backup initial state
        ctx.backup_campaign("initial")

        # Start observability
        phase5 = OutreachPhase5OrchestratorAgent(ctx)
        phase5.start_mission("campaign_lifecycle")

        # Run all validation agents
        agents = [
            LeadQualityAgent(ctx),
            ContactValidatorAgent(ctx),
            MessageComplianceAgent(ctx),
            RgTemplateOptimizerAgent(ctx),
            CampaignBalanceAgent(ctx),
            DeliverabilityAgent(ctx),
        ]

        for agent in agents:
            step_id = phase5.track_agent(agent.name, "execute")
            await agent.execute()
            result = ctx.results.get(agent.name, {})
            phase5.complete_agent(step_id, success=result.get("passed", True))

        # Run test pilot
        test_pilot = OutreachTestPilot(ctx)
        step_id = phase5.track_agent("OutreachTestPilot", "validate")
        await test_pilot.execute()
        phase5.complete_agent(step_id, success=True)

        # End mission
        trace = phase5.end_mission(success=True)

        # Verify
        assert trace is not None
        assert len(trace.steps) >= 7
        assert ctx.results.get("LeadQualityAgent", {}).get("passed") is True

    @pytest.mark.asyncio
    async def test_campaign_with_healing_cycle(
        self, ctx, complete_campaign, enterprise_leads, professional_messages
    ):
        """Test campaign with healing cycle."""
        ctx.current_campaign = complete_campaign
        ctx.leads = enterprise_leads
        ctx.messages = professional_messages

        # Run healing mission
        result = await run_outreach_healing_mission(
            campaign=complete_campaign,
            leads=enterprise_leads,
            messages=professional_messages,
            max_cycles=3,
        )

        assert isinstance(result, OutreachHealingResult)
        assert result.total_cycles >= 1
        assert result.final_campaign is not None


class TestMultiPhaseOrchestration:
    """Tests for multi-phase orchestration."""

    @pytest.mark.asyncio
    async def test_planning_validation_execution_phases(
        self, ctx, complete_campaign, enterprise_leads, professional_messages
    ):
        """Test planning, validation, and execution phases."""
        ctx.current_campaign = complete_campaign
        ctx.leads = enterprise_leads
        ctx.messages = professional_messages

        phase5 = OutreachPhase5OrchestratorAgent(ctx)
        learning_agent = OutreachLearningAgent(ctx)

        # Phase 1: Planning
        phase5.start_mission("multi_phase_test")

        planner = CampaignPlannerAgent(ctx)
        step_id = phase5.track_agent("CampaignPlannerAgent", "plan")
        await planner.execute()
        phase5.complete_agent(step_id, success=True)

        # Phase 2: Validation
        validation_agents = [
            LeadQualityAgent(ctx),
            ContactValidatorAgent(ctx),
            MessageComplianceAgent(ctx),
        ]

        for agent in validation_agents:
            step_id = phase5.track_agent(agent.name, "validate")
            await agent.execute()
            phase5.complete_agent(step_id, success=True)

        # Phase 3: Healing (if needed)
        if ctx.signals:
            step_id = phase5.track_agent("HealingOrchestratorAgent", "heal")
            orchestrator = LicHealingOrchestratorAgent(ctx, max_cycles=2)
            result = await orchestrator.run()
            phase5.complete_agent(step_id, success=result.total_cycles >= 1)

        # Phase 4: Learning
        step_id = phase5.track_agent("LearningAgent", "learn")
        await learning_agent.execute()
        phase5.complete_agent(step_id, success=True)

        # Phase 5: Reflection
        reflection = LicReflectionAgent(ctx)
        step_id = phase5.track_agent("ReflectionAgent", "reflect")
        await reflection.execute()
        phase5.complete_agent(step_id, success=True)

        # End mission
        trace = phase5.end_mission(success=True)
        report = phase5.generate_report()

        assert trace is not None
        assert report is not None
        assert len(trace.steps) >= 5


class TestRealWorldScenarios:
    """Tests for real-world scenarios."""

    @pytest.mark.asyncio
    async def test_cold_outreach_campaign(self, ctx):
        """Test cold outreach campaign scenario."""
        campaign = {
            "name": "Cold Outreach Q4",
            "goal": "Book 20 meetings",
            "type": "cold",
        }

        leads = [
            {"company": "Acme Corp", "contact_name": "Bob", "email": "bob@acme.com"},
            {"company": "Widgets Inc", "contact_name": "Alice", "email": "alice@widgets.io"},
        ]

        messages = [
            {
                "subject": "Quick question for {name}",
                "content": "Hi {name}, I'd love to schedule a call. Unsubscribe here.",
            },
        ]

        result = await run_outreach_healing_mission(
            campaign=campaign,
            leads=leads,
            messages=messages,
            max_cycles=2,
        )

        assert result.total_cycles >= 1

    @pytest.mark.asyncio
    async def test_follow_up_campaign(self, ctx):
        """Test follow-up campaign scenario."""
        campaign = {
            "name": "Follow-up Campaign",
            "goal": "Re-engage cold leads",
            "type": "follow_up",
            "previous_campaign": "Q3_Outreach",
        }

        leads = [
            {"company": "Previous Lead", "contact_name": "John", "email": "john@prev.com"},
        ]

        messages = [
            {
                "subject": "Following up, {name}",
                "content": "Hi {name}, just following up. Let's schedule a call. Unsubscribe.",
            },
        ]

        result = await run_outreach_healing_mission(
            campaign=campaign,
            leads=leads,
            messages=messages,
            max_cycles=2,
        )

        assert result.total_cycles >= 1

    @pytest.mark.asyncio
    async def test_event_based_outreach(self, ctx):
        """Test event-based outreach scenario."""
        campaign = {
            "name": "Conference Follow-up",
            "goal": "Connect with conference attendees",
            "type": "event",
            "event_name": "Tech Summit 2024",
        }

        leads = [
            {
                "company": "Attendee Corp",
                "contact_name": "Sarah",
                "email": "sarah@attendee.com",
                "met_at": "Tech Summit 2024",
            },
        ]

        messages = [
            {
                "subject": "Great meeting you at Tech Summit, {name}",
                "content": "Hi {name}, it was great meeting you. Let's schedule a follow-up call. Unsubscribe.",
            },
        ]

        result = await run_outreach_healing_mission(
            campaign=campaign,
            leads=leads,
            messages=messages,
            max_cycles=2,
        )

        assert result.total_cycles >= 1


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.asyncio
    async def test_empty_campaign(self, ctx):
        """Test handling empty campaign."""
        result = await run_outreach_healing_mission(
            campaign={},
            leads=[],
            messages=[],
            max_cycles=2,
        )

        assert result.total_cycles >= 1

    @pytest.mark.asyncio
    async def test_large_lead_list(self, ctx):
        """Test handling large lead list."""
        leads = [
            {"company": f"Company {i}", "contact_name": f"Contact {i}", "email": f"contact{i}@company{i}.com"}
            for i in range(100)
        ]

        result = await run_outreach_healing_mission(
            campaign={"name": "Large Campaign", "goal": "Test scale"},
            leads=leads,
            messages=[{"subject": "Test", "content": "Test content. Unsubscribe."}],
            max_cycles=2,
        )

        assert result.total_cycles >= 1

    @pytest.mark.asyncio
    async def test_special_characters_in_content(self, ctx):
        """Test handling special characters."""
        messages = [
            {
                "subject": "Special chars: é, ñ, 中文",
                "content": "Hello! Special: é, ñ, 中文, 日本語. Unsubscribe here.",
            },
        ]

        result = await run_outreach_healing_mission(
            campaign={"name": "Special Chars Test"},
            leads=[{"company": "Test", "contact_name": "Test", "email": "test@test.com"}],
            messages=messages,
            max_cycles=2,
        )

        assert result.total_cycles >= 1


class TestMemoryPersistence:
    """Tests for memory persistence."""

    def test_memory_store_and_retrieve(self, tmp_path):
        """Test storing and retrieving from agentic_core.semantic_memory."""
        memory_file = tmp_path / "test_memory.json"
        memory = OutreachMemoryPersistence(str(memory_file))

        memory.store("test_key", {"value": 42})

        result = memory.retrieve("test_key")

        assert result == {"value": 42}

    def test_memory_persistence_across_instances(self, tmp_path):
        """Test memory persists across instances."""
        memory_file = tmp_path / "persist_memory.json"

        # First instance
        memory1 = OutreachMemoryPersistence(str(memory_file))
        memory1.store("persistent_key", "persistent_value")

        # Second instance
        memory2 = OutreachMemoryPersistence(str(memory_file))
        result = memory2.retrieve("persistent_key")

        assert result == "persistent_value"

    def test_memory_clear(self, tmp_path):
        """Test clearing memory."""
        memory_file = tmp_path / "clear_memory.json"
        memory = OutreachMemoryPersistence(str(memory_file))

        memory.store("key1", "value1")
        memory.store("key2", "value2")

        memory.clear()

        assert memory.retrieve("key1") is None
        assert memory.retrieve("key2") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
