"""vLLM invariant contract + verifier tests: merged from 2-file family.

Covers:
  invariant_contract:  InvariantViolation canonical JSON, hashing, as_dict, enum stability
  invariant_verifier:  verify_gateway_invariants — all per-invariant pass/fail cases
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

#  # MOVED: from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
    InvariantId,
    InvariantSeverity,
    InvariantViolation,
)
#  # MOVED: from agentic_core.L2_execution.types.vllm_invariant_verifier_types import (
    verify_gateway_invariants,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_vllm_contracts", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_vllm_contracts", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_vllm_contracts", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_vllm_contracts", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_vllm_contracts", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_vllm_contracts", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_vllm_contracts", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_vllm_contracts", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_vllm_contracts", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_vllm_contracts", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_vllm_contracts", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_vllm_contracts", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_vllm_contracts", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_vllm_contracts", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_vllm_contracts", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_vllm_contracts", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_vllm_contracts", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_vllm_contracts", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_vllm_contracts", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_vllm_contracts", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_vllm_contracts", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_vllm_contracts", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_vllm_contracts", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_vllm_contracts", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_vllm_contracts", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_vllm_contracts", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_vllm_contracts", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_vllm_contracts", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_vllm_contracts")
# REMOVED: _emit_applies_guardrail("p0", "test_vllm_contracts", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_vllm_contracts", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_vllm_contracts", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_vllm_contracts", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_vllm_contracts", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_vllm_contracts", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_vllm_contracts", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_vllm_contracts", "write_through")
# REMOVED: _emit_writes_through("p1", "test_vllm_contracts", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_vllm_contracts", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_vllm_contracts", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_vllm_contracts", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_vllm_contracts", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_vllm_contracts", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_vllm_contracts", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_vllm_contracts", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_vllm_contracts", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_vllm_contracts", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_vllm_contracts", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_vllm_contracts", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_vllm_contracts", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_vllm_contracts", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_vllm_contracts", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_vllm_contracts")
# REMOVED: _emit_gated_by_confidence("p1", "test_vllm_contracts", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_vllm_contracts")
# REMOVED: emit_determinism_digest("p0", "test_vllm_contracts")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_vllm_contracts", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_vllm_contracts", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_vllm_contracts", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_vllm_contracts", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_vllm_contracts", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_vllm_contracts", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_vllm_contracts", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_vllm_contracts", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_vllm_contracts", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_vllm_contracts", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_vllm_contracts", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_vllm_contracts", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_vllm_contracts", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_vllm_contracts", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_vllm_contracts", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_vllm_contracts", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_vllm_contracts", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_vllm_contracts", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_vllm_contracts", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_vllm_contracts", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


# ===========================================================================
# invariant_contract tests
# ===========================================================================


def test_invariant_violation_canonical_json_stable():
        from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
        from agentic_core.L2_execution.types.vllm_invariant_verifier_types import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_TEMPERATURE_ZERO.value,
        severity=InvariantSeverity.WARN.value,
        message="Test",
        context={"z": 1, "a": 2, "m": 3},
    )

    json_str = violation.canonical_json()
    parsed = json.loads(json_str)

    assert list(parsed.keys()) == ["context", "invariant_id", "message", "severity"]
    assert list(parsed["context"].keys()) == ["a", "m", "z"]


def test_invariant_violation_hash_deterministic():
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
    assert InvariantId.INV_NO_GPU_IMPORTS_IN_L0_L6.value == "INV_NO_GPU_IMPORTS_IN_L0_L6"
    assert (
        InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value
        == "INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS"
    )
    assert InvariantId.INV_LOCAL_REQUEST_TEMPERATURE_ZERO.value == "INV_LOCAL_REQUEST_TEMPERATURE_ZERO"
    assert InvariantId.INV_LOCAL_REQUEST_SEED_PRESENT.value == "INV_LOCAL_REQUEST_SEED_PRESENT"
    assert InvariantId.INV_TELEMETRY_HAS_FINGERPRINT_HASH.value == "INV_TELEMETRY_HAS_FINGERPRINT_HASH"
    assert InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value == "INV_REPLAY_HASH_PRESENT_WHEN_ENABLED"
    assert InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value == "INV_GEMINI_FALLBACK_REQUIRES_REASON"


def test_invariant_severity_enum_values():
    assert InvariantSeverity.INFO.value == "INFO"
    assert InvariantSeverity.WARN.value == "WARN"
    assert InvariantSeverity.FAIL.value == "FAIL"


def test_invariant_violation_frozen():
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test",
        context={},
    )

    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        violation.message = "Changed"


# ===========================================================================
# invariant_verifier tests
# ===========================================================================


@dataclass
class MinimalLocalRequest:
    max_tokens: int | None = None
    temperature: float | None = None
    seed: int | None = None


def test_verify_no_violations_on_valid_local_request():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123", "failure_type": None}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert violations == []


def test_inv_missing_max_tokens():
    local_request = MinimalLocalRequest(max_tokens=None, temperature=0.0, seed=42)
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
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.7, seed=42)
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
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=None)
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
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
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
    telemetry_dict = {"fingerprint_hash": "abc123", "failure_type": None}

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
    telemetry_dict = {"fingerprint_hash": "abc123", "failure_type": "TOKEN_BUDGET_EXCEEDED"}

    violations = verify_gateway_invariants(
        provider_selected="gemini-2.5-pro",
        local_request=None,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    gemini_violations = [
        v for v in violations if v.invariant_id == InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value
    ]
    assert gemini_violations == []


def test_multiple_violations_sorted_deterministically():
"""Test multiple_violations_sorted_deterministically runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute multiple_violations_sorted_deterministically
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions


def test_violations_are_deterministic():
    local_request = MinimalLocalRequest(max_tokens=None, temperature=0.0, seed=42)
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


def test_inv_replay_hash_missing_when_enabled():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
        replay_hash_enabled=True,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "replay_hash" in violations[0].message.lower()


def test_inv_replay_hash_present_when_enabled_no_violation():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123", "replay_hash": "def456"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
        replay_hash_enabled=True,
    )

    replay_violations = [
        v for v in violations if v.invariant_id == InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value
    ]
    assert replay_violations == []


def test_inv_replay_hash_disabled_no_violation():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
        replay_hash_enabled=False,
    )

    replay_violations = [
        v for v in violations if v.invariant_id == InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value
    ]
    assert replay_violations == []


def test_inv_gpu_import_policy_violation():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
        gpu_import_policy_ok=False,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_NO_GPU_IMPORTS_IN_L0_L6.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "gpu import policy" in violations[0].message.lower()


def test_inv_gpu_import_policy_ok_no_violation():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
        gpu_import_policy_ok=True,
    )

    gpu_violations = [
        v for v in violations if v.invariant_id == InvariantId.INV_NO_GPU_IMPORTS_IN_L0_L6.value
    ]
    assert gpu_violations == []
