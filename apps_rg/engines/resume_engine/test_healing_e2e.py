from __future__ import annotations
"""
End-to-End Tests for Phase 2: Self-Healing Mission

Tests the complete self-healing workflow:
- run_self_healing_mission() function
- Full healing cycles with real resumes
- Edge cases and error handling
"""

import pytest

from ..healing import HealingResult, run_self_healing_mission


@pytest.fixture
def valid_resume():
    """Create a valid resume for testing."""
    return {
        "summary": "Experienced software engineer with 10+ years building scalable systems. Led teams of 5-10 engineers and delivered projects that increased revenue by 25%. Expert in cloud architecture and microservices.",
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Senior Engineer",
                "description": "Developed microservices architecture serving 1M+ users. Reduced latency by 40% through optimization. Managed team of 5 engineers."
            },
            {
                "company": "StartupXYZ",
                "title": "Software Engineer",
                "description": "Built core platform features used by 100K+ customers. Improved deployment frequency by 300%."
            }
        ],
        "skills": ["Python", "JavaScript", "TypeScript", "AWS", "Docker", "Kubernetes", "PostgreSQL", "Redis"],
        "education": "BS Computer Science, MIT, 2010",
        "certifications": ["AWS Solutions Architect", "Kubernetes Administrator"],
    }


@pytest.fixture
def problematic_resume():
    """Create a resume with multiple issues."""
    return {
        "summary": "I am a developer.",
        "experience": "Worked on stuff",
        "skills": "",
    }


@pytest.fixture
def JobDescription():
    """Sample job description."""
    return """
    Senior Software Engineer

    We are looking for an experienced software engineer to join our team.

    Requirements:
    - 5+ years of experience in software development
    - Strong Python and JavaScript skills
    - Experience with AWS and cloud infrastructure
    - Experience with microservices architecture
    - Strong communication skills

    Nice to have:
    - Kubernetes experience
    - Team leadership experience
    """


class TestRunSelfHealingMission:
    """Tests for run_self_healing_mission function."""

    @pytest.mark.asyncio
    async def test_mission_with_valid_resume(self, valid_resume, JobDescription):
        """Test mission completes successfully with valid resume."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=3,
        )

        assert isinstance(result, HealingResult)
        assert result.success is True
        assert result.convergence_cycle is not None
        assert result.total_cycles <= 3
        assert "summary" in result.final_resume

    @pytest.mark.asyncio
    async def test_mission_with_problematic_resume(self, problematic_resume, JobDescription):
        """Test mission with problematic resume."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=problematic_resume,
            max_cycles=2,
        )

        assert isinstance(result, HealingResult)
        assert result.total_cycles <= 2
        # May not converge
        if not result.success:
            assert len(result.final_signals) > 0

    @pytest.mark.asyncio
    async def test_mission_with_user_profile(self, valid_resume, JobDescription):
        """Test mission with user profile for fact-checking."""
        user_profile = {
            "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"],
            "work_history": [
                {"company": "Tech Corp", "title": "Senior Engineer"},
                {"company": "StartupXYZ", "title": "Software Engineer"},
            ]
        }

        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            user_profile=user_profile,
            max_cycles=3,
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_mission_respects_max_cycles(self, problematic_resume, JobDescription):
        """Test that mission respects max_cycles limit."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=problematic_resume,
            max_cycles=1,
        )

        assert result.total_cycles == 1

    @pytest.mark.asyncio
    async def test_mission_tracks_all_cycles(self, valid_resume, JobDescription):
        """Test that mission tracks all cycle results."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=3,
        )

        assert len(result.cycle_results) > 0
        assert len(result.cycle_results) == result.total_cycles

    @pytest.mark.asyncio
    async def test_mission_with_reflection(self, valid_resume, JobDescription):
        """Test mission with reflection enabled."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
            enable_reflection=True,
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_mission_without_reflection(self, valid_resume, JobDescription):
        """Test mission with reflection disabled."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
            enable_reflection=False,
        )

        assert result.success is True


class TestSelfHealingCycles:
    """Tests for self-healing cycle behavior."""

    @pytest.mark.asyncio
    async def test_early_convergence(self, valid_resume, JobDescription):
        """Test that mission converges early when possible."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=5,
        )

        # Should converge in 1-2 cycles for valid resume
        assert result.success is True
        assert result.convergence_cycle <= 2

    @pytest.mark.asyncio
    async def test_cycle_strategies_evolve(self, valid_resume, JobDescription):
        """Test that cycle strategies evolve based on signals."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=3,
        )

        # First cycle should be full diagnostic
        from ..healing import HealingStrategy
        assert result.cycle_results[0].strategy == HealingStrategy.FULL_DIAGNOSTIC

    @pytest.mark.asyncio
    async def test_signals_tracked_per_cycle(self, valid_resume, JobDescription):
        """Test that signals are tracked per cycle."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=3,
        )

        for cycle_result in result.cycle_results:
            assert isinstance(cycle_result.signals_before, set)
            assert isinstance(cycle_result.signals_after, set)


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_resume(self, JobDescription):
        """Test handling of empty resume."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume={},
            max_cycles=2,
        )

        assert result.success is False
        assert len(result.final_signals) > 0

    @pytest.mark.asyncio
    async def test_empty_job_description(self, valid_resume):
        """Test handling of empty job description."""
        result = await run_self_healing_mission(
            JobDescription="",
            master_resume=valid_resume,
            max_cycles=2,
        )

        # Should still work without job-specific optimization
        assert isinstance(result, HealingResult)

    @pytest.mark.asyncio
    async def test_minimal_resume(self, JobDescription):
        """Test handling of minimal but valid resume."""
        minimal_resume = {
            "summary": "Software engineer with 5 years of experience in Python development. Built systems serving 100K users.",
            "experience": "Senior Developer at TechCo - Led development of core platform features, improving performance by 50%.",
            "skills": ["Python", "JavaScript", "SQL"],
        }

        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=minimal_resume,
            max_cycles=3,
        )

        assert isinstance(result, HealingResult)

    @pytest.mark.asyncio
    async def test_single_cycle_limit(self, valid_resume, JobDescription):
        """Test with single cycle limit."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=1,
        )

        assert result.total_cycles == 1


class TestHealingResultDetails:
    """Tests for HealingResult details."""

    @pytest.mark.asyncio
    async def test_result_contains_timing(self, valid_resume, JobDescription):
        """Test that result contains timing information."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        assert result.total_duration_ms > 0
        for cycle_result in result.cycle_results:
            assert cycle_result.duration_ms > 0

    @pytest.mark.asyncio
    async def test_result_contains_agent_details(self, valid_resume, JobDescription):
        """Test that result contains agent execution details."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        for cycle_result in result.cycle_results:
            assert len(cycle_result.agents_executed) > 0
            assert isinstance(cycle_result.passed_agents, list)
            assert isinstance(cycle_result.failed_agents, list)

    @pytest.mark.asyncio
    async def test_result_preserves_resume(self, valid_resume, JobDescription):
        """Test that result preserves final resume state."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        # All original sections should be present
        for section in valid_resume.keys():
            assert section in result.final_resume


class TestResumePreservation:
    """Tests for resume data preservation during healing."""

    @pytest.mark.asyncio
    async def test_original_resume_not_modified(self, valid_resume, JobDescription):
        """Test that original resume is not modified."""
        original_copy = valid_resume.copy()

        await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        # Original should be unchanged
        assert valid_resume == original_copy

    @pytest.mark.asyncio
    async def test_resume_sections_preserved(self, valid_resume, JobDescription):
        """Test that all resume sections are preserved."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        # All original sections should be present
        for section in valid_resume.keys():
            assert section in result.final_resume


class TestBudgetManagement:
    """Tests for budget management during healing."""

    @pytest.mark.asyncio
    async def test_budget_not_exhausted_normally(self, valid_resume, JobDescription):
        """Test that budget is not exhausted under normal conditions."""
        result = await run_self_healing_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=3,
        )

        assert result.budget_exhausted is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
