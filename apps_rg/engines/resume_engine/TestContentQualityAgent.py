from __future__ import annotations
"""
Unit Tests for Resume Agents

Tests each specialized agent's functionality:
- ContentQualityAgent
- FactCheckAgent
- BrandComplianceAgent
- TemplateOptimizerAgent
- SectionBalanceAgent
- ATSCompatibilityAgent
- TestPilot
- StrategicPlannerAgent
- ReflectionAgent
"""
import re


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
def invalid_resume():
    """Create an invalid resume with issues."""
    return {
        "summary": "I am a developer.",  # Too short, first person
        "experience": "Worked on stuff",  # No quantification
        "skills": "",  # Empty
    }


class TestContentQualityAgent:
    """Tests for ContentQualityAgent."""

    @pytest.mark.asyncio
    async def test_valid_resume_passes(self, ctx, valid_resume):
        """Test that valid resume passes quality check."""
        ctx.current_resume = valid_resume
        agent = ContentQualityAgent(ctx)

        await agent.execute()

        assert ctx.results["ContentQualityAgent"]["passed"] is True
        assert "QUALITY_FAILURE" not in ctx.signals

    @pytest.mark.asyncio
    async def test_empty_resume_fails(self, ctx):
        """Test that empty resume fails."""
        ctx.current_resume = {}
        agent = ContentQualityAgent(ctx)

        await agent.execute()

        assert ctx.results["ContentQualityAgent"]["passed"] is False
        assert "QUALITY_FAILURE" in ctx.signals

    @pytest.mark.asyncio
    async def test_placeholder_detection(self, ctx):
        """Test placeholder detection."""
        ctx.current_resume = {
            "summary": "This is a [PLACEHOLDER] summary with TODO items",
            "experience": "Real experience content here with 5 years of work",
            "skills": "Python, JavaScript",
        }
        agent = ContentQualityAgent(ctx)

        await agent.execute()

        assert ctx.results["ContentQualityAgent"]["passed"] is False
        assert "QUALITY_FAILURE" in ctx.signals

    @pytest.mark.asyncio
    async def test_short_section_detection(self, ctx):
        """Test short section detection."""
        ctx.current_resume = {
            "summary": "Short",  # Too short
            "experience": "This is a longer experience section with enough content to pass the minimum length requirement.",
            "skills": "Python",
        }
        agent = ContentQualityAgent(ctx)

        await agent.execute()

        assert ctx.results["ContentQualityAgent"]["passed"] is False


class TestFactCheckAgent:
    """Tests for FactCheckAgent."""

    @pytest.mark.asyncio
    async def test_no_profile_skips(self, ctx, valid_resume):
        """Test that Missing profile skips deep fact-check."""
        ctx.current_resume = valid_resume
        ctx.user_profile = {}
        agent = FactCheckAgent(ctx)

        await agent.execute()

        # Should pass (skipped) when no profile
        assert ctx.results["FactCheckAgent"]["passed"] is True

    @pytest.mark.asyncio
    async def test_verified_skills_pass(self, ctx):
        """Test that verified skills pass."""
        ctx.current_resume = {
            "summary": "Software engineer",
            "skills": ["Python", "JavaScript"],
            "experience": "Worked at companies",
        }
        ctx.user_profile = {
            "skills": ["Python", "JavaScript", "AWS"],
        }
        agent = FactCheckAgent(ctx)

        await agent.execute()

        assert ctx.results["FactCheckAgent"]["passed"] is True
        assert "HALLUCINATION_DETECTED" not in ctx.signals

    @pytest.mark.asyncio
    async def test_empty_resume_fails(self, ctx):
        """Test that empty resume fails fact-check."""
        ctx.current_resume = {}
        agent = FactCheckAgent(ctx)

        await agent.execute()

        assert ctx.results["FactCheckAgent"]["passed"] is False


class TestBrandComplianceAgent:
    """Tests for BrandComplianceAgent."""

    @pytest.mark.asyncio
    async def test_professional_content_passes(self, ctx, valid_resume):
        """Test that professional content passes."""
        ctx.current_resume = valid_resume
        agent = BrandComplianceAgent(ctx)

        await agent.execute()

        assert ctx.results["BrandComplianceAgent"]["passed"] is True
        assert "BRAND_VIOLATION" not in ctx.signals

    @pytest.mark.asyncio
    async def test_forbidden_phrases_fail(self, ctx):
        """Test that forbidden phrases are detected."""
        ctx.current_resume = {
            "summary": "I am responsible for doing stuff and things etc.",
            "experience": "Helped with various projects",
            "skills": "Python",
        }
        agent = BrandComplianceAgent(ctx)

        await agent.execute()

        assert ctx.results["BrandComplianceAgent"]["passed"] is False
        assert "BRAND_VIOLATION" in ctx.signals

    @pytest.mark.asyncio
    async def test_empty_resume_fails(self, ctx):
        """Test that empty resume fails."""
        ctx.current_resume = {}
        agent = BrandComplianceAgent(ctx)

        await agent.execute()

        assert ctx.results["BrandComplianceAgent"]["passed"] is False


class TestTemplateOptimizer:
    """Tests for TemplateOptimizerAgent."""

    @pytest.mark.asyncio
    async def test_technical_job_detection(self, ctx, valid_resume):
        """Test technical job type detection."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = "Senior Software Engineer needed for cloud development"
        agent = TemplateOptimizerAgent(ctx)

        await agent.execute()

        assert ctx.results["TemplateOptimizerAgent"]["passed"] is True
        assert ctx.results["template_recommendations"]["job_type"] == "technical"

    @pytest.mark.asyncio
    async def test_executive_job_detection(self, ctx, valid_resume):
        """Test executive job type detection."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = "VP of Engineering, Director level position"
        agent = TemplateOptimizerAgent(ctx)

        await agent.execute()

        assert ctx.results["template_recommendations"]["job_type"] == "executive"

    @pytest.mark.asyncio
    async def test_no_job_description(self, ctx, valid_resume):
        """Test handling of Missing job description."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = ""
        agent = TemplateOptimizerAgent(ctx)

        await agent.execute()

        assert ctx.results["TemplateOptimizerAgent"]["passed"] is True


class TestSectionBalanceAgent:
    """Tests for SectionBalanceAgent."""

    @pytest.mark.asyncio
    async def test_balanced_resume_passes(self, ctx, valid_resume):
        """Test that balanced resume passes."""
        ctx.current_resume = valid_resume
        agent = SectionBalanceAgent(ctx)

        await agent.execute()

        assert ctx.results["SectionBalanceAgent"]["passed"] is True
        assert "BALANCE_ISSUE" not in ctx.signals

    @pytest.mark.asyncio
    async def test_missing_required_section(self, ctx):
        """Test detection of Missing required sections."""
        ctx.current_resume = {
            "summary": "A good summary here",
            # Missing experience and skills
        }
        agent = SectionBalanceAgent(ctx)

        await agent.execute()

        assert ctx.results["SectionBalanceAgent"]["passed"] is False

    @pytest.mark.asyncio
    async def test_empty_resume_fails(self, ctx):
        """Test that empty resume fails."""
        ctx.current_resume = {}
        agent = SectionBalanceAgent(ctx)

        await agent.execute()

        assert ctx.results["SectionBalanceAgent"]["passed"] is False


class TestATSCompatibilityAgent:
    """Tests for ATSCompatibilityAgent."""

    @pytest.mark.asyncio
    async def test_ats_friendly_passes(self, ctx, valid_resume):
        """Test that ATS-friendly resume passes."""
        ctx.current_resume = valid_resume
        ctx.JobDescription = "Python developer needed"
        agent = ATSCompatibilityAgent(ctx)

        await agent.execute()

        assert ctx.results["ATSCompatibilityAgent"]["passed"] is True
        assert "ATS_FAILURE" not in ctx.signals

    @pytest.mark.asyncio
    async def test_special_characters_fail(self, ctx):
        """Test that special characters are detected."""
        ctx.current_resume = {
            "summary": "★ Award-winning developer ★ with ● multiple skills",
            "experience": "Normal experience",
            "skills": "Python",
        }
        agent = ATSCompatibilityAgent(ctx)

        await agent.execute()

        assert ctx.results["ATSCompatibilityAgent"]["passed"] is False
        assert "ATS_FAILURE" in ctx.signals

    @pytest.mark.asyncio
    async def test_empty_resume_fails(self, ctx):
        """Test that empty resume fails."""
        ctx.current_resume = {}
        agent = ATSCompatibilityAgent(ctx)

        await agent.execute()

        assert ctx.results["ATSCompatibilityAgent"]["passed"] is False


class TestTestPilot:
    """Tests for TestPilot agent."""

    @pytest.mark.asyncio
    async def test_valid_resume_passes(self, ctx, valid_resume):
        """Test that valid resume passes all tests."""
        ctx.current_resume = valid_resume
        agent = TestPilot(ctx)

        await agent.execute()

        assert ctx.results["TestPilot"]["passed"] is True
        assert "TEST_FAILURE" not in ctx.signals

    @pytest.mark.asyncio
    async def test_missing_sections_fail(self, ctx):
        """Test that Missing required sections fail."""
        ctx.current_resume = {
            "contact": "email@test.com",
            # Missing summary, experience, skills
        }
        agent = TestPilot(ctx)

        await agent.execute()

        assert ctx.results["TestPilot"]["passed"] is False
        assert "TEST_FAILURE" in ctx.signals

    @pytest.mark.asyncio
    async def test_empty_resume_fails(self, ctx):
        """Test that empty resume fails."""
        ctx.current_resume = {}
        agent = TestPilot(ctx)

        await agent.execute()

        assert ctx.results["TestPilot"]["passed"] is False


class TestStrategicPlanner:
    """Tests for StrategicPlannerAgent agent."""

    @pytest.mark.asyncio
    async def test_quality_failure_strategy(self, ctx, valid_resume):
        """Test strategy for quality failure."""
        ctx.current_resume = valid_resume
        ctx.add_signal("QUALITY_FAILURE")
        agent = StrategicPlannerAgent(ctx)

        await agent.execute()

        plan = ctx.results["strategic_plan"]
        assert "QUALITY_FAILURE" in plan["priority_signals"]
        assert "ContentQualityAgent" in plan["recommended_agents"]

    @pytest.mark.asyncio
    async def test_ats_failure_strategy(self, ctx, valid_resume):
        """Test strategy for ATS failure."""
        ctx.current_resume = valid_resume
        ctx.add_signal("ATS_FAILURE")
        agent = StrategicPlannerAgent(ctx)

        await agent.execute()

        plan = ctx.results["strategic_plan"]
        assert "ATS_FAILURE" in plan["priority_signals"]
        assert "ATSCompatibilityAgent" in plan["recommended_agents"]

    @pytest.mark.asyncio
    async def test_blast_radius_tracking(self, ctx, valid_resume):
        """Test blast radius tracking."""
        ctx.current_resume = valid_resume
        ctx.impact_zone.add("skills")
        ctx.impact_zone.add("summary")
        agent = StrategicPlannerAgent(ctx)

        await agent.execute()

        plan = ctx.results["strategic_plan"]
        assert len(plan["sections_to_review"]) == 2


class TestReflectionAgent:
    """Tests for ReflectionAgent."""

    @pytest.mark.asyncio
    async def test_success_reflection(self, ctx, valid_resume):
        """Test reflection on successful execution."""
        ctx.current_resume = valid_resume
        ctx.current_cycle = 1
        ctx.record_result("Agent1", passed=True)
        ctx.record_result("Agent2", passed=True)
        agent = ReflectionAgent(ctx)

        await agent.execute()

        insights = ctx.results["reflection"]
        assert insights["outcome"] == "success"
        assert insights["converged"] is True

    @pytest.mark.asyncio
    async def test_incomplete_reflection(self, ctx, valid_resume):
        """Test reflection on incomplete execution."""
        ctx.current_resume = valid_resume
        ctx.current_cycle = 1
        ctx.add_signal("QUALITY_FAILURE")
        agent = ReflectionAgent(ctx)

        await agent.execute()

        insights = ctx.results["reflection"]
        assert insights["outcome"] == "needs_more_cycles"
        assert insights["converged"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
