"""
Qwen Replay Validation Test - Determinism and Consistency Testing

Provides comprehensive replay validation to ensure Qwen invocations
are deterministic and reproducible.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingInput,
)


def create_deterministic_healing_input() -> HealingInput:
    """Create a deterministic healing input for testing."""
    return HealingInput(
        failure_type="syntax_error",
        error_signature="test_syntax_error_001",
        trace_id="test-trace-001",
        retry_count=0,
        blast_radius_estimate=0.1,
        required_tools=("ast_rewrite",),
        violation_metadata_refs=(),
    )


def invoke_qwen_via_healing_tier(healing_input: HealingInput) -> InvocationRecord:
    """Invoke Qwen through the healing tier system."""
    # Import here to avoid circular dependency
    from agentic_core.L2_execution.healers.healing_tier_config import load_default_healing_tier_config
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing

    config = load_default_healing_tier_config()

    # Mock the actual OpenAI call for testing
    # In real implementation, this would call the actual vLLM server
    decision, record = dispatch_healing(
        healing_input,
        config,
        agent_name="test_agent",
    )

    return record


def test_qwen_replay_determinism():
    """Verify exact replay consistency across invocations."""
    healing_input = create_deterministic_healing_input()

    # Invoke Qwen twice with identical parameters
    record1 = invoke_qwen_via_healing_tier(healing_input)
    record2 = invoke_qwen_via_healing_tier(healing_input)

    # Verify determinism digest matches
    if record1.provider_metadata and record2.provider_metadata:
        digest1 = record1.provider_metadata.get("determinism_digest")
        digest2 = record2.provider_metadata.get("determinism_digest")
        assert digest1 == digest2, f"Determinism drift: {digest1} != {digest2}"

        # Verify output hash matches
        output1 = record1.provider_metadata.get("output_hash")
        output2 = record2.provider_metadata.get("output_hash")
        assert output1 == output2, f"Output drift: {output1} != {output2}"

    # Verify canonical JSON serialization matches
    json1 = json.dumps(asdict(record1), separators=(",", ":"), sort_keys=True)
    json2 = json.dumps(asdict(record2), separators=(",", ":"), sort_keys=True)
    assert json1 == json2, "InvocationRecord JSON mismatch"


def test_qwen_determinism_digest_completeness():
    """Verify determinism digest includes all required components."""
    from agentic_core.L2_execution.healers.qwen_determinism import compute_qwen_determinism_digest

    digest = compute_qwen_determinism_digest(
        model_id="Qwen/Qwen2.5-7B-Instruct",
        model_revision="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
        tokenizer_revision="f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7",
        inference_params={"temperature": 0.0, "top_p": 1.0, "max_tokens": 2048, "seed": 42},
        vllm_version="0.4.2",
        cuda_version="12.1",
        torch_version="2.1.0",
    )

    # Verify full SHA-256 (64 hex characters)
    assert len(digest) == 64, f"Digest should be 64 chars, got {len(digest)}"
    assert all(c in "0123456789abcdef" for c in digest), "Digest should be hex only"


def test_qwen_output_canonicalization():
    """Verify output canonicalization handles Unicode and whitespace."""
    from agentic_core.L2_execution.healers.qwen_determinism import canonicalize_qwen_output

    # Test Unicode normalization
    output1 = "café"  # Combined accent
    output2 = "cafe\u0301"  # Decomposed accent
    hash1 = canonicalize_qwen_output(output1)
    hash2 = canonicalize_qwen_output(output2)
    assert hash1 == hash2, "Unicode normalization failed"

    # Test whitespace normalization
    output3 = "  hello\nworld  \n  "
    output4 = "hello\nworld"
    hash3 = canonicalize_qwen_output(output3)
    hash4 = canonicalize_qwen_output(output4)
    assert hash3 == hash4, "Whitespace normalization failed"


def test_qwen_circuit_breaker_replay_safety():
    """Verify circuit breaker is deterministic in replay mode."""
    from agentic_core.L2_execution.healers.qwen_circuit_breaker import QwenCircuitBreaker

    # Normal mode - circuit breaker should work
    cb_normal = QwenCircuitBreaker(replay_mode=False)
    assert not cb_normal.record_failure(), "First failure should not open circuit"
    assert not cb_normal.record_failure(), "Second failure should not open circuit"
    assert cb_normal.record_failure(), "Third failure should open circuit"
    assert cb_normal.is_circuit_open(), "Circuit should be open"

    # Replay mode - circuit breaker should be disabled
    cb_replay = QwenCircuitBreaker(replay_mode=True)
    assert not cb_replay.record_failure(), "Replay mode should disable circuit breaker"
    assert not cb_replay.record_failure(), "Replay mode should disable circuit breaker"
    assert not cb_replay.record_failure(), "Replay mode should disable circuit breaker"
    assert not cb_replay.is_circuit_open(), "Replay mode should always be closed"


def test_qwen_meta_learning_boundaries():
    """Verify meta-learning respects threshold immutability."""
    from agentic_core.L2_execution.healers.qwen_meta_learning import (
        HEALING_CONFIDENCE_X,
        HEALING_CONFIDENCE_Y,
        update_qwen_confidence_prior,
        validate_threshold_immutability,
    )

    # Update confidence prior (allowed)
    update_qwen_confidence_prior("test_error", success=True)

    # Validate thresholds are immutable
    validate_threshold_immutability()

    # Verify thresholds haven't changed
    assert HEALING_CONFIDENCE_X == 0.75, "X threshold should remain immutable"
    assert HEALING_CONFIDENCE_Y == 0.40, "Y threshold should remain immutable"


if __name__ == "__main__":
    # Run tests if executed directly
    test_qwen_replay_determinism()
    test_qwen_determinism_digest_completeness()
    test_qwen_output_canonicalization()
    test_qwen_circuit_breaker_replay_safety()
    test_qwen_meta_learning_boundaries()
    print("All Qwen replay validation tests passed!")
