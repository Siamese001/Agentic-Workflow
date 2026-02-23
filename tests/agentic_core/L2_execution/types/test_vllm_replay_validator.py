"""
PHASE 4 WAVE 3 tests — VLLMReplayValidator unit tests.

Tests deterministic replay hashing, replay artifact validation, and tamper detection.
No GPU imports. Pure L2.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.types.vllm_gateway_integration import (
    VLLMCircuitBreakerRegistry,
    VLLMQueueController,
    evaluate_gateway_call,
)
from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint import (
    VLLMInfrastructureFingerprint,
)
from agentic_core.L2_execution.types.vllm_replay_validator import (
    VLLMReplayArtifact,
    VLLMReplayValidator,
    canonical_local_request_hash,
    canonical_prompt_hash,
    canonical_response_hash,
    compute_replay_hash,
)
from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint import sha256_hex
from agentic_core.L2_execution.types.vllm_token_budget_types import TaskClass


SHORT_PROMPT = "hello world"
TASK = TaskClass.PATCH_SUGGESTION.value


def make_clean():
    """Create clean queue and registry for testing."""
    return VLLMQueueController(), VLLMCircuitBreakerRegistry()


def test_replay_hash_deterministic_two_runs():
    """Identical inputs produce identical replay_hash across two runs."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    ctrl1, reg1 = make_clean()
    ctrl2, reg2 = make_clean()
    
    result1 = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl1, reg1, fingerprint=fp)
    result2 = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl2, reg2, fingerprint=fp)
    
    hash1 = compute_replay_hash(
        prompt=SHORT_PROMPT,
        request=result1.local_request,
        fingerprint=fp,
        result=result1,
    )
    hash2 = compute_replay_hash(
        prompt=SHORT_PROMPT,
        request=result2.local_request,
        fingerprint=fp,
        result=result2,
    )
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex length


def test_replay_hash_changes_on_fingerprint_change():
    """replay_hash changes when fingerprint changes."""
    fp1 = VLLMInfrastructureFingerprint.deterministic_test_instance()
    fp2 = VLLMInfrastructureFingerprint(
        model_name="DifferentModel",
        model_revision_sha="def456abc123",
        vllm_version="0.6.4",
        transformers_version="4.46.1",
        torch_version="2.5.2",
        cuda_version="12.5",
        driver_version="550.54.15",
    )
    
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg, fingerprint=fp1)
    
    hash1 = compute_replay_hash(
        prompt=SHORT_PROMPT,
        request=result.local_request,
        fingerprint=fp1,
        result=result,
    )
    hash2 = compute_replay_hash(
        prompt=SHORT_PROMPT,
        request=result.local_request,
        fingerprint=fp2,
        result=result,
    )
    
    assert hash1 != hash2


def test_replay_hash_changes_on_prompt_change():
    """replay_hash changes when prompt changes."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    ctrl, reg = make_clean()
    
    result1 = evaluate_gateway_call("hello", TASK, "low", ctrl, reg, fingerprint=fp)
    result2 = evaluate_gateway_call("world", TASK, "low", ctrl, reg, fingerprint=fp)
    
    hash1 = compute_replay_hash(
        prompt="hello",
        request=result1.local_request,
        fingerprint=fp,
        result=result1,
    )
    hash2 = compute_replay_hash(
        prompt="world",
        request=result2.local_request,
        fingerprint=fp,
        result=result2,
    )
    
    assert hash1 != hash2


def test_replay_validator_accepts_valid_artifact():
    """Replay validator accepts untampered artifact."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg, fingerprint=fp)
    
    artifact = VLLMReplayArtifact(
        prompt=SHORT_PROMPT,
        local_request=result.local_request,
        fingerprint=fp,
        result=result,
    )
    
    validator = VLLMReplayValidator()
    assert validator.validate(artifact) is True
    
    report = validator.validate_and_report(artifact)
    assert report["valid"] is True
    assert report["stored_replay_hash"] == report["computed_replay_hash"]


def test_replay_validator_rejects_tampered_artifact():
    """Replay validator rejects tampered artifact."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg, fingerprint=fp)
    
    # Create artifact with original data
    artifact = VLLMReplayArtifact(
        prompt=SHORT_PROMPT,
        local_request=result.local_request,
        fingerprint=fp,
        result=result,
    )
    
    # Tamper by creating new artifact with different prompt but same stored hash
    # (This simulates artifact tampering)
    class TamperedArtifact(VLLMReplayArtifact):
        def __init__(self, original_artifact):
            # Copy all fields but change prompt
            super().__init__(
                prompt="TAMPERED_PROMPT",
                local_request=original_artifact.local_request,
                fingerprint=original_artifact.fingerprint,
                result=original_artifact.result,
            )
            # Preserve original replay_hash to simulate tampering
            object.__setattr__(self, "replay_hash", original_artifact.replay_hash)
    
    tampered = TamperedArtifact(artifact)
    
    validator = VLLMReplayValidator()
    assert validator.validate(tampered) is False
    
    report = validator.validate_and_report(tampered)
    assert report["valid"] is False
    assert report["stored_replay_hash"] != report["computed_replay_hash"]


def test_canonical_prompt_hash():
    """canonical_prompt_hash produces stable SHA256."""
    hash1 = canonical_prompt_hash("test")
    hash2 = canonical_prompt_hash("test")
    assert hash1 == hash2
    assert len(hash1) == 64


def test_canonical_local_request_hash():
    """canonical_local_request_hash produces stable SHA256."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg, fingerprint=fp)
    
    request = result.local_request
    assert request is not None
    
    hash1 = canonical_local_request_hash(request)
    hash2 = canonical_local_request_hash(request)
    assert hash1 == hash2
    assert len(hash1) == 64


def test_canonical_response_hash():
    """canonical_response_hash produces stable SHA256."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg, fingerprint=fp)
    
    hash1 = canonical_response_hash(result)
    hash2 = canonical_response_hash(result)
    assert hash1 == hash2
    assert len(hash1) == 64


def test_replay_artifact_with_none_local_request():
    """Replay artifact handles None local_request (Gemini fallback)."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    ctrl, reg = make_clean()
    
    # Force token budget exceed to get None local_request
    from agentic_core.L2_execution.types.vllm_serving_profile_types import LOCAL_FAST_7B_MAX_MODEL_LEN
    from agentic_core.L2_execution.types.vllm_token_budget_types import SAFETY_MARGIN_TOKENS, TASK_CLASS_OUTPUT_CAPS
    
    cap = TASK_CLASS_OUTPUT_CAPS[TASK]
    available = LOCAL_FAST_7B_MAX_MODEL_LEN - SAFETY_MARGIN_TOKENS - cap
    over_prompt = "a" * ((available + 10) * 3)
    
    result = evaluate_gateway_call(over_prompt, TASK, "low", ctrl, reg, fingerprint=fp)
    assert result.local_request is None
    
    artifact = VLLMReplayArtifact(
        prompt=over_prompt,
        local_request=None,
        fingerprint=fp,
        result=result,
    )
    
    validator = VLLMReplayValidator()
    assert validator.validate(artifact) is True
    
    # Verify local_request_hash is hash of empty dict
    assert artifact.local_request_hash == sha256_hex("{}")
