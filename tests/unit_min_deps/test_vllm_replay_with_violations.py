"""
Unit tests for Phase 6: Deterministic Replay Under Invariant Enforcement.

Tests that replay artifacts with invariant violations produce stable, deterministic
replay hashes and that tampering is detected.
"""

import pytest

from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    InvariantId,
    InvariantSeverity,
    InvariantViolation,
)

pytestmark = pytest.mark.unit_min_deps


def test_replay_hash_identical_with_same_violations():
    """Test that identical FAIL scenarios produce identical replay_hash."""
    from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
        VLLMGatewayCallResult,
        VLLMGatewayTelemetry,
    )
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        VLLMInfrastructureFingerprint,
    )
    from agentic_core.L2_execution.types.vllm_replay_validator_types import (
        compute_replay_hash,
    )

    # Create mock result with violations
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    violation = InvariantViolation(
        invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test violation",
        context={"test": True},
    )

    # Create two identical results
    from dataclasses import dataclass

    @dataclass
    class MockPreflight:
        prompt_tokens_estimated: int = 1
        max_output_tokens_requested: int = 100
        max_model_len_configured: int = 8192
        token_budget_ok: bool = True
        budget_margin_tokens: int = 7000
        failure_type: str | None = None
        route_to_gemini: bool = False

    @dataclass
    class MockBackpressure:
        escalate_to_gemini: bool = False
        reason: str = "ok"
        failure_type: str | None = None
        model_id: str = ""
        queue_depth: int = 0
        circuit_breaker_open: bool = False

    telemetry = VLLMGatewayTelemetry(
        provider_selected="gemini-2.5-pro",
        model_tier="remote",
        prompt_tokens_estimated=1,
        max_output_tokens_requested=100,
        max_model_len_configured=8192,
        token_budget_ok=True,
        budget_margin_tokens=7000,
        queue_depth=0,
        queue_full=False,
        queue_wait_seconds=0.0,
        breaker_state="CLOSED",
        breaker_failure_count=0,
        failure_type="INVARIANT_VIOLATION",
        model_name=fp.model_name,
        model_revision_sha=fp.model_revision_sha,
        vllm_version=fp.vllm_version,
        transformers_version=fp.transformers_version,
        torch_version=fp.torch_version,
        cuda_version=fp.cuda_version,
        driver_version=fp.driver_version,
        fingerprint_hash=fp.fingerprint_hash(),
    )

    result1 = VLLMGatewayCallResult(
        route_to_gemini=True,
        local_request=None,
        telemetry=telemetry,
        preflight=MockPreflight(),
        backpressure=MockBackpressure(),
        invariant_violations=[violation],
    )

    result2 = VLLMGatewayCallResult(
        route_to_gemini=True,
        local_request=None,
        telemetry=telemetry,
        preflight=MockPreflight(),
        backpressure=MockBackpressure(),
        invariant_violations=[violation],
    )

    # Compute replay hashes
    hash1 = compute_replay_hash("hello", None, fp, result1)
    hash2 = compute_replay_hash("hello", None, fp, result2)

    # Identical inputs should produce identical hashes
    assert hash1 == hash2
    assert len(hash1) == 64
    assert all(c in "0123456789abcdef" for c in hash1)


def test_replay_hash_changes_when_violation_id_changes():
    """Test that changing invariant_id changes replay_hash."""
    from dataclasses import dataclass

    from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
        VLLMGatewayCallResult,
        VLLMGatewayTelemetry,
    )
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        VLLMInfrastructureFingerprint,
    )
    from agentic_core.L2_execution.types.vllm_replay_validator_types import (
        compute_replay_hash,
    )

    @dataclass
    class MockPreflight:
        prompt_tokens_estimated: int = 1
        max_output_tokens_requested: int = 100
        max_model_len_configured: int = 8192
        token_budget_ok: bool = True
        budget_margin_tokens: int = 7000
        failure_type: str | None = None
        route_to_gemini: bool = False

    @dataclass
    class MockBackpressure:
        escalate_to_gemini: bool = False
        reason: str = "ok"
        failure_type: str | None = None
        model_id: str = ""
        queue_depth: int = 0
        circuit_breaker_open: bool = False

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    violation1 = InvariantViolation(
        invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test violation",
        context={"test": True},
    )

    violation2 = InvariantViolation(
        invariant_id=InvariantId.INV_NO_GPU_IMPORTS_IN_L0_L6.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test violation",
        context={"test": True},
    )

    telemetry = VLLMGatewayTelemetry(
        provider_selected="gemini-2.5-pro",
        model_tier="remote",
        prompt_tokens_estimated=1,
        max_output_tokens_requested=100,
        max_model_len_configured=8192,
        token_budget_ok=True,
        budget_margin_tokens=7000,
        queue_depth=0,
        queue_full=False,
        queue_wait_seconds=0.0,
        breaker_state="CLOSED",
        breaker_failure_count=0,
        failure_type="INVARIANT_VIOLATION",
        model_name=fp.model_name,
        model_revision_sha=fp.model_revision_sha,
        vllm_version=fp.vllm_version,
        transformers_version=fp.transformers_version,
        torch_version=fp.torch_version,
        cuda_version=fp.cuda_version,
        driver_version=fp.driver_version,
        fingerprint_hash=fp.fingerprint_hash(),
    )

    result1 = VLLMGatewayCallResult(
        route_to_gemini=True,
        local_request=None,
        telemetry=telemetry,
        preflight=MockPreflight(),
        backpressure=MockBackpressure(),
        invariant_violations=[violation1],
    )

    result2 = VLLMGatewayCallResult(
        route_to_gemini=True,
        local_request=None,
        telemetry=telemetry,
        preflight=MockPreflight(),
        backpressure=MockBackpressure(),
        invariant_violations=[violation2],
    )

    hash1 = compute_replay_hash("hello", None, fp, result1)
    hash2 = compute_replay_hash("hello", None, fp, result2)

    # Different violation IDs should produce different hashes
    assert hash1 != hash2


def test_replay_hash_changes_when_violation_hash_changes():
    """Test that changing violation content changes replay_hash."""
    from dataclasses import dataclass

    from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
        VLLMGatewayCallResult,
        VLLMGatewayTelemetry,
    )
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        VLLMInfrastructureFingerprint,
    )
    from agentic_core.L2_execution.types.vllm_replay_validator_types import (
        compute_replay_hash,
    )

    @dataclass
    class MockPreflight:
        prompt_tokens_estimated: int = 1
        max_output_tokens_requested: int = 100
        max_model_len_configured: int = 8192
        token_budget_ok: bool = True
        budget_margin_tokens: int = 7000
        failure_type: str | None = None
        route_to_gemini: bool = False

    @dataclass
    class MockBackpressure:
        escalate_to_gemini: bool = False
        reason: str = "ok"
        failure_type: str | None = None
        model_id: str = ""
        queue_depth: int = 0
        circuit_breaker_open: bool = False

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    violation1 = InvariantViolation(
        invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test violation 1",
        context={"test": True},
    )

    violation2 = InvariantViolation(
        invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test violation 2",  # Different message
        context={"test": True},
    )

    telemetry = VLLMGatewayTelemetry(
        provider_selected="gemini-2.5-pro",
        model_tier="remote",
        prompt_tokens_estimated=1,
        max_output_tokens_requested=100,
        max_model_len_configured=8192,
        token_budget_ok=True,
        budget_margin_tokens=7000,
        queue_depth=0,
        queue_full=False,
        queue_wait_seconds=0.0,
        breaker_state="CLOSED",
        breaker_failure_count=0,
        failure_type="INVARIANT_VIOLATION",
        model_name=fp.model_name,
        model_revision_sha=fp.model_revision_sha,
        vllm_version=fp.vllm_version,
        transformers_version=fp.transformers_version,
        torch_version=fp.torch_version,
        cuda_version=fp.cuda_version,
        driver_version=fp.driver_version,
        fingerprint_hash=fp.fingerprint_hash(),
    )

    result1 = VLLMGatewayCallResult(
        route_to_gemini=True,
        local_request=None,
        telemetry=telemetry,
        preflight=MockPreflight(),
        backpressure=MockBackpressure(),
        invariant_violations=[violation1],
    )

    result2 = VLLMGatewayCallResult(
        route_to_gemini=True,
        local_request=None,
        telemetry=telemetry,
        preflight=MockPreflight(),
        backpressure=MockBackpressure(),
        invariant_violations=[violation2],
    )

    hash1 = compute_replay_hash("hello", None, fp, result1)
    hash2 = compute_replay_hash("hello", None, fp, result2)

    # Different violation content should produce different hashes
    assert hash1 != hash2
    # But both violations should have different hashes themselves
    assert violation1.violation_hash() != violation2.violation_hash()


def test_replay_hash_deterministic_without_violations():
    """Test that PASS scenario (no violations) produces deterministic replay_hash."""
    from dataclasses import dataclass

    from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
        VLLMGatewayCallResult,
        VLLMGatewayTelemetry,
    )
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        VLLMInfrastructureFingerprint,
    )
    from agentic_core.L2_execution.types.vllm_replay_validator_types import (
        compute_replay_hash,
    )

    @dataclass
    class MockPreflight:
        prompt_tokens_estimated: int = 1
        max_output_tokens_requested: int = 100
        max_model_len_configured: int = 8192
        token_budget_ok: bool = True
        budget_margin_tokens: int = 7000
        failure_type: str | None = None
        route_to_gemini: bool = False

    @dataclass
    class MockBackpressure:
        escalate_to_gemini: bool = False
        reason: str = "ok"
        failure_type: str | None = None
        model_id: str = ""
        queue_depth: int = 0
        circuit_breaker_open: bool = False

    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    telemetry = VLLMGatewayTelemetry(
        provider_selected="Qwen2.5-7B-Instruct",
        model_tier="fast",
        prompt_tokens_estimated=1,
        max_output_tokens_requested=100,
        max_model_len_configured=8192,
        token_budget_ok=True,
        budget_margin_tokens=7000,
        queue_depth=0,
        queue_full=False,
        queue_wait_seconds=0.0,
        breaker_state="CLOSED",
        breaker_failure_count=0,
        failure_type=None,
        model_name=fp.model_name,
        model_revision_sha=fp.model_revision_sha,
        vllm_version=fp.vllm_version,
        transformers_version=fp.transformers_version,
        torch_version=fp.torch_version,
        cuda_version=fp.cuda_version,
        driver_version=fp.driver_version,
        fingerprint_hash=fp.fingerprint_hash(),
    )

    result1 = VLLMGatewayCallResult(
        route_to_gemini=False,
        local_request=None,
        telemetry=telemetry,
        preflight=MockPreflight(),
        backpressure=MockBackpressure(),
        invariant_violations=[],  # No violations
    )

    result2 = VLLMGatewayCallResult(
        route_to_gemini=False,
        local_request=None,
        telemetry=telemetry,
        preflight=MockPreflight(),
        backpressure=MockBackpressure(),
        invariant_violations=[],  # No violations
    )

    hash1 = compute_replay_hash("hello", None, fp, result1)
    hash2 = compute_replay_hash("hello", None, fp, result2)

    # Identical inputs with no violations should produce identical hashes
    assert hash1 == hash2
    assert len(hash1) == 64
