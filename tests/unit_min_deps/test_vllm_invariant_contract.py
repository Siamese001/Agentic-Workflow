"""
Unit tests for vLLM invariant contract (minimal dependencies).

Tests invariant violation deterministic serialization and hashing.
"""

import json

import pytest

from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
    InvariantId,
    InvariantSeverity,
    InvariantViolation,
)

pytestmark = pytest.mark.unit_min_deps


def test_invariant_violation_canonical_json_stable():
    """Test that canonical JSON is stable across multiple calls."""
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test message",
        context={"key1": "value1", "key2": "value2"},
    )

    json1 = violation.canonical_json()
    json2 = violation.canonical_json()

    assert json1 == json2
    assert isinstance(json1, str)


def test_invariant_violation_canonical_json_sorted_keys():
    """Test that canonical JSON has sorted keys."""
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_TEMPERATURE_ZERO.value,
        severity=InvariantSeverity.WARN.value,
        message="Test",
        context={"z": 1, "a": 2, "m": 3},
    )

    json_str = violation.canonical_json()
    parsed = json.loads(json_str)

    # Verify keys are in sorted order
    assert list(parsed.keys()) == ["context", "invariant_id", "message", "severity"]
    assert list(parsed["context"].keys()) == ["a", "m", "z"]


def test_invariant_violation_hash_deterministic():
    """Test that violation hash is deterministic."""
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_TELEMETRY_HAS_FINGERPRINT_HASH.value,
        severity=InvariantSeverity.FAIL.value,
        message="Missing fingerprint",
        context={"provider": "test"},
    )

    hash1 = violation.violation_hash()
    hash2 = violation.violation_hash()

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex digest
    assert all(c in "0123456789abcdef" for c in hash1)


def test_invariant_violation_hash_changes_on_content_change():
    """Test that hash changes when violation content changes."""
    violation1 = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_SEED_PRESENT.value,
        severity=InvariantSeverity.FAIL.value,
        message="Message 1",
        context={},
    )

    violation2 = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_SEED_PRESENT.value,
        severity=InvariantSeverity.FAIL.value,
        message="Message 2",
        context={},
    )

    assert violation1.violation_hash() != violation2.violation_hash()


def test_invariant_violation_as_dict_includes_hash():
    """Test that as_dict includes violation_hash."""
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test",
        context={"key": "value"},
    )

    result = violation.as_dict()

    assert "violation_hash" in result
    assert result["violation_hash"] == violation.violation_hash()
    assert result["invariant_id"] == violation.invariant_id
    assert result["severity"] == violation.severity
    assert result["message"] == violation.message
    assert result["context"] == violation.context


def test_invariant_id_enum_values_stable():
    """Test that InvariantId enum values are stable strings."""
    assert InvariantId.INV_NO_GPU_IMPORTS_IN_L0_L6.value == "INV_NO_GPU_IMPORTS_IN_L0_L6"
    assert InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value == "INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS"
    assert InvariantId.INV_LOCAL_REQUEST_TEMPERATURE_ZERO.value == "INV_LOCAL_REQUEST_TEMPERATURE_ZERO"
    assert InvariantId.INV_LOCAL_REQUEST_SEED_PRESENT.value == "INV_LOCAL_REQUEST_SEED_PRESENT"
    assert InvariantId.INV_TELEMETRY_HAS_FINGERPRINT_HASH.value == "INV_TELEMETRY_HAS_FINGERPRINT_HASH"
    assert InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value == "INV_REPLAY_HASH_PRESENT_WHEN_ENABLED"
    assert InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value == "INV_GEMINI_FALLBACK_REQUIRES_REASON"


def test_invariant_severity_enum_values():
    """Test that InvariantSeverity enum values are stable."""
    assert InvariantSeverity.INFO.value == "INFO"
    assert InvariantSeverity.WARN.value == "WARN"
    assert InvariantSeverity.FAIL.value == "FAIL"


def test_invariant_violation_frozen():
    """Test that InvariantViolation is immutable."""
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test",
        context={},
    )

    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        violation.message = "Changed"
