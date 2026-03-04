"""Unit tests for FailureSignalNormalizer — determinism and contract proofs."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.healers.failure_signal_normalizer import (
    extract_failure_metadata,
    normalize_failure_signal,
)


class TestNormalizeFailureSignal:
    """normalize_failure_signal contract tests."""

    def test_full_action_produces_expected_text(self) -> None:
        action = {
            "type": "IMPORT_BOUNDARY_VIOLATION",
            "agent": "DependencyRepairAgent",
            "fix_summary": "yaml config loader",
        }
        result = normalize_failure_signal(action)
        assert result == "IMPORT_BOUNDARY_VIOLATION DependencyRepairAgent yaml config loader"

    def test_failure_type_uppercased(self) -> None:
        action = {"type": "layer_violation", "agent": "ArchGovernor"}
        result = normalize_failure_signal(action)
        assert result.startswith("LAYER_VIOLATION")

    def test_falls_back_to_routing_tier_when_type_missing(self) -> None:
        action = {"routing_tier": "DETERMINISTIC", "agent": "TestRepairAgent"}
        result = normalize_failure_signal(action)
        assert "DETERMINISTIC" in result
        assert "TestRepairAgent" in result

    def test_unknown_when_no_type_fields(self) -> None:
        action = {"agent": "SomeAgent"}
        result = normalize_failure_signal(action)
        assert "UNKNOWN" in result
        assert "SomeAgent" in result

    def test_empty_fix_summary_omitted(self) -> None:
        action = {"type": "LAYER_VIOLATION", "agent": "GovernorAgent", "fix_summary": ""}
        result = normalize_failure_signal(action)
        assert result == "LAYER_VIOLATION GovernorAgent"

    def test_missing_agent_uses_default(self) -> None:
        action = {"type": "GATEWAY_BYPASS"}
        result = normalize_failure_signal(action)
        assert "GATEWAY_BYPASS" in result
        assert "unknown_agent" in result

    def test_deterministic_identical_inputs(self) -> None:
        action = {"type": "LAYER_VIOLATION", "agent": "TestAgent", "fix_summary": "fixed"}
        assert normalize_failure_signal(action) == normalize_failure_signal(action)

    def test_empty_action_does_not_raise(self) -> None:
        result = normalize_failure_signal({})
        assert isinstance(result, str)
        assert len(result) > 0

    def test_whitespace_stripped(self) -> None:
        action = {"type": "  LAYER_VIOLATION  ", "agent": "  Agent  "}
        result = normalize_failure_signal(action)
        assert "  " not in result


class TestExtractFailureMetadata:
    """extract_failure_metadata contract tests — metadata is kept separate from embedding text."""

    def test_all_fields_captured(self) -> None:
        action = {
            "territory": "L5_safety",
            "routing_digest": "abc123",
            "confidence": 0.85,
            "routing_tier": "DETERMINISTIC",
            "outcome": "SUCCESS",
            "timestamp": "2026-01-01T00:00:00",
        }
        meta = extract_failure_metadata(action)
        assert meta["territory"] == "L5_safety"
        assert meta["routing_digest"] == "abc123"
        assert meta["confidence_score"] == 0.85
        assert meta["routing_tier"] == "DETERMINISTIC"
        assert meta["outcome"] == "SUCCESS"
        assert meta["timestamp"] == "2026-01-01T00:00:00"

    def test_missing_fields_default_to_none_or_unknown(self) -> None:
        meta = extract_failure_metadata({})
        assert meta["territory"] == "unknown"
        assert meta["routing_digest"] is None
        assert meta["confidence_score"] is None

    def test_metadata_does_not_include_embedding_fields(self) -> None:
        action = {"type": "LAYER_VIOLATION", "agent": "Healer", "fix_summary": "fixed"}
        meta = extract_failure_metadata(action)
        assert "type" not in meta
        assert "agent" not in meta
        assert "fix_summary" not in meta
