"""
End-to-end tests for Phase 5 invariant enforcement at adapter seam.

Tests that FAIL violations trigger Gemini fallback with violations in telemetry.
"""

import pytest

from agentic_core.L2_execution.types.vllm_gateway_adapter_types import (
    VLLMGatewayAdapter,
    reset_singletons,
)
from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLMCircuitBreakerRegistry,
    VLLMQueueController,
)
from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
    VLLMInfrastructureFingerprint,
)
from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
    InvariantId,
    InvariantSeverity,
)

pytestmark = pytest.mark.integration_full_deps


@pytest.fixture(autouse=True)
def reset_adapter_state():
    """Reset adapter singletons before each test."""
    reset_singletons()
    yield
    reset_singletons()


def test_adapter_local_success_with_zero_violations():
    """Test that valid local request produces zero violations."""
    adapter = VLLMGatewayAdapter(
        queue=VLLMQueueController(),
        registry=VLLMCircuitBreakerRegistry(),
    )

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    result = adapter.evaluate(
        prompt="hello",
        task_class="patch_suggestion",
        severity="low",
        oldest_wait_seconds=0.0,
        fingerprint=fp,
    )

    # Should route to local (no violations)
    assert not result.route_to_gemini
    assert result.local_request is not None
    assert result.invariant_violations == []


def test_adapter_with_fingerprint_produces_no_violations():
    """Test that providing fingerprint produces no violations.

    NOTE: When fingerprint=None, evaluate_gateway_call uses deterministic_test_instance,
    so telemetry always has fingerprint_hash. This is by design for Phase 4 compatibility.
    """
    adapter = VLLMGatewayAdapter(
        queue=VLLMQueueController(),
        registry=VLLMCircuitBreakerRegistry(),
    )

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    result = adapter.evaluate(
        prompt="hello",
        task_class="patch_suggestion",
        severity="low",
        oldest_wait_seconds=0.0,
        fingerprint=fp,
    )

    # Should route to local (no violations)
    assert not result.route_to_gemini
    assert result.local_request is not None

    # Should have no violations
    assert result.invariant_violations == []


def test_adapter_result_has_invariant_violations_field():
    """Test that result always has invariant_violations field."""
    adapter = VLLMGatewayAdapter(
        queue=VLLMQueueController(),
        registry=VLLMCircuitBreakerRegistry(),
    )

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    result = adapter.evaluate(
        prompt="hello",
        task_class="patch_suggestion",
        severity="low",
        oldest_wait_seconds=0.0,
        fingerprint=fp,
    )

    # Result should always have invariant_violations field
    assert hasattr(result, "invariant_violations")
    assert isinstance(result.invariant_violations, list)


def test_adapter_preserves_phase_1_4_behavior():
    """Test that Phase 5 preserves Phase 1-4 routing behavior when no violations."""
    adapter = VLLMGatewayAdapter(
        queue=VLLMQueueController(),
        registry=VLLMCircuitBreakerRegistry(),
    )

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    # Test local success path
    result = adapter.evaluate(
        prompt="hello",
        task_class="patch_suggestion",
        severity="low",
        oldest_wait_seconds=0.0,
        fingerprint=fp,
    )

    # Should route to local (Phase 1-4 behavior preserved)
    assert not result.route_to_gemini
    assert result.local_request is not None
    assert result.telemetry is not None
    assert result.preflight is not None
    assert result.backpressure is not None

    # Phase 5 addition: invariant_violations
    assert result.invariant_violations == []


def test_adapter_fail_violation_triggers_gemini_with_violations_attached():
    """Test that FAIL violation triggers Gemini fallback with violations in telemetry.

    This test uses monkey-patching to force a FAIL violation and verify the
    adapter's enforcement behavior.
    """
    from unittest.mock import patch

    from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
        InvariantViolation,
    )

    adapter = VLLMGatewayAdapter(
        queue=VLLMQueueController(),
        registry=VLLMCircuitBreakerRegistry(),
    )

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    # Create a mock FAIL violation
    mock_violation = InvariantViolation(
        invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test FAIL violation",
        context={"test": True},
    )

    # Patch the verifier to return a FAIL violation
    with patch(
        "agentic_core.L2_execution.types.vllm_invariant_verifier_types.verify_gateway_invariants"
    ) as mock_verify:
        mock_verify.return_value = [mock_violation]

        result = adapter.evaluate(
            prompt="hello",
            task_class="patch_suggestion",
            severity="low",
            oldest_wait_seconds=0.0,
            fingerprint=fp,
        )

    # CRITICAL: FAIL violation should trigger Gemini fallback
    assert result.route_to_gemini, "FAIL violation must trigger Gemini fallback"
    assert result.local_request is None, "Local request should be None when routing to Gemini"

    # CRITICAL: FAIL violation must set failure_type=INVARIANT_VIOLATION
    assert result.telemetry.failure_type == "INVARIANT_VIOLATION", (
        "FAIL violation must set failure_type=INVARIANT_VIOLATION"
    )

    # Violations should be attached to result
    assert len(result.invariant_violations) == 1
    assert (
        result.invariant_violations[0].invariant_id == InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value
    )
    assert result.invariant_violations[0].severity == InvariantSeverity.FAIL.value

    # Violations should be serializable with hashes
    violation_dict = result.invariant_violations[0].as_dict()
    assert "violation_hash" in violation_dict
    assert len(violation_dict["violation_hash"]) == 64
