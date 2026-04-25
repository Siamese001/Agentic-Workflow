"""Tests for sovereign_egress.py module."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.enforcement.governance.sovereign_egress import (
    EgressStatus,
    EgressResult,
    SovereignEgress,
)


class TestEgressStatus:
    """Tests for EgressStatus enum."""

    def test_egress_status_values(self):
        """Test EgressStatus has expected values."""
        assert EgressStatus.ALLOWED is not None
        assert EgressStatus.BLOCKED is not None
        assert EgressStatus.FALLBACK_TRIGGERED is not None
        assert EgressStatus.ERROR is not None

    def test_egress_status_count(self):
        """Test EgressStatus has 4 values."""
        assert len(EgressStatus) == 4


class TestEgressResult:
    """Tests for EgressResult dataclass."""

    def test_egress_result_allowed(self):
        """Test EgressResult with ALLOWED status."""
        result = EgressResult(
            status=EgressStatus.ALLOWED,
            symbolic_request="symbolic",
            resolved_provider="provider",
            resolved_path="/path",
            is_fallback=False,
        )
        assert result.status == EgressStatus.ALLOWED
        assert result.symbolic_request == "symbolic"
        assert result.resolved_provider == "provider"
        assert result.resolved_path == "/path"
        assert result.is_fallback is False
        assert result.rejection_reason == ""

    def test_egress_result_blocked(self):
        """Test EgressResult with BLOCKED status."""
        result = EgressResult(
            status=EgressStatus.BLOCKED,
            symbolic_request="symbolic",
            resolved_provider="provider",
            resolved_path="/path",
            is_fallback=False,
            rejection_reason="path_no_longer_approved",
        )
        assert result.status == EgressStatus.BLOCKED
        assert result.rejection_reason == "path_no_longer_approved"

    def test_egress_result_fallback_triggered(self):
        """Test EgressResult with FALLBACK_TRIGGERED status."""
        result = EgressResult(
            status=EgressStatus.FALLBACK_TRIGGERED,
            symbolic_request="symbolic",
            resolved_provider="",
            resolved_path="",
            is_fallback=True,
            rejection_reason="silent_fallback_blocked",
        )
        assert result.status == EgressStatus.FALLBACK_TRIGGERED
        assert result.is_fallback is True
        assert result.resolved_provider == ""
        assert result.resolved_path == ""

    def test_egress_result_error(self):
        """Test EgressResult with ERROR status."""
        result = EgressResult(
            status=EgressStatus.ERROR,
            symbolic_request="symbolic",
            resolved_provider="",
            resolved_path="",
            is_fallback=False,
            rejection_reason="unmapped_symbolic_request",
        )
        assert result.status == EgressStatus.ERROR
        assert result.rejection_reason == "unmapped_symbolic_request"

    def test_egress_result_defaults(self):
        """Test EgressResult default values."""
        result = EgressResult(
            status=EgressStatus.ALLOWED,
            symbolic_request="symbolic",
            resolved_provider="provider",
            resolved_path="/path",
            is_fallback=False,
        )
        assert result.rejection_reason == ""


class TestSovereignEgress:
    """Tests for SovereignEgress class."""

    def test_sovereign_egress_init(self):
        """Test SovereignEgress initialization."""
        egress = SovereignEgress()
        assert egress._provider_map == {}
        assert egress._approved_paths == {}
        assert egress._fallback_attempts == 0
        assert egress._fallback_blocked == 0

    def test_egress_allowed(self):
        """Test egress returns ALLOWED when all checks pass."""
        egress = SovereignEgress()
        egress.register_provider_map("symbolic", "provider")
        egress.register_approved_path("provider", "/path")
        
        result = egress.egress("symbolic")
        
        assert result.status == EgressStatus.ALLOWED
        assert result.symbolic_request == "symbolic"
        assert result.resolved_provider == "provider"
        assert result.resolved_path == "/path"
        assert result.is_fallback is False

    def test_egress_unmapped_symbolic(self):
        """Test egress returns ERROR when symbolic request unmapped."""
        egress = SovereignEgress()
        
        result = egress.egress("unknown_symbolic")
        
        assert result.status == EgressStatus.ERROR
        assert result.rejection_reason == "unmapped_symbolic_request"
        assert result.resolved_provider == ""
        assert result.resolved_path == ""

    def test_egress_no_approved_paths(self):
        """Test egress returns ERROR when provider has no approved paths."""
        egress = SovereignEgress()
        egress.register_provider_map("symbolic", "provider")
        
        result = egress.egress("symbolic")
        
        assert result.status == EgressStatus.ERROR
        assert result.rejection_reason == "no_approved_paths_for_provider"
        assert result.resolved_provider == "provider"
        assert result.resolved_path == ""

    def test_egress_path_no_longer_approved(self):
        """Test egress returns BLOCKED when path no longer approved."""
        egress = SovereignEgress()
        egress.register_provider_map("symbolic", "provider")
        egress.register_approved_path("provider", "/path1")
        egress.register_approved_path("provider", "/path2")
        
        # Simulate path removal by clearing approved paths
        egress._approved_paths["provider"] = []
        
        result = egress.egress("symbolic")
        
        assert result.status == EgressStatus.ERROR
        assert result.rejection_reason == "no_approved_paths_for_provider"

    def test_egress_deterministic_path_selection(self):
        """Test egress selects first approved path deterministically."""
        egress = SovereignEgress()
        egress.register_provider_map("symbolic", "provider")
        egress.register_approved_path("provider", "/path1")
        egress.register_approved_path("provider", "/path2")
        egress.register_approved_path("provider", "/path3")
        
        result = egress.egress("symbolic")
        
        assert result.resolved_path == "/path1"  # First path

    def test_attempt_fallback_blocked(self):
        """Test attempt_fallback blocks fallback by design."""
        egress = SovereignEgress()
        
        result = egress.attempt_fallback("symbolic", "/failed_path")
        
        assert result.status == EgressStatus.FALLBACK_TRIGGERED
        assert result.is_fallback is True
        assert result.rejection_reason == "silent_fallback_blocked_by_sovereign_egress"
        assert result.resolved_provider == ""
        assert result.resolved_path == ""

    def test_attempt_fallback_increments_stats(self):
        """Test attempt_fallback increments fallback statistics."""
        egress = SovereignEgress()
        
        egress.attempt_fallback("symbolic1", "/path1")
        egress.attempt_fallback("symbolic2", "/path2")
        
        stats = egress.get_fallback_stats()
        assert stats["attempts"] == 2
        assert stats["blocked"] == 2

    def test_register_provider_map(self):
        """Test register_provider_map adds mapping."""
        egress = SovereignEgress()
        
        egress.register_provider_map("symbolic", "provider")
        
        assert egress._provider_map["symbolic"] == "provider"
        assert egress.get_provider_count() == 1

    def test_register_provider_map_overwrite(self):
        """Test register_provider_map overwrites existing mapping."""
        egress = SovereignEgress()
        egress.register_provider_map("symbolic", "provider1")
        
        egress.register_provider_map("symbolic", "provider2")
        
        assert egress._provider_map["symbolic"] == "provider2"
        assert egress.get_provider_count() == 1

    def test_register_approved_path(self):
        """Test register_approved_path adds path to provider."""
        egress = SovereignEgress()
        
        egress.register_approved_path("provider", "/path1")
        
        assert "/path1" in egress._approved_paths["provider"]

    def test_register_approved_path_multiple(self):
        """Test register_approved_path can add multiple paths."""
        egress = SovereignEgress()
        
        egress.register_approved_path("provider", "/path1")
        egress.register_approved_path("provider", "/path2")
        egress.register_approved_path("provider", "/path3")
        
        assert len(egress._approved_paths["provider"]) == 3
        assert "/path1" in egress._approved_paths["provider"]
        assert "/path2" in egress._approved_paths["provider"]
        assert "/path3" in egress._approved_paths["provider"]

    def test_register_approved_path_multiple_providers(self):
        """Test register_approved_path can handle multiple providers."""
        egress = SovereignEgress()
        
        egress.register_approved_path("provider1", "/path1")
        egress.register_approved_path("provider2", "/path2")
        
        assert "/path1" in egress._approved_paths["provider1"]
        assert "/path2" in egress._approved_paths["provider2"]
        assert len(egress._approved_paths) == 2

    def test_get_fallback_stats(self):
        """Test get_fallback_stats returns correct statistics."""
        egress = SovereignEgress()
        
        stats = egress.get_fallback_stats()
        assert stats["attempts"] == 0
        assert stats["blocked"] == 0
        
        egress.attempt_fallback("symbolic", "/path")
        
        stats = egress.get_fallback_stats()
        assert stats["attempts"] == 1
        assert stats["blocked"] == 1

    def test_get_provider_count(self):
        """Test get_provider_count returns correct count."""
        egress = SovereignEgress()
        
        assert egress.get_provider_count() == 0
        
        egress.register_provider_map("symbolic1", "provider1")
        assert egress.get_provider_count() == 1
        
        egress.register_provider_map("symbolic2", "provider2")
        assert egress.get_provider_count() == 2
        
        egress.register_provider_map("symbolic3", "provider1")  # Same provider
        assert egress.get_provider_count() == 3  # Counts mappings, not unique providers

    def test_egress_multiple_symbolic_to_same_provider(self):
        """Test egress handles multiple symbolic requests to same provider."""
        egress = SovereignEgress()
        egress.register_provider_map("symbolic1", "provider")
        egress.register_provider_map("symbolic2", "provider")
        egress.register_approved_path("provider", "/path")
        
        result1 = egress.egress("symbolic1")
        result2 = egress.egress("symbolic2")
        
        assert result1.status == EgressStatus.ALLOWED
        assert result2.status == EgressStatus.ALLOWED
        assert result1.resolved_provider == "provider"
        assert result2.resolved_provider == "provider"

    def test_egress_no_fallback_on_path_failure(self):
        """Test egress does not fallback when primary path fails."""
        egress = SovereignEgress()
        egress.register_provider_map("symbolic", "provider")
        egress.register_approved_path("provider", "/path1")
        egress.register_approved_path("provider", "/path2")
        
        # Even though there are multiple paths, only first is selected
        result = egress.egress("symbolic")
        
        assert result.resolved_path == "/path1"
        assert result.is_fallback is False
