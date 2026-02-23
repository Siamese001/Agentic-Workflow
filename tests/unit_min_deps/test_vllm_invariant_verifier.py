"""
Unit tests for vLLM invariant verifier (minimal dependencies).

Tests invariant verification logic with minimal fixtures.
"""

from dataclasses import dataclass

import pytest

from agentic_core.L2_execution.types.vllm_invariant_contract import (
    InvariantId,
    InvariantSeverity,
)
from agentic_core.L2_execution.types.vllm_invariant_verifier import (
    verify_gateway_invariants,
)

pytestmark = pytest.mark.unit_min_deps


@dataclass
class MinimalLocalRequest:
    """Minimal local request fixture for testing."""

    max_tokens: int | None = None
    temperature: float | None = None
    seed: int | None = None


def test_verify_no_violations_on_valid_local_request():
    """Test that valid local request produces no violations."""
    local_request = MinimalLocalRequest(
        max_tokens=100,
        temperature=0.0,
        seed=42,
    )

    telemetry_dict = {
        "fingerprint_hash": "abc123",
        "failure_type": None,
    }

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert violations == []


def test_inv_missing_max_tokens():
    """Test INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS violation."""
    local_request = MinimalLocalRequest(
        max_tokens=None,
        temperature=0.0,
        seed=42,
    )

    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "max_tokens" in violations[0].message.lower()


def test_inv_temperature_not_zero():
    """Test INV_LOCAL_REQUEST_TEMPERATURE_ZERO violation."""
    local_request = MinimalLocalRequest(
        max_tokens=100,
        temperature=0.7,
        seed=42,
    )

    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_LOCAL_REQUEST_TEMPERATURE_ZERO.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "0.7" in violations[0].message


def test_inv_missing_seed():
    """Test INV_LOCAL_REQUEST_SEED_PRESENT violation."""
    local_request = MinimalLocalRequest(
        max_tokens=100,
        temperature=0.0,
        seed=None,
    )

    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_LOCAL_REQUEST_SEED_PRESENT.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "seed" in violations[0].message.lower()


def test_inv_missing_fingerprint_hash():
    """Test INV_TELEMETRY_HAS_FINGERPRINT_HASH violation."""
    local_request = MinimalLocalRequest(
        max_tokens=100,
        temperature=0.0,
        seed=42,
    )

    telemetry_dict = {}  # Missing fingerprint_hash

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_TELEMETRY_HAS_FINGERPRINT_HASH.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "fingerprint_hash" in violations[0].message.lower()


def test_inv_gemini_fallback_requires_reason():
    """Test INV_GEMINI_FALLBACK_REQUIRES_REASON violation."""
    telemetry_dict = {
        "fingerprint_hash": "abc123",
        "failure_type": None,  # Missing failure_type for Gemini
    }

    violations = verify_gateway_invariants(
        provider_selected="gemini-2.5-pro",
        local_request=None,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "failure_type" in violations[0].message.lower()


def test_gemini_fallback_with_reason_no_violation():
    """Test that Gemini fallback with failure_type produces no violation."""
    telemetry_dict = {
        "fingerprint_hash": "abc123",
        "failure_type": "TOKEN_BUDGET_EXCEEDED",
    }

    violations = verify_gateway_invariants(
        provider_selected="gemini-2.5-pro",
        local_request=None,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    # Should have no INV_GEMINI_FALLBACK_REQUIRES_REASON violation
    gemini_violations = [
        v for v in violations
        if v.invariant_id == InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value
    ]
    assert gemini_violations == []


def test_multiple_violations_sorted_deterministically():
    """Test that multiple violations are sorted by invariant_id then severity."""
    local_request = MinimalLocalRequest(
        max_tokens=None,
        temperature=0.7,
        seed=None,
    )

    telemetry_dict = {}  # Missing fingerprint_hash

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    # Should have 4 violations
    assert len(violations) == 4

    # Verify they are sorted by invariant_id
    invariant_ids = [v.invariant_id for v in violations]
    assert invariant_ids == sorted(invariant_ids)


def test_violations_are_deterministic():
    """Test that violations are deterministic across multiple calls."""
    local_request = MinimalLocalRequest(
        max_tokens=None,
        temperature=0.0,
        seed=42,
    )

    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations1 = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    violations2 = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations1) == len(violations2)
    for v1, v2 in zip(violations1, violations2):
        assert v1.invariant_id == v2.invariant_id
        assert v1.severity == v2.severity
        assert v1.message == v2.message
        assert v1.violation_hash() == v2.violation_hash()
