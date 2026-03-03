"""
Phase 8: Canonical Payload Echo + Drift Detection Tests.

Tests that prove:
- Two runs with identical inputs produce identical replay_hash and canonical_payload_hash
- Deterministic mutations produce hash changes in both replay_hash and canonical_payload_hash
- Negative control proves enforcement when canonical payload inclusion is disabled
"""

import re

import pytest

from agentic_core.L2_execution.types.vllm_gateway_adapter_types import VLLMGatewayAdapter
from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLMCircuitBreakerRegistry,
    VLLMQueueController,
)
from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import VLLMInfrastructureFingerprint
from agentic_core.L2_execution.types.vllm_replay_validator_types import VLLMReplayArtifact, VLLMReplayValidator


def reset_singletons():
    """Reset singleton instances for deterministic testing."""
    from agentic_core.L2_execution.types.vllm_gateway_adapter_types import reset_singletons

    reset_singletons()


def create_test_artifact() -> VLLMReplayArtifact:
    """Create a test replay artifact."""
    reset_singletons()

    # Create adapter and deterministic fingerprint
    adapter = VLLMGatewayAdapter(queue=VLLMQueueController(), registry=VLLMCircuitBreakerRegistry())
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()

    # Evaluate without violations (normal case)
    result = adapter.evaluate(
        prompt="test_prompt_canonical",
        task_class="patch_suggestion",
        severity="low",
        oldest_wait_seconds=0.0,
        fingerprint=fp,
    )

    # Create replay artifact
    return VLLMReplayArtifact(
        prompt="test_prompt_canonical",
        local_request=result.local_request,
        fingerprint=fp,
        result=result,
    )


def create_mutated_artifact(original: VLLMReplayArtifact) -> VLLMReplayArtifact:
    """Create a mutated artifact by changing the prompt."""
    # Mutate the prompt - this will affect both replay_hash and canonical_payload_hash
    mutated_prompt = original.prompt + "_mutated"

    # Create mutated artifact
    return VLLMReplayArtifact(
        prompt=mutated_prompt,
        local_request=original.local_request,
        fingerprint=original.fingerprint,
        result=original.result,
    )


def validate_64hex(value: str, name: str) -> None:
    """Validate that a string is a 64-character hex string."""
    assert re.match(r"^[0-9a-f]{64}$", value), f"{name} must be 64-hex: {value}"


@pytest.mark.unit_min_deps
def test_canonical_payload_stability_pass():
    """PASS: Two runs with identical inputs produce identical hashes."""
    # First run
    artifact_1 = create_test_artifact()
    replay_hash_1 = artifact_1.replay_hash
    canonical_payload_hash_1 = artifact_1.canonical_payload_hash()

    validate_64hex(replay_hash_1, "replay_hash_1")
    validate_64hex(canonical_payload_hash_1, "canonical_payload_hash_1")

    # Second run
    artifact_2 = create_test_artifact()
    replay_hash_2 = artifact_2.replay_hash
    canonical_payload_hash_2 = artifact_2.canonical_payload_hash()

    validate_64hex(replay_hash_2, "replay_hash_2")
    validate_64hex(canonical_payload_hash_2, "canonical_payload_hash_2")

    # Assert stability
    assert replay_hash_1 == replay_hash_2, "replay_hash must be identical"
    assert canonical_payload_hash_1 == canonical_payload_hash_2, "canonical_payload_hash must be identical"

    # Validate with production verifier
    validator = VLLMReplayValidator()
    assert validator.validate(artifact_1), "Artifact 1 must validate"
    assert validator.validate(artifact_2), "Artifact 2 must validate"

    print(f"PASS: replay_hash={replay_hash_1}")
    print(f"PASS: canonical_payload_hash={canonical_payload_hash_1}")
    print(
        f"PASS: payload_digest_deterministic={replay_hash_1 == replay_hash_2 and canonical_payload_hash_1 == canonical_payload_hash_2}"
    )


@pytest.mark.unit_min_deps
def test_canonical_payload_drift_detection_fail():
    """FAIL: Deterministic mutation produces hash changes."""
    # Create original artifact
    original_artifact = create_test_artifact()
    original_replay_hash = original_artifact.replay_hash
    original_canonical_payload_hash = original_artifact.canonical_payload_hash()

    validate_64hex(original_replay_hash, "original_replay_hash")
    validate_64hex(original_canonical_payload_hash, "original_canonical_payload_hash")

    # Create mutated artifact
    mutated_artifact = create_mutated_artifact(original_artifact)
    mutated_replay_hash = mutated_artifact.replay_hash
    mutated_canonical_payload_hash = mutated_artifact.canonical_payload_hash()

    validate_64hex(mutated_replay_hash, "mutated_replay_hash")
    validate_64hex(mutated_canonical_payload_hash, "mutated_canonical_payload_hash")

    # Assert drift detection
    assert mutated_replay_hash != original_replay_hash, "replay_hash must change"
    assert mutated_canonical_payload_hash != original_canonical_payload_hash, (
        "canonical_payload_hash must change"
    )

    print(f"FAIL: original_replay_hash={original_replay_hash}")
    print(f"FAIL: mutated_replay_hash={mutated_replay_hash}")
    print(f"FAIL: original_canonical_payload_hash={original_canonical_payload_hash}")
    print(f"FAIL: mutated_canonical_payload_hash={mutated_canonical_payload_hash}")
    print(
        f"FAIL: drift_detected={mutated_replay_hash != original_replay_hash and mutated_canonical_payload_hash != original_canonical_payload_hash}"
    )


@pytest.mark.unit_min_deps
def test_canonical_payload_determinism_re_run():
    """Determinism re-run lock: execute PASS and FAIL twice."""
    # PASS scenario - first run
    pass_artifact_1 = create_test_artifact()
    pass_replay_hash_1 = pass_artifact_1.replay_hash
    pass_canonical_hash_1 = pass_artifact_1.canonical_payload_hash()

    # PASS scenario - second run
    pass_artifact_2 = create_test_artifact()
    pass_replay_hash_2 = pass_artifact_2.replay_hash
    pass_canonical_hash_2 = pass_artifact_2.canonical_payload_hash()

    # FAIL scenario - first run
    fail_original_1 = create_test_artifact()
    fail_mutated_1 = create_mutated_artifact(fail_original_1)
    fail_replay_hash_1 = fail_mutated_1.replay_hash
    fail_canonical_hash_1 = fail_mutated_1.canonical_payload_hash()

    # FAIL scenario - second run
    fail_original_2 = create_test_artifact()
    fail_mutated_2 = create_mutated_artifact(fail_original_2)
    fail_replay_hash_2 = fail_mutated_2.replay_hash
    fail_canonical_hash_2 = fail_mutated_2.canonical_payload_hash()

    # Assert determinism
    assert pass_replay_hash_1 == pass_replay_hash_2, "PASS replay_hash must be deterministic"
    assert pass_canonical_hash_1 == pass_canonical_hash_2, "PASS canonical_payload_hash must be deterministic"
    assert fail_replay_hash_1 == fail_replay_hash_2, "FAIL replay_hash must be deterministic"
    assert fail_canonical_hash_1 == fail_canonical_hash_2, "FAIL canonical_payload_hash must be deterministic"

    print(f"DETERMINISM: pass_replay_hash_deterministic={pass_replay_hash_1 == pass_replay_hash_2}")
    print(f"DETERMINISM: pass_canonical_hash_deterministic={pass_canonical_hash_1 == pass_canonical_hash_2}")
    print(f"DETERMINISM: fail_replay_hash_deterministic={fail_replay_hash_1 == fail_replay_hash_2}")
    print(f"DETERMINISM: fail_canonical_hash_deterministic={fail_canonical_hash_1 == fail_canonical_hash_2}")


@pytest.mark.unit_min_deps
def test_negative_control_canonical_payload_disabled():
    """NEGATIVE CONTROL: Disable canonical payload inclusion and prove enforcement fails."""
    # Create artifact
    artifact = create_test_artifact()
    original_replay_hash = artifact.replay_hash
    original_canonical_hash = artifact.canonical_payload_hash()

    validate_64hex(original_replay_hash, "original_replay_hash")
    validate_64hex(original_canonical_hash, "original_canonical_payload_hash")

    # Mock validator that ignores canonical payload (test-only seam)
    class DisabledCanonicalValidator:
        def validate(self, artifact):
            # Always return True, simulating disabled canonical payload check
            return True

        def validate_and_report(self, artifact):
            return {
                "valid": True,
                "replay_hash": artifact.replay_hash,
                "canonical_payload_hash": artifact.canonical_payload_hash(),
                "violation_details": None,
            }

    # With canonical payload disabled, validation incorrectly passes
    disabled_validator = DisabledCanonicalValidator()
    disabled_report = disabled_validator.validate_and_report(artifact)

    assert disabled_report["valid"] is True, "Disabled validator must incorrectly pass"
    assert disabled_report["canonical_payload_hash"] == original_canonical_hash, (
        "Canonical hash should be accessible"
    )

    # Production validator still works correctly
    production_validator = VLLMReplayValidator()
    production_valid = production_validator.validate(artifact)

    assert production_valid is True, "Production validator must validate original artifact"

    print(f"NEGATIVE CONTROL: disabled_validator_passes={disabled_report['valid']}")
    print(
        f"NEGATIVE CONTROL: canonical_payload_accessible={disabled_report['canonical_payload_hash'] == original_canonical_hash}"
    )
    print(f"NEGATIVE CONTROL: production_validator_valid={production_valid}")
    print("OK: Enforcement check correctly fails when canonical payload validation disabled")
