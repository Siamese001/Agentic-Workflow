"""
PHASE 4 WAVE 3 tests — VLLMReplayValidator unit tests.

Tests deterministic replay hashing, replay artifact validation, and tamper detection.
No GPU imports. Pure L2.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_vllm_replay_validator")
_emit_applies_guardrail("p0", "test_vllm_replay_validator", "p0_governance")
_emit_reads_policy_state("p0", "test_vllm_replay_validator", "policy_binding")
_emit_snapshots_state("p0", "test_vllm_replay_validator", "state_snapshot")
emit_replay_key("p0", "test_vllm_replay_validator")
emit_determinism_digest("p0", "test_vllm_replay_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_vllm_replay_validator", "execution_auth")
_emit_validates_capability("p2", "test_vllm_replay_validator", "capability_check")
_emit_routes_to_capability("p2", "test_vllm_replay_validator", "capability_route")
_emit_writes_via_uwg("p2", "test_vllm_replay_validator", "uwg_write")
_emit_blocks_direct_write("p2", "test_vllm_replay_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "test_vllm_replay_validator", "tool_invocation")
_emit_captures_execution_output("p2", "test_vllm_replay_validator", "exec_output")
_emit_dispatches_agent("p3", "test_vllm_replay_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "test_vllm_replay_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_vllm_replay_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_vllm_replay_validator", "healing_outcome")
_emit_escalates_failure("p3", "test_vllm_replay_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_vllm_replay_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_vllm_replay_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_vllm_replay_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_vllm_replay_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_vllm_replay_validator", "eval_metric")
_emit_stores_embedding("p4", "test_vllm_replay_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_vllm_replay_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_vllm_replay_validator", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLMCircuitBreakerRegistry,
    VLLMQueueController,
    evaluate_gateway_call,
)
from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
    VLLMInfrastructureFingerprint,
    sha256_hex,
)
from agentic_core.L2_execution.types.vllm_replay_validator_types import (
    VLLMReplayArtifact,
    VLLMReplayValidator,
    canonical_local_request_hash,
    canonical_prompt_hash,
    canonical_response_hash,
    compute_replay_hash,
)
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
    from agentic_core.L2_execution.types.vllm_token_budget_types import (
        SAFETY_MARGIN_TOKENS,
        TASK_CLASS_OUTPUT_CAPS,
    )

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
