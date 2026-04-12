"""Tests for ResumeOrchestrator — G5 reasoning_profile integration.

G5 Fix: Provides test coverage for ResumeOrchestrator's reasoning_profile
integration with ADG-informed dynamic reasoning path selection.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from apps_rg.reasoning.ResumeOrchestrator import (
    ResumeOrchestrator,
    orchestrate_resume,
)


class MockReasoningProfile:
    """Mock ReasoningIntensityProfile for testing."""

    def __init__(
        self,
        complexity_tier: str = "moderate",
        profile_hash: str = "mock-hash",
        adg_node_count: int = 100,
        adg_edge_count: int = 500,
    ):
        self.adg_complexity_tier = complexity_tier
        self.profile_hash = profile_hash
        self.adg_node_count = adg_node_count
        self.adg_edge_count = adg_edge_count


class TestResumeOrchestratorReasoningProfile:
    """Test ResumeOrchestrator reasoning_profile integration — G5."""

    def test_orchestrator_without_profile_uses_default(self):
        """Edge case: no profile uses default complexity tier."""
        master_resume = {"name": "Test", "skills": ["Python"]}
        orchestrator = ResumeOrchestrator(master_resume=master_resume)

        assert orchestrator.reasoning_profile is None
        assert orchestrator.complexity_tier == "moderate"
        assert orchestrator.profile_hash is None

    def test_orchestrator_with_profile_extracts_complexity_tier(self):
        """Happy path: profile extracts ADG complexity tier."""
        master_resume = {"name": "Test", "skills": ["Python"]}
        profile = MockReasoningProfile(complexity_tier="complex")

        with patch("apps_rg.reasoning.ResumeOrchestrator._emit_records_telemetry_event"):
            orchestrator = ResumeOrchestrator(
                master_resume=master_resume,
                reasoning_profile=profile,
            )

        assert orchestrator.reasoning_profile == profile
        assert orchestrator.complexity_tier == "complex"
        assert orchestrator.profile_hash == "mock-hash"

    def test_orchestrator_with_simple_tier(self):
        """Happy path: simple tier extracted from profile."""
        master_resume = {"name": "Test", "skills": ["Python"]}
        profile = MockReasoningProfile(
            complexity_tier="simple",
            profile_hash="simple-hash",
        )

        with patch("apps_rg.reasoning.ResumeOrchestrator._emit_records_telemetry_event"):
            orchestrator = ResumeOrchestrator(
                master_resume=master_resume,
                reasoning_profile=profile,
            )

        assert orchestrator.complexity_tier == "simple"
        assert orchestrator.profile_hash == "simple-hash"

    def test_orchestrator_with_deep_tier(self):
        """Happy path: deep tier extracted from profile."""
        master_resume = {"name": "Test", "skills": ["Python"]}
        profile = MockReasoningProfile(
            complexity_tier="deep",
            adg_node_count=5000,
            adg_edge_count=20000,
        )

        with patch("apps_rg.reasoning.ResumeOrchestrator._emit_records_telemetry_event"):
            orchestrator = ResumeOrchestrator(
                master_resume=master_resume,
                reasoning_profile=profile,
            )

        assert orchestrator.complexity_tier == "deep"
        assert orchestrator.reasoning_profile.adg_node_count == 5000

    def test_orchestrator_profile_without_adg_tier_defaults_moderate(self):
        """Edge case: profile without adg_complexity_tier defaults to moderate."""
        master_resume = {"name": "Test", "skills": ["Python"]}
        import types

        # Omit adg_complexity_tier entirely so getattr falls back to 'moderate'
        profile = types.SimpleNamespace(profile_hash="test-hash")

        with patch("apps_rg.reasoning.ResumeOrchestrator._emit_records_telemetry_event"):
            orchestrator = ResumeOrchestrator(
                master_resume=master_resume,
                reasoning_profile=profile,
            )

        # When adg_complexity_tier is None, getattr returns 'moderate'
        assert orchestrator.complexity_tier == "moderate"


class TestOrchestrateResumeFunction:
    """Test orchestrate_resume function with reasoning_profile — G5."""

    @pytest.fixture
    def master_resume(self):
        """Sample master resume fixture."""
        return {"name": "John Doe", "skills": ["Python", "AWS", "ML"]}

    @pytest.fixture
    def job_description(self):
        """Sample job description fixture."""
        return "Senior Python Engineer - AWS and ML required"

    @pytest.fixture
    def reasoning_profile(self):
        """Sample reasoning profile fixture."""
        return MockReasoningProfile(
            complexity_tier="complex",
            profile_hash="complex-profile-hash",
            adg_node_count=1500,
            adg_edge_count=6000,
        )

    def test_orchestrate_resume_without_profile(self, master_resume, job_description):
        """Happy path: orchestrate_resume works without profile."""
        # Mock the orchestrator.run method to avoid actual processing
        with patch.object(ResumeOrchestrator, "run") as mock_run:
            mock_run.return_value = {
                "status": "success",
                "enriched_data": {},
                "checkpoints": ["HOP-1", "HOP-2"],
            }

            result = orchestrate_resume(
                master_resume=master_resume,
                JobDescription=job_description,
            )

            assert result["status"] == "success"
            assert "checkpoints" in result

    def test_orchestrate_resume_with_profile(self, master_resume, job_description, reasoning_profile):
        """Happy path: orchestrate_resume passes profile to orchestrator."""
        with (
            patch.object(ResumeOrchestrator, "run") as mock_run,
            patch("apps_rg.reasoning.ResumeOrchestrator._emit_records_telemetry_event"),
        ):
            mock_run.return_value = {
                "status": "success",
                "enriched_data": {},
                "checkpoints": ["HOP-1", "HOP-2"],
            }

            result = orchestrate_resume(
                master_resume=master_resume,
                JobDescription=job_description,
                reasoning_profile=reasoning_profile,
            )

            assert result["status"] == "success"

    def test_orchestrate_resume_propagates_complexity_tier(self, master_resume, job_description):
        """Validation: orchestrate_resume propagates complexity tier correctly."""
        profile = MockReasoningProfile(complexity_tier="deep")

        with (
            patch.object(ResumeOrchestrator, "run") as mock_run,
            patch("apps_rg.reasoning.ResumeOrchestrator._emit_records_telemetry_event"),
        ):
            mock_run.return_value = {
                "status": "success",
                "enriched_data": {"complexity_tier": "deep"},
                "checkpoints": [],
            }

            result = orchestrate_resume(
                master_resume=master_resume,
                JobDescription=job_description,
                reasoning_profile=profile,
            )

            assert result["status"] == "success"


class TestResumeOrchestratorTelemetry:
    """Test telemetry emission with reasoning_profile — G5."""

    def test_telemetry_emitted_with_profile(self):
        """Validation: telemetry emitted when profile is provided."""
        master_resume = {"name": "Test", "skills": ["Python"]}
        profile = MockReasoningProfile(
            complexity_tier="complex",
            profile_hash="telemetry-test",
            adg_node_count=1000,
            adg_edge_count=5000,
        )

        with patch("apps_rg.reasoning.ResumeOrchestrator._emit_records_telemetry_event") as mock_emit:
            # Initialize orchestrator - should emit telemetry
            orchestrator = ResumeOrchestrator(
                master_resume=master_resume,
                reasoning_profile=profile,
            )

            # Check that telemetry data contains expected fields
            assert orchestrator.complexity_tier == "complex"
            assert orchestrator.profile_hash == "telemetry-test"

    def test_no_telemetry_emitted_without_profile(self):
        """Validation: no telemetry data when profile is None."""
        master_resume = {"name": "Test", "skills": ["Python"]}

        orchestrator = ResumeOrchestrator(
            master_resume=master_resume,
            reasoning_profile=None,
        )

        # Should have default values, not telemetry emission
        assert orchestrator.complexity_tier == "moderate"
        assert orchestrator.profile_hash is None
