from __future__ import annotations
"""
End-to-End Tests for Autonomous Resume Engine

Tests the complete mission workflow:
- run_resume_mission() orchestration
- Self-healing cycles
- Convergence detection
- Full workflow scenarios
"""

import pytest

from ..orchestrator import quick_validate, run_resume_mission


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
        "summary": "I am a developer.",  # Too short, first person
        "experience": "Worked on stuff",  # No quantification, vague
        "skills": "",  # Empty
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


class TestRunResumeMission:
    """Tests for run_resume_mission orchestrator."""

    @pytest.mark.asyncio
    async def test_mission_with_valid_resume(self, valid_resume, JobDescription):
        """Test mission completes successfully with valid resume."""
        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=3,
        )

        assert result["status"] == "success"
        assert result["converged"] is True
        assert result["cycles_used"] <= 3
        assert "resume" in result
        assert "stats" in result

    @pytest.mark.asyncio
    async def test_mission_with_problematic_resume(self, problematic_resume, JobDescription):
        """Test mission detects issues with problematic resume."""
        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=problematic_resume,
            max_cycles=2,
        )

        # May not converge due to issues
        assert "status" in result
        assert "resume" in result
        assert "stats" in result

        # Should have detected signals
        stats = result["stats"]
        assert len(stats["signals"]) > 0 or not result["converged"]

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

        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            user_profile=user_profile,
            max_cycles=3,
        )

        assert result["status"] == "success"
        assert result["converged"] is True

    @pytest.mark.asyncio
    async def test_mission_respects_max_cycles(self, problematic_resume, JobDescription):
        """Test that mission respects max_cycles limit."""
        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=problematic_resume,
            max_cycles=1,
        )

        assert result["cycles_used"] == 1

    @pytest.mark.asyncio
    async def test_mission_tracks_budget(self, valid_resume, JobDescription):
        """Test that mission tracks budget usage."""
        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        stats = result["stats"]
        assert "budget_stats" in stats
        assert "current_cost_usd" in stats["budget_stats"]


class TestQuickValidate:
    """Tests for quick_validate function."""

    @pytest.mark.asyncio
    async def test_quick_validate_valid_resume(self, valid_resume, JobDescription):
        """Test quick validation of valid resume."""
        result = await quick_validate(
            resume=valid_resume,
            JobDescription=JobDescription,
        )

        assert result["valid"] is True
        assert "results" in result
        assert "signals" in result

    @pytest.mark.asyncio
    async def test_quick_validate_invalid_resume(self, problematic_resume):
        """Test quick validation of invalid resume."""
        result = await quick_validate(
            resume=problematic_resume,
            JobDescription="Software Engineer",
        )

        assert result["valid"] is False
        assert len(result["signals"]) > 0

    @pytest.mark.asyncio
    async def test_quick_validate_no_job_description(self, valid_resume):
        """Test quick validation without job description."""
        result = await quick_validate(
            resume=valid_resume,
            JobDescription="",
        )

        assert "valid" in result
        assert "results" in result


class TestSelfHealingCycles:
    """Tests for self-healing cycle behavior."""

    @pytest.mark.asyncio
    async def test_early_convergence(self, valid_resume, JobDescription):
        """Test that mission converges early when possible."""
        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=5,
        )

        # Should converge in 1-2 cycles for valid resume
        assert result["converged"] is True
        assert result["cycles_used"] <= 2

    @pytest.mark.asyncio
    async def test_signal_based_routing(self, valid_resume, JobDescription):
        """Test that signals influence agent routing."""
        # This is tested implicitly through the mission
        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=3,
        )

        # Stats should show signal activity
        stats = result["stats"]
        assert "signals" in stats


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_resume(self, JobDescription):
        """Test handling of empty resume."""
        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume={},
            max_cycles=2,
        )

        assert result["status"] == "incomplete"
        assert not result["converged"]

    @pytest.mark.asyncio
    async def test_empty_job_description(self, valid_resume):
        """Test handling of empty job description."""
        result = await run_resume_mission(
            JobDescription="",
            master_resume=valid_resume,
            max_cycles=2,
        )

        # Should still work, just without job-specific optimization
        assert "status" in result
        assert "resume" in result

    @pytest.mark.asyncio
    async def test_minimal_resume(self, JobDescription):
        """Test handling of minimal but valid resume."""
        minimal_resume = {
            "summary": "Software engineer with 5 years of experience in Python development. Built systems serving 100K users.",
            "experience": "Senior Developer at TechCo - Led development of core platform features, improving performance by 50%.",
            "skills": ["Python", "JavaScript", "SQL"],
        }

        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=minimal_resume,
            max_cycles=3,
        )

        assert "status" in result
        assert "resume" in result


class TestStatisticsAndReporting:
    """Tests for statistics and reporting."""

    @pytest.mark.asyncio
    async def test_stats_completeness(self, valid_resume, JobDescription):
        """Test that stats are complete."""
        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        stats = result["stats"]

        # Check all expected stat categories
        assert "generation_stats" in stats
        assert "budget_stats" in stats
        assert "current_cycle" in stats
        assert "signals" in stats
        assert "modified_sections" in stats
        assert "impact_zone" in stats
        assert "failed_agents" in stats

    @pytest.mark.asyncio
    async def test_budget_stats_accuracy(self, valid_resume, JobDescription):
        """Test budget stats are accurate."""
        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        budget_stats = result["stats"]["budget_stats"]

        assert budget_stats["current_cost_usd"] >= 0
        assert budget_stats["max_cost_usd"] == 2.0
        assert budget_stats["remaining_usd"] <= 2.0
        assert budget_stats["call_count"] >= 0


class TestResumePreservation:
    """Tests for resume data preservation."""

    @pytest.mark.asyncio
    async def test_original_resume_not_modified(self, valid_resume, JobDescription):
        """Test that original resume is not modified."""
        original_copy = valid_resume.copy()

        await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        # Original should be unchanged
        assert valid_resume == original_copy

    @pytest.mark.asyncio
    async def test_resume_sections_preserved(self, valid_resume, JobDescription):
        """Test that all resume sections are preserved."""
        result = await run_resume_mission(
            JobDescription=JobDescription,
            master_resume=valid_resume,
            max_cycles=2,
        )

        output_resume = result["resume"]

        # All original sections should be present
        for section in valid_resume.keys():
            assert section in output_resume


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
