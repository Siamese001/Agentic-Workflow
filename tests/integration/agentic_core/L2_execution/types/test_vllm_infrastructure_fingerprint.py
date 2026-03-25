"""
PHASE 4 WAVE 2 tests — VLLMInfrastructureFingerprint unit tests.

Tests deterministic serialization, hashing, and field change detection.
No GPU imports. Pure L2.
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_vllm_infrastructure_fingerprint")
# REMOVED: _emit_applies_guardrail("p0", "test_vllm_infrastructure_fingerprint", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_vllm_infrastructure_fingerprint", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_vllm_infrastructure_fingerprint", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_vllm_infrastructure_fingerprint")
# REMOVED: emit_determinism_digest("p0", "test_vllm_infrastructure_fingerprint")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_vllm_infrastructure_fingerprint", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_vllm_infrastructure_fingerprint", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_vllm_infrastructure_fingerprint", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_vllm_infrastructure_fingerprint", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_vllm_infrastructure_fingerprint", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_vllm_infrastructure_fingerprint", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_vllm_infrastructure_fingerprint", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_vllm_infrastructure_fingerprint", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_vllm_infrastructure_fingerprint", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_vllm_infrastructure_fingerprint", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_vllm_infrastructure_fingerprint", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_vllm_infrastructure_fingerprint", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_vllm_infrastructure_fingerprint", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_vllm_infrastructure_fingerprint", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_vllm_infrastructure_fingerprint", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_vllm_infrastructure_fingerprint", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_vllm_infrastructure_fingerprint", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_vllm_infrastructure_fingerprint", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_vllm_infrastructure_fingerprint", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_vllm_infrastructure_fingerprint", "exec_snapshot_link")

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

from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
    VLLMInfrastructureFingerprint,
    canonical_json,
    sha256_hex,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_vllm_infrastructure_fingerprint", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_vllm_infrastructure_fingerprint", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_vllm_infrastructure_fingerprint", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_vllm_infrastructure_fingerprint", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_vllm_infrastructure_fingerprint", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_vllm_infrastructure_fingerprint", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_vllm_infrastructure_fingerprint", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_vllm_infrastructure_fingerprint", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_vllm_infrastructure_fingerprint", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_vllm_infrastructure_fingerprint", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_vllm_infrastructure_fingerprint", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_vllm_infrastructure_fingerprint", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_vllm_infrastructure_fingerprint", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_vllm_infrastructure_fingerprint", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_vllm_infrastructure_fingerprint", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_vllm_infrastructure_fingerprint", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_vllm_infrastructure_fingerprint", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_vllm_infrastructure_fingerprint", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_vllm_infrastructure_fingerprint", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_vllm_infrastructure_fingerprint", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_vllm_infrastructure_fingerprint", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_vllm_infrastructure_fingerprint", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_vllm_infrastructure_fingerprint", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_vllm_infrastructure_fingerprint", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_vllm_infrastructure_fingerprint", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_vllm_infrastructure_fingerprint", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_vllm_infrastructure_fingerprint", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_vllm_infrastructure_fingerprint", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_vllm_infrastructure_fingerprint", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_vllm_infrastructure_fingerprint", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_vllm_infrastructure_fingerprint", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_vllm_infrastructure_fingerprint", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_vllm_infrastructure_fingerprint", "write_through")
# REMOVED: _emit_writes_through("p1", "test_vllm_infrastructure_fingerprint", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_vllm_infrastructure_fingerprint", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_vllm_infrastructure_fingerprint", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_vllm_infrastructure_fingerprint", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_vllm_infrastructure_fingerprint", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_vllm_infrastructure_fingerprint", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_vllm_infrastructure_fingerprint", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_vllm_infrastructure_fingerprint", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_vllm_infrastructure_fingerprint", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_vllm_infrastructure_fingerprint", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_vllm_infrastructure_fingerprint", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_vllm_infrastructure_fingerprint", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_vllm_infrastructure_fingerprint", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_vllm_infrastructure_fingerprint", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_vllm_infrastructure_fingerprint", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_vllm_infrastructure_fingerprint")
# REMOVED: _emit_gated_by_confidence("p1", "test_vllm_infrastructure_fingerprint", "confidence_gate")


def test_fingerprint_canonical_serialization_stable():
    """Canonical JSON serialization is stable across calls."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    json1 = fp.canonical_json()
    json2 = fp.canonical_json()
    assert json1 == json2
    # Verify no whitespace and sorted keys
    assert " " not in json1
    assert "\n" not in json1
    # Keys should be in alphabetical order
    keys = list(json.loads(json1).keys())
    assert keys == sorted(keys)


def test_fingerprint_hash_changes_on_field_change():
    """Fingerprint hash changes when any field changes."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    original_hash = fp.fingerprint_hash()

    # Change each field and verify hash changes
    fields_to_change = {
        "model_name": "DifferentModel",
        "model_revision_sha": "def456abc123",
        "vllm_version": "0.6.4",
        "transformers_version": "4.46.1",
        "torch_version": "2.5.2",
        "cuda_version": "12.5",
        "driver_version": "550.54.15",
    }

    for field, new_value in fields_to_change.items():
        kwargs = fp.as_dict()
        kwargs[field] = new_value
        modified_fp = VLLMInfrastructureFingerprint(**kwargs)
        modified_hash = modified_fp.fingerprint_hash()
        assert modified_hash != original_hash
        assert len(modified_hash) == 64  # SHA256 hex length


def test_fingerprint_deterministic_test_instance():
    """Deterministic test instance always produces same values."""
    fp1 = VLLMInfrastructureFingerprint.deterministic_test_instance()
    fp2 = VLLMInfrastructureFingerprint.deterministic_test_instance()
    assert fp1 == fp2
    assert fp1.fingerprint_hash() == fp2.fingerprint_hash()
    assert fp1.model_name == "Qwen2.5-7B-Instruct"


def test_canonical_json_stable_keys():
    """canonical_json produces stable key ordering."""
    data = {"z": 1, "a": 2, "m": 3}
    json1 = canonical_json(data)
    json2 = canonical_json(data)
    assert json1 == json2
    assert json1 == '{"a":2,"m":3,"z":1}'


def test_sha256_hex_consistent():
    """sha256_hex produces consistent hashes."""
    data = "test string"
    hash1 = sha256_hex(data)
    hash2 = sha256_hex(data)
    assert hash1 == hash2
    assert len(hash1) == 64
    # Verify against known SHA256 of "test string"
    expected = "d5579c46dfcc7f18207013e65b44e4cb4e2c2298f4ac457ba8f82743f31e930b"
    assert hash1 == expected


def test_fingerprint_as_dict_roundtrip():
    """as_dict() produces values that can reconstruct fingerprint."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    data = fp.as_dict()
    fp2 = VLLMInfrastructureFingerprint(**data)
    assert fp == fp2
    assert fp.fingerprint_hash() == fp2.fingerprint_hash()
