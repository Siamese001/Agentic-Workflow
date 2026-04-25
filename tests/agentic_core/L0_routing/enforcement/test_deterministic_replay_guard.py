"""Tests for deterministic_replay_guard.py module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.enforcement.deterministic_replay_guard import (
    DeterminismViolation,
    ReplayVerificationResult,
    DeterministicReplayGuard,
    get_replay_guard,
    reset_replay_guard,
)
from agentic_core.L0_routing.reasoning.deterministic_routing_gateway import RoutingArtifact


class TestReplayVerificationResult:
    """Tests for ReplayVerificationResult dataclass."""

    def test_replay_verification_result_passed(self):
        """Test ReplayVerificationResult with passed=True."""
        artifact = MagicMock(spec=RoutingArtifact)
        result = ReplayVerificationResult(
            artifact=artifact,
            expected_replay_key="expected_key",
            actual_replay_key="expected_key",
            passed=True,
        )
        assert result.passed is True
        assert result.mismatch_summary == "PASS"

    def test_replay_verification_result_failed(self):
        """Test ReplayVerificationResult with passed=False."""
        artifact = MagicMock(spec=RoutingArtifact)
        result = ReplayVerificationResult(
            artifact=artifact,
            expected_replay_key="expected_key",
            actual_replay_key="actual_key",
            passed=False,
        )
        assert result.passed is False
        assert "MISMATCH" in result.mismatch_summary


class TestDeterministicReplayGuard:
    """Tests for DeterministicReplayGuard class."""

    def test_replay_guard_init_default(self):
        """Test DeterministicReplayGuard initialization with default replay_mode."""
        guard = DeterministicReplayGuard()
        assert guard.replay_mode is False

    def test_replay_guard_init_replay_mode_true(self):
        """Test DeterministicReplayGuard initialization with replay_mode=True."""
        guard = DeterministicReplayGuard(replay_mode=True)
        assert guard.replay_mode is True

    def test_verify_routing_replay_passed(self):
        """Test verify_routing_replay when verification passes."""
        guard = DeterministicReplayGuard(replay_mode=False)
        artifact = MagicMock(spec=RoutingArtifact)
        artifact.route_path = "R3_GROUNDED"
        artifact.policy_config_hash = "hash1"
        artifact.trace_id = "trace-123"
        artifact.replay_key = "expected_key"
        
        with patch("agentic_core.L0_routing.enforcement.deterministic_replay_guard.get_routing_gateway") as mock_get_gw:
            gw = MagicMock()
            gw.verify_replay.return_value = True
            mock_get_gw.return_value = gw
            
            result = guard.verify_routing_replay(artifact)
            
            assert result.passed is True

    def test_verify_routing_replay_failed_no_replay_mode(self):
        """Test verify_routing_replay when verification fails but replay_mode=False."""
        guard = DeterministicReplayGuard(replay_mode=False)
        artifact = MagicMock(spec=RoutingArtifact)
        artifact.route_path = "R3_GROUNDED"
        artifact.policy_config_hash = "hash1"
        artifact.trace_id = "trace-123"
        artifact.replay_key = "actual_key"
        
        with patch("agentic_core.L0_routing.enforcement.deterministic_replay_guard.get_routing_gateway") as mock_get_gw:
            gw = MagicMock()
            gw.verify_replay.return_value = False
            mock_get_gw.return_value = gw
            
            result = guard.verify_routing_replay(artifact)
            
            assert result.passed is False
            # Should not raise when replay_mode=False

    def test_verify_routing_replay_failed_with_replay_mode(self):
        """Test verify_routing_replay raises DeterminismViolation when replay_mode=True."""
        guard = DeterministicReplayGuard(replay_mode=True)
        artifact = MagicMock(spec=RoutingArtifact)
        artifact.route_path = "R3_GROUNDED"
        artifact.policy_config_hash = "hash1"
        artifact.trace_id = "trace-123"
        artifact.replay_key = "actual_key"
        
        with patch("agentic_core.L0_routing.enforcement.deterministic_replay_guard.get_routing_gateway") as mock_get_gw:
            gw = MagicMock()
            gw.verify_replay.return_value = False
            mock_get_gw.return_value = gw
            
            with pytest.raises(DeterminismViolation, match="Routing replay verification failed"):
                guard.verify_routing_replay(artifact)

    def test_verify_routing_replay_failed_fail_closed_false(self):
        """Test verify_routing_replay with fail_closed=False does not raise."""
        guard = DeterministicReplayGuard(replay_mode=True)
        artifact = MagicMock(spec=RoutingArtifact)
        artifact.route_path = "R3_GROUNDED"
        artifact.policy_config_hash = "hash1"
        artifact.trace_id = "trace-123"
        artifact.replay_key = "actual_key"
        
        with patch("agentic_core.L0_routing.enforcement.deterministic_replay_guard.get_routing_gateway") as mock_get_gw:
            gw = MagicMock()
            gw.verify_replay.return_value = False
            mock_get_gw.return_value = gw
            
            result = guard.verify_routing_replay(artifact, fail_closed=False)
            
            assert result.passed is False
            # Should not raise when fail_closed=False

    def test_verify_routing_replay_stamps_decision(self):
        """Test verify_routing_replay calls stamp_decision on gateway."""
        guard = DeterministicReplayGuard(replay_mode=False)
        artifact = MagicMock(spec=RoutingArtifact)
        artifact.route_path = "R3_GROUNDED"
        artifact.policy_config_hash = "hash1"
        artifact.trace_id = "trace-123"
        artifact.replay_key = "expected_key"
        
        with patch("agentic_core.L0_routing.enforcement.deterministic_replay_guard.get_routing_gateway") as mock_get_gw:
            gw = MagicMock()
            gw.verify_replay.return_value = True
            mock_get_gw.return_value = gw
            
            guard.verify_routing_replay(artifact)
            
            gw.stamp_decision.assert_called_once()


class TestGetReplayGuard:
    """Tests for get_replay_guard function."""

    def test_get_replay_guard_creates_singleton(self):
        """Test get_replay_guard creates singleton instance."""
        reset_replay_guard()
        guard1 = get_replay_guard(replay_mode=False)
        guard2 = get_replay_guard(replay_mode=False)
        assert guard1 is guard2

    def test_get_replay_guard_with_replay_mode(self):
        """Test get_replay_guard with replay_mode parameter."""
        reset_replay_guard()
        guard = get_replay_guard(replay_mode=True)
        assert guard.replay_mode is True


class TestResetReplayGuard:
    """Tests for reset_replay_guard function."""

    def test_reset_replay_guard_clears_singleton(self):
        """Test reset_replay_guard clears global singleton."""
        guard1 = get_replay_guard(replay_mode=False)
        reset_replay_guard()
        guard2 = get_replay_guard(replay_mode=True)
        # After reset, the guard should be recreated with new mode
        assert guard1 is not guard2
        assert guard2.replay_mode is True

    def test_reset_replay_guard_idempotent(self):
        """Test reset_replay_guard can be called multiple times."""
        reset_replay_guard()
        reset_replay_guard()
        reset_replay_guard()
        # Should not raise any errors
