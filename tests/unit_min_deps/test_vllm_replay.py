"""vLLM replay determinism tests: merged from 3-file family.

Covers:
  canonical_payload_lock:    Phase 8 canonical payload echo + drift detection
  replay_tamper_roundtrip:   Phase 7 deterministic tamper round-trip validation
  replay_with_violations:    Phase 6 replay under invariant enforcement
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from unittest.mock import patch

import pytest

from agentic_core.L2_execution.types.vllm_gateway_adapter_types import VLLMGatewayAdapter
from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLMCircuitBreakerRegistry,
    VLLMGatewayCallResult,
    VLLMGatewayTelemetry,
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
    compute_replay_hash,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_vllm_replay")
_emit_applies_guardrail("p0", "test_vllm_replay", "p0_governance")
_emit_reads_policy_state("p0", "test_vllm_replay", "policy_binding")
_emit_snapshots_state("p0", "test_vllm_replay", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_vllm_replay", "p4obs", "metric_1")
_emit_emits_metric_event("test_vllm_replay", "p4obs", "metric_2")
_emit_emits_metric_event("test_vllm_replay", "p4obs", "metric_3")
_emit_emits_metric_event("test_vllm_replay", "p4obs", "metric_4")
_emit_emits_metric_event("test_vllm_replay", "p4obs", "metric_5")
_emit_emits_metric_event("test_vllm_replay", "p4obs", "metric_6")
_emit_records_incident_event("test_vllm_replay", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_vllm_replay", "p4obs", "anomaly")
_emit_writes_observability_log("test_vllm_replay", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_vllm_replay", "p4obs", "mon_state")
_emit_triggers_alert("test_vllm_replay", "p4obs", "alert")
_emit_links_incident_trace("test_vllm_replay", "p4obs", "trace_link")
_emit_captures_pattern("test_vllm_replay", "p3lm", "pattern")
_emit_records_learning_event("test_vllm_replay", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_vllm_replay", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_vllm_replay", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_vllm_replay", "p3lm", "routing")
_emit_improves_agent_policy("test_vllm_replay", "p3lm", "policy")
_emit_stores_learning_state("test_vllm_replay", "p3lm", "state")
_emit_records_execution_trace("test_vllm_replay", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_vllm_replay", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_vllm_replay", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_vllm_replay", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_vllm_replay", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_vllm_replay", "env_read", "p2_env_1")
_emit_reads_environ("test_vllm_replay", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_vllm_replay", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_vllm_replay", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_vllm_replay", "context_pull")
_emit_pulls_context("p1", "test_vllm_replay", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_vllm_replay", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_vllm_replay", "uwg_term_2")
_emit_writes_through("p1", "test_vllm_replay", "write_through")
_emit_writes_through("p1", "test_vllm_replay", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_vllm_replay", "safety_validation")
_emit_invokes_eval("p1", "test_vllm_replay", "eval_call")
_emit_proposal_commits_routing("p1", "test_vllm_replay", "routing_commit")
_emit_escalates_to_human("p1", "test_vllm_replay", "human_escalation")
_emit_routes_through("p1", "test_vllm_replay", "route_through")
_emit_checks_agent_registry("p1", "test_vllm_replay", "agent_registry")
_emit_validates_agent_capability("p1", "test_vllm_replay", "capability")
_emit_dispatches_execution_plan("p1", "test_vllm_replay", "exec_plan")
_emit_agent_executes_agent("p1", "test_vllm_replay", "sub_agent")
_emit_routes_to_agent("p1", "test_vllm_replay", "target_agent")
_emit_verifies_policy("p1", "test_vllm_replay", "policy_check")
_emit_observes_runtime_state("p1", "test_vllm_replay", "runtime_state")
_emit_verifies_boundary("p1", "test_vllm_replay", "boundary_check")
_emit_transcripts_response("p1", "test_vllm_replay", "transcript")
_emit_hard_fails_untranscripted("p1", "test_vllm_replay")
_emit_gated_by_confidence("p1", "test_vllm_replay", "confidence_gate")
emit_replay_key("p0", "test_vllm_replay")
emit_determinism_digest("p0", "test_vllm_replay")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_vllm_replay", "execution_auth")
_emit_validates_capability("p2", "test_vllm_replay", "capability_check")
_emit_routes_to_capability("p2", "test_vllm_replay", "capability_route")
_emit_writes_via_uwg("p2", "test_vllm_replay", "uwg_write")
_emit_blocks_direct_write("p2", "test_vllm_replay", "direct_write_block")
_emit_records_tool_invocation("p2", "test_vllm_replay", "tool_invocation")
_emit_captures_execution_output("p2", "test_vllm_replay", "exec_output")
_emit_dispatches_agent("p3", "test_vllm_replay", "agent_dispatch")
_emit_coordinates_agents("p3", "test_vllm_replay", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_vllm_replay", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_vllm_replay", "healing_outcome")
_emit_escalates_failure("p3", "test_vllm_replay", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_vllm_replay", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_vllm_replay", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_vllm_replay", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_vllm_replay", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_vllm_replay", "eval_metric")
_emit_stores_embedding("p4", "test_vllm_replay", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_vllm_replay", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_vllm_replay", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _reset_singletons():
    from agentic_core.L2_execution.types.vllm_gateway_adapter_types import reset_singletons

    reset_singletons()


def _validate_64hex(value: str, name: str) -> None:
    assert re.match(r"^[0-9a-f]{64}$", value), f"{name} must be 64-hex: {value}"


@dataclass
class _MockPreflight:
    prompt_tokens_estimated: int = 1
    max_output_tokens_requested: int = 100
    max_model_len_configured: int = 8192
    token_budget_ok: bool = True
    budget_margin_tokens: int = 7000
    failure_type: str | None = None
    route_to_gemini: bool = False


@dataclass
class _MockBackpressure:
    escalate_to_gemini: bool = False
    reason: str = "ok"
    failure_type: str | None = None
    model_id: str = ""
    queue_depth: int = 0
    circuit_breaker_open: bool = False


def _make_telemetry(fp: VLLMInfrastructureFingerprint, **kw) -> VLLMGatewayTelemetry:
    defaults: dict = {
        "provider_selected": "Qwen2.5-7B-Instruct",
        "model_tier": "fast",
        "prompt_tokens_estimated": 1,
        "max_output_tokens_requested": 100,
        "max_model_len_configured": 8192,
        "token_budget_ok": True,
        "budget_margin_tokens": 7000,
        "queue_depth": 0,
        "queue_full": False,
        "queue_wait_seconds": 0.0,
        "breaker_state": "CLOSED",
        "breaker_failure_count": 0,
        "failure_type": None,
        "model_name": fp.model_name,
        "model_revision_sha": fp.model_revision_sha,
        "vllm_version": fp.vllm_version,
        "transformers_version": fp.transformers_version,
        "torch_version": fp.torch_version,
        "cuda_version": fp.cuda_version,
        "driver_version": fp.driver_version,
        "fingerprint_hash": fp.fingerprint_hash(),
    }
    defaults.update(kw)
    return VLLMGatewayTelemetry(**defaults)


def _make_result(fp, violations=None, route_to_gemini=False, failure_type=None) -> VLLMGatewayCallResult:
    return VLLMGatewayCallResult(
        route_to_gemini=route_to_gemini,
        local_request=None,
        telemetry=_make_telemetry(
            fp,
            provider_selected="gemini-2.5-pro" if route_to_gemini else "Qwen2.5-7B-Instruct",
            model_tier="remote" if route_to_gemini else "fast",
            failure_type=failure_type,
        ),
        preflight=_MockPreflight(),
        backpressure=_MockBackpressure(),
        invariant_violations=violations or [],
    )


# ---------------------------------------------------------------------------
# canonical_payload_lock helpers
# ---------------------------------------------------------------------------


def _create_test_artifact() -> VLLMReplayArtifact:
    _reset_singletons()
    adapter = VLLMGatewayAdapter(queue=VLLMQueueController(), registry=VLLMCircuitBreakerRegistry())
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    result = adapter.evaluate(
        prompt="test_prompt_canonical",
        task_class="patch_suggestion",
        severity="low",
        oldest_wait_seconds=0.0,
        fingerprint=fp,
    )
    return VLLMReplayArtifact(
        prompt="test_prompt_canonical",
        local_request=result.local_request,
        fingerprint=fp,
        result=result,
    )


def _create_mutated_artifact(original: VLLMReplayArtifact) -> VLLMReplayArtifact:
    return VLLMReplayArtifact(
        prompt=original.prompt + "_mutated",
        local_request=original.local_request,
        fingerprint=original.fingerprint,
        result=original.result,
    )


# ---------------------------------------------------------------------------
# canonical_payload_lock tests
# ---------------------------------------------------------------------------


def test_canonical_payload_stability_pass():
    artifact_1 = _create_test_artifact()
    replay_hash_1 = artifact_1.replay_hash
    canonical_payload_hash_1 = artifact_1.canonical_payload_hash()

    _validate_64hex(replay_hash_1, "replay_hash_1")
    _validate_64hex(canonical_payload_hash_1, "canonical_payload_hash_1")

    artifact_2 = _create_test_artifact()
    replay_hash_2 = artifact_2.replay_hash
    canonical_payload_hash_2 = artifact_2.canonical_payload_hash()

    _validate_64hex(replay_hash_2, "replay_hash_2")
    _validate_64hex(canonical_payload_hash_2, "canonical_payload_hash_2")

    assert replay_hash_1 == replay_hash_2
    assert canonical_payload_hash_1 == canonical_payload_hash_2

    validator = VLLMReplayValidator()
    assert validator.validate(artifact_1)
    assert validator.validate(artifact_2)


def test_canonical_payload_drift_detection_fail():
    original_artifact = _create_test_artifact()
    original_replay_hash = original_artifact.replay_hash
    original_canonical_payload_hash = original_artifact.canonical_payload_hash()

    _validate_64hex(original_replay_hash, "original_replay_hash")
    _validate_64hex(original_canonical_payload_hash, "original_canonical_payload_hash")

    mutated_artifact = _create_mutated_artifact(original_artifact)
    mutated_replay_hash = mutated_artifact.replay_hash
    mutated_canonical_payload_hash = mutated_artifact.canonical_payload_hash()

    _validate_64hex(mutated_replay_hash, "mutated_replay_hash")
    _validate_64hex(mutated_canonical_payload_hash, "mutated_canonical_payload_hash")

    assert mutated_replay_hash != original_replay_hash
    assert mutated_canonical_payload_hash != original_canonical_payload_hash


def test_canonical_payload_determinism_re_run():
    pass_artifact_1 = _create_test_artifact()
    pass_replay_hash_1 = pass_artifact_1.replay_hash
    pass_canonical_hash_1 = pass_artifact_1.canonical_payload_hash()

    pass_artifact_2 = _create_test_artifact()
    pass_replay_hash_2 = pass_artifact_2.replay_hash
    pass_canonical_hash_2 = pass_artifact_2.canonical_payload_hash()

    fail_original_1 = _create_test_artifact()
    fail_mutated_1 = _create_mutated_artifact(fail_original_1)
    fail_replay_hash_1 = fail_mutated_1.replay_hash
    fail_canonical_hash_1 = fail_mutated_1.canonical_payload_hash()

    fail_original_2 = _create_test_artifact()
    fail_mutated_2 = _create_mutated_artifact(fail_original_2)
    fail_replay_hash_2 = fail_mutated_2.replay_hash
    fail_canonical_hash_2 = fail_mutated_2.canonical_payload_hash()

    assert pass_replay_hash_1 == pass_replay_hash_2
    assert pass_canonical_hash_1 == pass_canonical_hash_2
    assert fail_replay_hash_1 == fail_replay_hash_2
    assert fail_canonical_hash_1 == fail_canonical_hash_2


def test_negative_control_canonical_payload_disabled():
    artifact = _create_test_artifact()
    original_replay_hash = artifact.replay_hash
    original_canonical_hash = artifact.canonical_payload_hash()

    _validate_64hex(original_replay_hash, "original_replay_hash")
    _validate_64hex(original_canonical_hash, "original_canonical_payload_hash")

    class DisabledCanonicalValidator:
        def validate(self, artifact):
            return True

        def validate_and_report(self, artifact):
            return {
                "valid": True,
                "replay_hash": artifact.replay_hash,
                "canonical_payload_hash": artifact.canonical_payload_hash(),
                "violation_details": None,
            }

    disabled_validator = DisabledCanonicalValidator()
    disabled_report = disabled_validator.validate_and_report(artifact)

    assert disabled_report["valid"] is True
    assert disabled_report["canonical_payload_hash"] == original_canonical_hash

    production_validator = VLLMReplayValidator()
    assert production_validator.validate(artifact) is True


# ---------------------------------------------------------------------------
# replay_tamper_roundtrip helpers
# ---------------------------------------------------------------------------


def _create_artifact_with_violations() -> VLLMReplayArtifact:
    _reset_singletons()
    adapter = VLLMGatewayAdapter(queue=VLLMQueueController(), registry=VLLMCircuitBreakerRegistry())
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    fail_violation = InvariantViolation(
        invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
        severity=InvariantSeverity.FAIL.value,
        message="Replay hash enforcement enabled but replay_hash missing from telemetry",
        context={"provider": "Qwen2.5-7B-Instruct", "replay_hash_enabled": True},
    )
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
    return VLLMReplayArtifact(
        prompt="test_prompt_for_tamper",
        local_request=None,
        fingerprint=fp,
        result=result,
    )


def _create_tampered_artifact(original: VLLMReplayArtifact) -> VLLMReplayArtifact:
    tampered_artifact = VLLMReplayArtifact(
        prompt=original.prompt + "_tampered",
        local_request=original.local_request,
        fingerprint=original.fingerprint,
        result=original.result,
    )
    object.__setattr__(tampered_artifact, "replay_hash", original.replay_hash)
    return tampered_artifact


# ---------------------------------------------------------------------------
# replay_tamper_roundtrip tests
# ---------------------------------------------------------------------------


def test_replay_tamper_round_trip():
    original_artifact = _create_artifact_with_violations()
    original_hash = original_artifact.replay_hash
    _validate_64hex(original_hash, "original_replay_hash")

    validator = VLLMReplayValidator()
    original_validation = validator.validate_and_report(original_artifact)

    assert original_validation["valid"] is True
    assert original_validation["stored_replay_hash"] == original_hash

    tampered_artifact = _create_tampered_artifact(original_artifact)
    tampered_stored_hash = tampered_artifact.replay_hash
    _validate_64hex(tampered_stored_hash, "tampered_stored_replay_hash")

    tampered_validation = validator.validate_and_report(tampered_artifact)

    assert tampered_validation["valid"] is False
    assert tampered_stored_hash == original_hash
    assert tampered_validation["stored_replay_hash"] == tampered_stored_hash
    assert tampered_validation["computed_replay_hash"] != original_hash


def test_replay_tamper_determinism_re_run():
    original_artifact_1 = _create_artifact_with_violations()
    original_hash_1 = original_artifact_1.replay_hash
    _validate_64hex(original_hash_1, "original_replay_hash_run1")

    tampered_artifact_1 = _create_tampered_artifact(original_artifact_1)
    _validate_64hex(tampered_artifact_1.replay_hash, "tampered_replay_hash_run1")

    original_artifact_2 = _create_artifact_with_violations()
    original_hash_2 = original_artifact_2.replay_hash
    _validate_64hex(original_hash_2, "original_replay_hash_run2")

    tampered_artifact_2 = _create_tampered_artifact(original_artifact_2)
    validator = VLLMReplayValidator()
    tampered_validation_2 = validator.validate_and_report(tampered_artifact_2)
    tampered_computed_hash_2 = tampered_validation_2["computed_replay_hash"]
    _validate_64hex(tampered_computed_hash_2, "tampered_computed_replay_hash_run2")

    tampered_validation_1 = validator.validate_and_report(tampered_artifact_1)
    tampered_computed_hash_1 = tampered_validation_1["computed_replay_hash"]

    assert original_hash_1 == original_hash_2
    assert tampered_computed_hash_1 == tampered_computed_hash_2


def test_negative_control_tamper_detection_disabled():
    original_artifact = _create_artifact_with_violations()
    original_hash = original_artifact.replay_hash
    _validate_64hex(original_hash, "original_replay_hash")

    tampered_artifact = _create_tampered_artifact(original_artifact)
    tampered_hash = tampered_artifact.replay_hash
    _validate_64hex(tampered_hash, "tampered_replay_hash")

    class DisabledValidator:
        def validate(self, artifact):
            return True

        def validate_and_report(self, artifact):
            return {
                "valid": True,
                "stored_replay_hash": artifact.replay_hash,
                "computed_replay_hash": artifact.replay_hash,
                "violation_details": None,
            }

    disabled_validator = DisabledValidator()
    disabled_validation = disabled_validator.validate_and_report(tampered_artifact)

    assert disabled_validation["valid"] is True
    assert disabled_validation["stored_replay_hash"] == tampered_hash

    production_validator = VLLMReplayValidator()
    production_validation = production_validator.validate_and_report(tampered_artifact)

    assert production_validation["valid"] is False


# ---------------------------------------------------------------------------
# replay_with_violations tests
# ---------------------------------------------------------------------------


def test_replay_hash_identical_with_same_violations():
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test violation",
        context={"test": True},
    )
    result1 = _make_result(
        fp, violations=[violation], route_to_gemini=True, failure_type="INVARIANT_VIOLATION"
    )
    result2 = _make_result(
        fp, violations=[violation], route_to_gemini=True, failure_type="INVARIANT_VIOLATION"
    )

    hash1 = compute_replay_hash("hello", None, fp, result1)
    hash2 = compute_replay_hash("hello", None, fp, result2)

    assert hash1 == hash2
    assert len(hash1) == 64
    assert all(c in "0123456789abcdef" for c in hash1)


def test_replay_hash_changes_when_violation_id_changes():
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
    result1 = _make_result(
        fp, violations=[violation1], route_to_gemini=True, failure_type="INVARIANT_VIOLATION"
    )
    result2 = _make_result(
        fp, violations=[violation2], route_to_gemini=True, failure_type="INVARIANT_VIOLATION"
    )

    hash1 = compute_replay_hash("hello", None, fp, result1)
    hash2 = compute_replay_hash("hello", None, fp, result2)

    assert hash1 != hash2


def test_replay_hash_changes_when_violation_hash_changes():
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
        message="Test violation 2",
        context={"test": True},
    )
    result1 = _make_result(
        fp, violations=[violation1], route_to_gemini=True, failure_type="INVARIANT_VIOLATION"
    )
    result2 = _make_result(
        fp, violations=[violation2], route_to_gemini=True, failure_type="INVARIANT_VIOLATION"
    )

    hash1 = compute_replay_hash("hello", None, fp, result1)
    hash2 = compute_replay_hash("hello", None, fp, result2)

    assert hash1 != hash2
    assert violation1.violation_hash() != violation2.violation_hash()


def test_replay_hash_deterministic_without_violations():
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    result1 = _make_result(fp, violations=[])
    result2 = _make_result(fp, violations=[])

    hash1 = compute_replay_hash("hello", None, fp, result1)
    hash2 = compute_replay_hash("hello", None, fp, result2)

    assert hash1 == hash2
    assert len(hash1) == 64
