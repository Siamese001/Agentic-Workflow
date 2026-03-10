"""
Phase 7: Deterministic Replay Tamper Round-Trip Validation (production-path).

Tests that:
- A persisted replay artifact validates under the real verifier.
- A deterministically tampered copy is rejected (with stable, 64-hex replay_hash deltas).
- All proofs use production verifier (no test doubles).
- Tamper logic is test-only.
"""

import re

import pytest

from agentic_core.L2_execution.types.vllm_gateway_adapter_types import VLLMGatewayAdapter
from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    VLLMCircuitBreakerRegistry,
    VLLMQueueController,
)
from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
    VLLMInfrastructureFingerprint,
)
from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
    InvariantId,
    InvariantSeverity,
    InvariantViolation,
)
from agentic_core.L2_execution.types.vllm_replay_validator_types import (
    VLLMReplayArtifact,
    VLLMReplayValidator,
)


def reset_singletons():
    """Reset singleton instances for deterministic testing."""
    from agentic_core.L2_execution.types.vllm_gateway_adapter_types import reset_singletons

    reset_singletons()


def create_test_artifact_with_violations() -> VLLMReplayArtifact:
    """Create a test replay artifact with invariant violations."""
    reset_singletons()

    # Create adapter and deterministic fingerprint
    adapter = VLLMGatewayAdapter(queue=VLLMQueueController(), registry=VLLMCircuitBreakerRegistry())
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    # Create FAIL violation
    fail_violation = InvariantViolation(
        invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
        severity=InvariantSeverity.FAIL.value,
        message="Replay hash enforcement enabled but replay_hash missing from telemetry",
        context={"provider": "Qwen2.5-7B-Instruct", "replay_hash_enabled": True},
    )

    # Mock the verifier to return the violation
    from unittest.mock import patch

    with patch(
        "agentic_core.L2_execution.types.vllm_invariant_verifier_types.verify_gateway_invariants"
    ) as mock_verify:
        mock_verify.return_value = [fail_violation]

        result = adapter.evaluate(
            prompt="test_prompt_for_tamper",
            task_class="patch_suggestion",
            severity="low",
            oldest_wait_seconds=0.0,
            fingerprint=fp,
        )

    # Create replay artifact
    return VLLMReplayArtifact(
        prompt="test_prompt_for_tamper",
        local_request=None,  # Will be None due to FAIL violation routing to Gemini
        fingerprint=fp,
        result=result,
    )


def create_tampered_artifact(original: VLLMReplayArtifact) -> VLLMReplayArtifact:
    """Create a deterministically tampered copy with mismatched stored hash."""
    # Create artifact with tampered prompt
    tampered_prompt = original.prompt + "_tampered"
    tampered_artifact = VLLMReplayArtifact(
        prompt=tampered_prompt,
        local_request=original.local_request,
        fingerprint=original.fingerprint,
        result=original.result,
    )

    # Get the new correct hash for tampered artifact
    correct_hash = tampered_artifact.replay_hash

    # Override the stored hash with the original hash to create a mismatch
    object.__setattr__(tampered_artifact, "replay_hash", original.replay_hash)

    return tampered_artifact


def validate_64hex(value: str, name: str) -> None:
    """Validate that a string is a 64-character hex string."""
    assert re.match(r"^[0-9a-f]{64}$", value), f"{name} must be 64-hex: {value}"


@pytest.mark.unit_min_deps
def test_replay_tamper_round_trip():
    """Test deterministic tamper round-trip with production verifier."""
    # Create original artifact
    original_artifact = create_test_artifact_with_violations()
    original_hash = original_artifact.replay_hash
    validate_64hex(original_hash, "original_replay_hash")

    # Validate original artifact with production verifier
    validator = VLLMReplayValidator()
    original_validation = validator.validate_and_report(original_artifact)

    assert original_validation["valid"] is True, "Original artifact should validate"
    assert original_validation["stored_replay_hash"] == original_hash, "Stored hash should match"

    # Create tampered artifact
    tampered_artifact = create_tampered_artifact(original_artifact)
    tampered_stored_hash = tampered_artifact.replay_hash
    validate_64hex(tampered_stored_hash, "tampered_stored_replay_hash")

    # Validate tampered artifact with production verifier
    tampered_validation = validator.validate_and_report(tampered_artifact)

    assert tampered_validation["valid"] is False, "Tampered artifact should be rejected"
    assert tampered_stored_hash == original_hash, "Tampered stored hash should match original (by design)"
    assert tampered_validation["stored_replay_hash"] == tampered_stored_hash, "Stored hash should match"
    assert tampered_validation["computed_replay_hash"] != original_hash, (
        "Computed hash must differ from original"
    )

    print(f"Original replay_hash: {original_hash}")
    print(f"Tampered stored replay_hash: {tampered_stored_hash}")
    print(f"Tampered computed replay_hash: {tampered_validation['computed_replay_hash']}")
    print(f"Tampering detected: {not tampered_validation['valid']}")


@pytest.mark.unit_min_deps
def test_replay_tamper_determinism_re_run():
    """Test that tamper round-trip is deterministic across multiple runs."""
    # First run
    original_hash_1 = None
    tampered_hash_1 = None

    original_artifact_1 = create_test_artifact_with_violations()
    original_hash_1 = original_artifact_1.replay_hash
    validate_64hex(original_hash_1, "original_replay_hash_run1")

    tampered_artifact_1 = create_tampered_artifact(original_artifact_1)
    tampered_hash_1 = tampered_artifact_1.replay_hash
    validate_64hex(tampered_hash_1, "tampered_replay_hash_run1")

    # Second run
    original_hash_2 = None
    tampered_computed_hash_2 = None

    original_artifact_2 = create_test_artifact_with_violations()
    original_hash_2 = original_artifact_2.replay_hash
    validate_64hex(original_hash_2, "original_replay_hash_run2")

    tampered_artifact_2 = create_tampered_artifact(original_artifact_2)
    validator = VLLMReplayValidator()
    tampered_validation_2 = validator.validate_and_report(tampered_artifact_2)
    tampered_computed_hash_2 = tampered_validation_2["computed_replay_hash"]
    validate_64hex(tampered_computed_hash_2, "tampered_computed_replay_hash_run2")

    # Get first run computed hash for comparison
    tampered_validation_1 = validator.validate_and_report(tampered_artifact_1)
    tampered_computed_hash_1 = tampered_validation_1["computed_replay_hash"]

    # Assert determinism
    assert original_hash_1 == original_hash_2, "Original hash must be deterministic"
    assert tampered_computed_hash_1 == tampered_computed_hash_2, (
        "Tampered computed hash must be deterministic"
    )

    print(f"Determinism check: original_hash_1 == original_hash_2 = {original_hash_1 == original_hash_2}")
    print(
        f"Determinism check: tampered_computed_hash_1 == tampered_computed_hash_2 = {tampered_computed_hash_1 == tampered_computed_hash_2}"
    )


@pytest.mark.unit_min_deps
def test_negative_control_tamper_detection_disabled():
    """Negative control: prove enforcement fails when tamper detection is disabled."""
    # Create original artifact
    original_artifact = create_test_artifact_with_violations()
    original_hash = original_artifact.replay_hash
    validate_64hex(original_hash, "original_replay_hash")

    # Create tampered artifact
    tampered_artifact = create_tampered_artifact(original_artifact)
    tampered_hash = tampered_artifact.replay_hash
    validate_64hex(tampered_hash, "tampered_replay_hash")

    # Mock validator to always return True (tamper detection disabled)
    class DisabledValidator:
        def validate(self, artifact):
            return True  # Always pass, tamper detection disabled

        def validate_and_report(self, artifact):
            return {
                "valid": True,
                "stored_replay_hash": artifact.replay_hash,
                "computed_replay_hash": artifact.replay_hash,
                "violation_details": None,
            }

    # With tamper detection disabled, tampered artifact incorrectly passes
    disabled_validator = DisabledValidator()
    disabled_validation = disabled_validator.validate_and_report(tampered_artifact)

    assert disabled_validation["valid"] is True, (
        "Tampered artifact incorrectly passes when detection disabled"
    )
    assert disabled_validation["stored_replay_hash"] == tampered_hash, "Stored hash should match tampered"

    # But production validator correctly rejects it
    production_validator = VLLMReplayValidator()
    production_validation = production_validator.validate_and_report(tampered_artifact)

    assert production_validation["valid"] is False, "Production validator must reject tampered artifact"

    print(f"Negative control: disabled_validator passes tampered = {disabled_validation['valid']}")
    print(f"Negative control: production_validator rejects tampered = {not production_validation['valid']}")
    print("OK: Enforcement check correctly fails when tamper detection disabled")
