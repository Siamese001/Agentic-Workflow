"""REQ-018: all governance artifacts use HMAC-SHA256; signing is deterministic."""

from __future__ import annotations

import hashlib
import hmac

import pytest

#  # MOVED: from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
    hash_artifact_canonical,
    sign_artifact,
    verify_signature,
)
#  # MOVED: from agentic_core.L0_routing.types.crypto_trust_types import (
    DeterministicTestEnclave,
    KeyRecord,
    KeyStatus,
    SigningAlgorithm,
    TrustRoot,
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

# REMOVED: _emit_emits_metric_event("test_hmac_artifact_coverage", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_hmac_artifact_coverage", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_hmac_artifact_coverage", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_hmac_artifact_coverage", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_hmac_artifact_coverage", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_hmac_artifact_coverage", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_hmac_artifact_coverage", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_hmac_artifact_coverage", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_hmac_artifact_coverage", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_hmac_artifact_coverage", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_hmac_artifact_coverage", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_hmac_artifact_coverage", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_hmac_artifact_coverage", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_hmac_artifact_coverage", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_hmac_artifact_coverage", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_hmac_artifact_coverage", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_hmac_artifact_coverage", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_hmac_artifact_coverage", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_hmac_artifact_coverage", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_hmac_artifact_coverage", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_hmac_artifact_coverage", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_hmac_artifact_coverage", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_hmac_artifact_coverage", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_hmac_artifact_coverage", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_hmac_artifact_coverage", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_hmac_artifact_coverage", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_hmac_artifact_coverage", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_hmac_artifact_coverage", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_hmac_artifact_coverage")
# REMOVED: _emit_applies_guardrail("p0", "test_hmac_artifact_coverage", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_hmac_artifact_coverage", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_hmac_artifact_coverage", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_hmac_artifact_coverage", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_hmac_artifact_coverage", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hmac_artifact_coverage", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hmac_artifact_coverage", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_hmac_artifact_coverage", "write_through")
# REMOVED: _emit_writes_through("p1", "test_hmac_artifact_coverage", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_hmac_artifact_coverage", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_hmac_artifact_coverage", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_hmac_artifact_coverage", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_hmac_artifact_coverage", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_hmac_artifact_coverage", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_hmac_artifact_coverage", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_hmac_artifact_coverage", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_hmac_artifact_coverage", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_hmac_artifact_coverage", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_hmac_artifact_coverage", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_hmac_artifact_coverage", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_hmac_artifact_coverage", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_hmac_artifact_coverage", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_hmac_artifact_coverage", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_hmac_artifact_coverage")
# REMOVED: _emit_gated_by_confidence("p1", "test_hmac_artifact_coverage", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_hmac_artifact_coverage")
# REMOVED: emit_determinism_digest("p0", "test_hmac_artifact_coverage")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_hmac_artifact_coverage", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_hmac_artifact_coverage", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_hmac_artifact_coverage", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_hmac_artifact_coverage", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_hmac_artifact_coverage", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_hmac_artifact_coverage", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_hmac_artifact_coverage", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_hmac_artifact_coverage", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_hmac_artifact_coverage", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_hmac_artifact_coverage", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_hmac_artifact_coverage", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_hmac_artifact_coverage", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_hmac_artifact_coverage", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_hmac_artifact_coverage", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_hmac_artifact_coverage", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_hmac_artifact_coverage", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_hmac_artifact_coverage", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_hmac_artifact_coverage", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_hmac_artifact_coverage", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_hmac_artifact_coverage", "exec_snapshot_link")

_KEY_ID = "req018-hmac-key"
_KEY_SECRET = b"req018-fixed-hmac-secret-padding!"


def _make_trust_root() -> TrustRoot:
    return TrustRoot(
        keys=(
            KeyRecord(
                key_id=_KEY_ID,
                public_key=_KEY_SECRET,
                created_tick=0,
                status=KeyStatus.ACTIVE,
            ),
        )
    )


@pytest.mark.governance
def test_sign_artifact_uses_hmac_sha256() -> None:
    from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
    from agentic_core.L0_routing.types.crypto_trust_types import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    """SignatureEnvelope.algorithm MUST be HMAC_SHA256."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"instruction_id":"INS-001","payload":"run_gate"}'
    envelope = sign_artifact(artifact, _KEY_ID, enclave, "TR-001", 1)
    assert envelope.algorithm == SigningAlgorithm.HMAC_SHA256


@pytest.mark.governance
def test_sign_artifact_deterministic_across_two_runs() -> None:
"""Test sign_artifact_deterministic_across_two_runs runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute sign_artifact_deterministic_across_two_runs
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
def test_artifact_hash_is_sha256_hex() -> None:
    """hash_artifact_canonical MUST return lowercase SHA-256 hex (64 chars)."""
    artifact = b"canonical test bytes"
    digest = hash_artifact_canonical(artifact)
    expected = hashlib.sha256(artifact).hexdigest()
    assert digest == expected
    assert len(digest) == 64
    assert digest == digest.lower()


@pytest.mark.governance
def test_signature_is_expected_hmac_hex() -> None:
    """The signature stored in the envelope MUST equal HMAC-SHA256(key, artifact_bytes).hexdigest()."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"instruction_id":"INS-003","payload":"hmac_value_check"}'

    envelope = sign_artifact(artifact, _KEY_ID, enclave, "TR-003", 1)

    expected_sig = hmac.new(_KEY_SECRET, artifact, hashlib.sha256).hexdigest()
    assert envelope.signature == expected_sig


@pytest.mark.governance
def test_verify_signature_round_trip() -> None:
    """sign_artifact followed by verify_signature MUST return True."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"instruction_id":"INS-004","payload":"roundtrip"}'
    envelope = sign_artifact(artifact, _KEY_ID, enclave, "TR-004", 1)
    assert verify_signature(artifact, envelope, trust_root, enclave) is True


@pytest.mark.governance
def test_w2_determinism_digest_format() -> None:
    """SOV-DELTA: phase emits W2-DETERMINISM-DIGEST; two invocations must match."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"phase":"W2","gate":"determinism"}'
    env_a = sign_artifact(artifact, _KEY_ID, enclave, "W2-DIGEST", 0)
    env_b = sign_artifact(artifact, _KEY_ID, enclave, "W2-DIGEST", 0)
    digest_line_a = f"W2-DETERMINISM-DIGEST: {env_a.signature}"
    digest_line_b = f"W2-DETERMINISM-DIGEST: {env_b.signature}"
    assert digest_line_a == digest_line_b
