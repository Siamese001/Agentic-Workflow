"""Behavioral tests for VerificationGate + NamingAgent stub."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L5_safety.enforcement.verification_gate import VerificationGate
from agentic_core.L5_safety.reasoning.NamingAgent import (
    NamingAgent,
    PlacementResult,
)


# ============================================================================
# VerificationGate
# ============================================================================


class TestVerificationGateConstruction:
    def test_default_no_context_manager(self) -> None:
        gate = VerificationGate()
        assert gate.context_manager is None

    def test_custom_context_manager_stored(self) -> None:
        sentinel = object()
        gate = VerificationGate(context_manager=sentinel)
        assert gate.context_manager is sentinel

    def test_verification_cache_empty(self) -> None:
        gate = VerificationGate()
        assert gate.verification_cache == {}


class TestVerificationGateCache:
    def test_clear_cache_empties_dict(self) -> None:
        gate = VerificationGate()
        gate.verification_cache["/x.py::mod::foo"] = True
        gate.clear_cache()
        assert gate.verification_cache == {}

    def test_get_cache_stats_shape(self) -> None:
        gate = VerificationGate()
        stats = gate.get_cache_stats()
        assert "cache_size" in stats
        assert "cache_keys" in stats
        assert stats["cache_size"] == 0
        assert stats["cache_keys"] == []

    def test_get_cache_stats_reflects_content(self) -> None:
        gate = VerificationGate()
        gate.verification_cache["k1"] = True
        gate.verification_cache["k2"] = False
        stats = gate.get_cache_stats()
        assert stats["cache_size"] == 2
        assert set(stats["cache_keys"]) == {"k1", "k2"}


class TestVerificationGateVerifyAction:
    def test_missing_file_rejected(self, tmp_path: Path) -> None:
        gate = VerificationGate()
        # verify_action on a non-existent file should not crash and should
        # return False (the target_node cannot exist in a missing file).
        result = gate.verify_action(
            tmp_path / "missing.py", "modify", "some_func",
        )
        assert result is False


# ============================================================================
# NamingAgent (stub)
# ============================================================================


class TestPlacementResult:
    def test_defaults(self) -> None:
        r = PlacementResult()
        assert r.path == ""
        assert r.confidence == 1.0
        assert r.suggestions == []

    def test_custom(self) -> None:
        r = PlacementResult(path="/a/b.py", confidence=0.5)
        assert r.path == "/a/b.py"
        assert r.confidence == 0.5


class TestNamingAgent:
    def test_construct_without_args(self) -> None:
        agent = NamingAgent()
        assert agent is not None

    def test_construct_with_args_and_kwargs_swallowed(self) -> None:
        # Stub accepts anything
        agent = NamingAgent("x", 1, foo="bar")
        assert agent is not None

    def test_validate_name_returns_true(self) -> None:
        agent = NamingAgent()
        assert agent.validate_name("anything") is True

    def test_suggest_name_is_identity(self) -> None:
        agent = NamingAgent()
        assert agent.suggest_name("my_context") == "my_context"

    def test_analyze_placement_returns_placement_result(self) -> None:
        agent = NamingAgent()
        result = agent.analyze_placement("code")
        assert isinstance(result, PlacementResult)

    def test_validate_prefix_location_match_returns_empty_list(
        self, tmp_path: Path,
    ) -> None:
        agent = NamingAgent()
        assert agent.validate_prefix_location_match(tmp_path / "x.py") == []

    def test_scan_repository_duplicates_returns_empty_dict(self) -> None:
        agent = NamingAgent()
        assert agent.scan_repository_duplicates() == {}

    def test_move_to_canonical_location_reports_stub(
        self, tmp_path: Path,
    ) -> None:
        agent = NamingAgent()
        result = agent.move_to_canonical_location(tmp_path / "x.py")
        assert result["moved"] is False
        assert "Stub" in result["reason"]

    def test_heal_with_target(self) -> None:
        agent = NamingAgent()
        result = agent.heal({"file": "x.py"})
        # Stub implementation returns something with at minimum some status
        assert isinstance(result, dict)

