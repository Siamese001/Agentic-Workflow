from __future__ import annotations
"""
Integration Tests for Autonomous Resume Engine

Tests agent coordination and signal-based routing:
- Multiple agents working together
- Signal propagation
- Rollback mechanisms
- Strategic planning integration
"""

import pytest

from ..agents import (
    ATSCompatibilityAgent,
    BrandComplianceAgent,
    ContentQualityAgent,
    FactCheckAgent,
    ReflectionAgent,
    SectionBalanceAgent,
    StrategicPlannerAgent,
    TemplateOptimizerAgent,
    TestPilot,
)
from ..context import ResumeEngineContext


@pytest.fixture
def ctx():
    """Create a fresh context for each test."""
    return ResumeEngineContext()


@pytest.fixture
def valid_resume():
    """Create a valid resume for testing."""
    return {
        "summary": "Experienced software engineer with 10+ years building scalable systems. Led teams of 5-10 engineers and delivered projects that increased revenue by 25%.",
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Senior Engineer",
                "description": "Developed microservices architecture serving 1M+ users. Reduced latency by 40% through optimization."
            }
        ],
        "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"],
        "education": "BS Computer Science, MIT, 2010",
    }


@pytest.fixture
def problematic_resume():
    """Create a resume with multiple issues."""
    return {
        "summary": "I am responsible for doing stuff.",  # Brand Violation + too short
        "experience": "Worked on things",  # No quantification
        "skills": ["Python"],
        "education": "Some school",
    }


class TestAgentCoordination:
    """Tests for multi-agent coordination."""

    @pytest.mark.asyncio
    async def test_full_agent_pipeline_valid(self, ctx, valid_resume):
        """Test full pipeline with valid resume."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = "Senior Software Engineer"

        agents = [
            ContentQualityAgent(ctx),
            FactCheckAgent(ctx),
            BrandComplianceAgent(ctx),
            TemplateOptimizerAgent(ctx),
            SectionBalanceAgent(ctx),
            ATSCompatibilityAgent(ctx),
            TestPilot(ctx),
        ]

        for agent in agents:
            await agent.execute()

        # All agent results should pass (filter out non-agent results like template_recommendations)
        agent_results = {k: v for k, v in ctx.results.items() if isinstance(v, dict) and "passed" in v}
        assert all(r["passed"] for r in agent_results.values())
        assert ctx.is_converged()

    @pytest.mark.asyncio
    async def test_full_agent_pipeline_invalid(self, ctx, problematic_resume):
        """Test full pipeline with problematic resume."""
        ctx.current_resume = problematic_resume
        ctx.JobDescription = "Software Engineer"

        agents = [
            ContentQualityAgent(ctx),
            BrandComplianceAgent(ctx),
            SectionBalanceAgent(ctx),
            TestPilot(ctx),
        ]

        for agent in agents:
            await agent.execute()

        # Should have failures
        assert not ctx.is_converged()
        assert len(ctx.signals) > 0


class TestSignalPropagation:
    """Tests for signal-based communication."""

    @pytest.mark.asyncio
    async def test_quality_failure_signal(self, ctx):
        """Test QUALITY_FAILURE signal propagation."""
        ctx.current_resume = {"summary": "Too short"}

        agent = ContentQualityAgent(ctx)
        await agent.execute()

        assert "QUALITY_FAILURE" in ctx.signals

        # Strategic planner should pick up the signal
        planner = StrategicPlannerAgent(ctx)
        await planner.execute()

        plan = ctx.results["strategic_plan"]
        assert "QUALITY_FAILURE" in plan["priority_signals"]
        assert "ContentQualityAgent" in plan["recommended_agents"]

    @pytest.mark.asyncio
    async def test_brand_violation_signal(self, ctx):
        """Test BRAND_VIOLATION signal propagation."""
        ctx.current_resume = {
            "summary": "I am responsible for stuff etc.",
            "experience": "Did things",
            "skills": "Python",
        }

        agent = BrandComplianceAgent(ctx)
        await agent.execute()

        assert "BRAND_VIOLATION" in ctx.signals

        # Strategic planner should recommend BrandComplianceAgent
        planner = StrategicPlannerAgent(ctx)
        await planner.execute()

        plan = ctx.results["strategic_plan"]
        assert "BrandComplianceAgent" in plan["recommended_agents"]

    @pytest.mark.asyncio
    async def test_multiple_signals(self, ctx, problematic_resume):
        """Test multiple signals from different agents."""
        ctx.current_resume = problematic_resume

        # Run multiple agents
        await ContentQualityAgent(ctx).execute()
        await BrandComplianceAgent(ctx).execute()

        # Should have multiple signals
        assert len(ctx.signals) >= 2

        # Strategic planner should handle all
        planner = StrategicPlannerAgent(ctx)
        await planner.execute()

        plan = ctx.results["strategic_plan"]
        assert len(plan["priority_signals"]) >= 2


class TestRollbackMechanism:
    """Tests for section backup and rollback."""

    @pytest.mark.asyncio
    async def test_section_modification_tracking(self, ctx, valid_resume):
        """Test that section modifications are tracked."""
        ctx.current_resume = valid_resume.copy()

        # Modify a section
        ctx.update_section("summary", "New summary content")

        assert "summary" in ctx.modified_sections
        assert "summary" in ctx.section_backups

    @pytest.mark.asyncio
    async def test_rollback_on_failure(self, ctx, valid_resume):
        """Test rollback when test fails after modification."""
        ctx.current_resume = valid_resume.copy()
        original_summary = valid_resume["summary"]

        # Modify section
        ctx.update_section("summary", "Bad summary")

        # Simulate test failure
        ctx.add_signal("TEST_FAILURE")

        # Rollback
        ctx.rollback_all()

        assert ctx.current_resume["summary"] == original_summary
        assert len(ctx.modified_sections) == 0

    @pytest.mark.asyncio
    async def test_blast_radius_calculation(self, ctx, valid_resume):
        """Test blast radius calculation on modification."""
        ctx.current_resume = valid_resume.copy()

        # Modify experience (should impact skills and achievements)
        ctx.update_section("experience", "New experience")

        # Check impact zone
        assert len(ctx.impact_zone) > 0


class TestStrategicPlanningIntegration:
    """Tests for strategic planning with other agents."""

    @pytest.mark.asyncio
    async def test_planner_after_failures(self, ctx, problematic_resume):
        """Test strategic planner after agent failures."""
        ctx.current_resume = problematic_resume

        # Run validation agents
        await ContentQualityAgent(ctx).execute()
        await BrandComplianceAgent(ctx).execute()
        await ATSCompatibilityAgent(ctx).execute()

        # Run strategic planner
        planner = StrategicPlannerAgent(ctx)
        await planner.execute()

        plan = ctx.results["strategic_plan"]

        # Should have prioritized signals and recommended agents
        assert len(plan["priority_signals"]) > 0
        assert len(plan["recommended_agents"]) > 0
        assert plan["strategy"] != "standard"

    @pytest.mark.asyncio
    async def test_reflection_after_success(self, ctx, valid_resume):
        """Test reflection agent after successful validation."""
        ctx.current_resume = valid_resume
        ctx.current_cycle = 1

        # Run all validation agents
        agents = [
            ContentQualityAgent(ctx),
            FactCheckAgent(ctx),
            BrandComplianceAgent(ctx),
            SectionBalanceAgent(ctx),
            ATSCompatibilityAgent(ctx),
            TestPilot(ctx),
        ]

        for agent in agents:
            await agent.execute()

        # Run reflection
        reflection = ReflectionAgent(ctx)
        await reflection.execute()

        insights = ctx.results["reflection"]
        assert insights["outcome"] == "success"
        assert insights["converged"] is True

    @pytest.mark.asyncio
    async def test_reflection_records_learning(self, ctx, valid_resume):
        """Test that reflection records successful patterns."""
        ctx.current_resume = valid_resume
        ctx.current_cycle = 1

        # Mark all as passed
        ctx.record_result("Agent1", passed=True)
        ctx.record_result("Agent2", passed=True)

        # Run reflection
        reflection = ReflectionAgent(ctx)
        await reflection.execute()

        # Should have recorded success
        assert ctx.generation_stats["success"] == 1
        assert len(ctx.successful_generations) == 1


class TestBudgetIntegration:
    """Tests for budget management integration."""

    @pytest.mark.asyncio
    async def test_budget_tracking_across_agents(self, ctx, valid_resume):
        """Test budget tracking across multiple agents."""
        ctx.current_resume = valid_resume

        initial_cost = ctx.budget.current_cost

        # Run agents (they may or may not call LLM)
        await ContentQualityAgent(ctx).execute()
        await BrandComplianceAgent(ctx).execute()

        # Budget should be tracked (even if no LLM calls)
        assert ctx.budget.current_cost >= initial_cost

    def test_budget_stats_in_context(self, ctx):
        """Test budget stats are included in context stats."""
        stats = ctx.get_stats()

        assert "budget_stats" in stats
        assert "current_cost_usd" in stats["budget_stats"]
        assert "remaining_usd" in stats["budget_stats"]


class TestEndToEndScenarios:
    """End-to-end scenario tests."""

    @pytest.mark.asyncio
    async def test_scenario_valid_resume_full_validation(self, ctx, valid_resume):
        """Scenario: Valid resume goes through full validation."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = "Senior Software Engineer at Tech Company"
        ctx.user_profile = {"skills": ["Python", "JavaScript", "AWS"]}

        # Full agent pipeline
        agents = [
            TemplateOptimizerAgent(ctx),
            ContentQualityAgent(ctx),
            FactCheckAgent(ctx),
            BrandComplianceAgent(ctx),
            SectionBalanceAgent(ctx),
            ATSCompatibilityAgent(ctx),
            TestPilot(ctx),
            StrategicPlannerAgent(ctx),
            ReflectionAgent(ctx),
        ]

        for agent in agents:
            await agent.execute()

        # Should converge successfully
        assert ctx.is_converged()
        assert ctx.results["reflection"]["outcome"] == "success"

    @pytest.mark.asyncio
    async def test_scenario_problematic_resume_detection(self, ctx, problematic_resume):
        """Scenario: Problematic resume issues are detected."""
        ctx.current_resume = problematic_resume
        ctx.JobDescription = "Software Engineer"

        # Run detection agents
        await ContentQualityAgent(ctx).execute()
        await BrandComplianceAgent(ctx).execute()
        await TestPilot(ctx).execute()

        # Should not converge
        assert not ctx.is_converged()

        # Should have signals for issues
        assert len(ctx.signals) > 0

        # Strategic planner should identify issues
        await StrategicPlannerAgent(ctx).execute()
        plan = ctx.results["strategic_plan"]
        assert len(plan["recommended_agents"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
