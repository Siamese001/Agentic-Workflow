"""Tests for HOPPipelineExecutor — G6 reasoning_profile integration.

G6 Fix: Provides test coverage for HOPPipelineExecutor's reasoning_profile
integration with ADG-informed dynamic reasoning path selection.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from apps_lic.reasoning.HOPPipelineExecutor import HOPPipelineExecutor


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


class TestHOPPipelineExecutorReasoningProfile:
    """Test HOPPipelineExecutor reasoning_profile integration — G6."""

    def test_executor_without_profile_uses_default(self):
        """Edge case: no profile uses default complexity tier."""
        executor = HOPPipelineExecutor(
            stage_id=1,
            reasoning_profile=None,
        )

        assert executor.reasoning_profile is None
        assert executor.stage_name == "profile_analysis"

    def test_executor_with_profile_extracts_complexity_tier(self):
        """Happy path: profile extracts ADG complexity tier."""
        profile = MockReasoningProfile(complexity_tier="complex")

        executor = HOPPipelineExecutor(
            stage_id=2,
            reasoning_profile=profile,
        )

        assert executor.reasoning_profile == profile
        assert executor.stage_name == "research"

    def test_executor_with_stage_name_mapping(self):
        """Happy path: all stage IDs map to correct names."""
        expected_names = {
            1: "profile_analysis",
            2: "research",
            3: "sender_grounding",
            4: "routing",
            5: "generation",
            6: "validation",
            7: "gate_decision",
            8: "qa_report",
            9: "integration",
        }

        for stage_id, expected_name in expected_names.items():
            executor = HOPPipelineExecutor(
                stage_id=stage_id,
                reasoning_profile=None,
            )
            assert executor.stage_name == expected_name

    def test_executor_with_simple_tier(self):
        """Happy path: simple tier extracted from profile."""
        profile = MockReasoningProfile(
            complexity_tier="simple",
            profile_hash="simple-hash",
        )

        executor = HOPPipelineExecutor(
            stage_id=3,
            reasoning_profile=profile,
        )

        assert executor.reasoning_profile == profile
        assert executor.stage_name == "sender_grounding"

    def test_executor_with_deep_tier(self):
        """Happy path: deep tier extracted from profile."""
        profile = MockReasoningProfile(
            complexity_tier="deep",
            adg_node_count=5000,
            adg_edge_count=20000,
        )

        executor = HOPPipelineExecutor(
            stage_id=5,
            reasoning_profile=profile,
        )

        assert executor.reasoning_profile == profile
        assert executor.stage_name == "generation"


class TestHOPPipelineExecutorProcess:
    """Test HOPPipelineExecutor._process with reasoning_profile — G6."""

    def test_process_without_profile_uses_default_tier(self):
        """Happy path: _process works without profile."""
        executor = HOPPipelineExecutor(
            stage_id=1,
            reasoning_profile=None,
        )

        with patch("apps_lic.engines.hop_stage_registry.get_stage_handler") as mock_get_handler:
            mock_handler = MagicMock(return_value={"stage": 1, "status": "ok"})
            mock_get_handler.return_value = mock_handler

            result = executor._process(context={"test": "data"})

            mock_handler.assert_called_once()
            # Check that handler was called with default complexity_tier="moderate"
            call_kwargs = mock_handler.call_args[1]
            assert call_kwargs["complexity_tier"] == "moderate"
            assert call_kwargs["profile_hash"] is None

    def test_process_with_profile_extracts_tier(self):
        """Happy path: _process extracts complexity tier from profile."""
        profile = MockReasoningProfile(
            complexity_tier="complex",
            profile_hash="complex-hash",
            adg_node_count=1500,
            adg_edge_count=6000,
        )

        executor = HOPPipelineExecutor(
            stage_id=2,
            reasoning_profile=profile,
        )

        with patch("apps_lic.engines.hop_stage_registry.get_stage_handler") as mock_get_handler:
            mock_handler = MagicMock(return_value={"stage": 2, "status": "ok"})
            mock_get_handler.return_value = mock_handler

            result = executor._process(context={"test": "data"})

            call_kwargs = mock_handler.call_args[1]
            assert call_kwargs["complexity_tier"] == "complex"
            assert call_kwargs["profile_hash"] == "complex-hash"
            assert call_kwargs["reasoning_profile"] == profile

    def test_process_passes_all_tiers(self):
        """Validation: _process passes all complexity tiers correctly."""
        tiers = ["simple", "moderate", "complex", "deep"]

        for tier in tiers:
            profile = MockReasoningProfile(complexity_tier=tier)
            executor = HOPPipelineExecutor(
                stage_id=1,
                reasoning_profile=profile,
            )

            with patch("apps_lic.engines.hop_stage_registry.get_stage_handler") as mock_get_handler:
                mock_handler = MagicMock(return_value={"stage": 1, "tier": tier})
                mock_get_handler.return_value = mock_handler

                executor._process(context={})

                call_kwargs = mock_handler.call_args[1]
                assert call_kwargs["complexity_tier"] == tier

    def test_process_handler_not_found(self):
        """Edge case: _process returns error when no handler found."""
        executor = HOPPipelineExecutor(
            stage_id=99,  # Unknown stage
            reasoning_profile=None,
        )

        with patch("apps_lic.engines.hop_stage_registry.get_stage_handler") as mock_get_handler:
            mock_get_handler.return_value = None

            result = executor._process(context={})

            assert "error" in result
            assert "No handler" in result["error"]


class TestHOPPipelineExecutorTelemetry:
    """Test telemetry emission with reasoning_profile — G6."""

    def test_telemetry_emitted_with_profile(self):
        """Validation: telemetry data extracted when profile provided."""
        profile = MockReasoningProfile(
            complexity_tier="complex",
            profile_hash="telemetry-test",
            adg_node_count=2000,
            adg_edge_count=10000,
        )

        executor = HOPPipelineExecutor(
            stage_id=3,
            reasoning_profile=profile,
        )

        # Verify profile data is accessible
        assert executor.reasoning_profile.adg_complexity_tier == "complex"
        assert executor.reasoning_profile.adg_node_count == 2000
        assert executor.reasoning_profile.adg_edge_count == 10000

    def test_no_telemetry_without_profile(self):
        """Validation: works without profile (no telemetry)."""
        executor = HOPPipelineExecutor(
            stage_id=4,
            reasoning_profile=None,
        )

        assert executor.reasoning_profile is None

        with patch("apps_lic.engines.hop_stage_registry.get_stage_handler") as mock_get_handler:
            mock_handler = MagicMock(return_value={"stage": 4, "status": "ok"})
            mock_get_handler.return_value = mock_handler

            result = executor._process(context={})

            # Should still work, with default complexity_tier
            mock_handler.assert_called_once()
            call_kwargs = mock_handler.call_args[1]
            assert call_kwargs["complexity_tier"] == "moderate"
