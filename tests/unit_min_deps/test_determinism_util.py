"""
Unit tests for apps_shared.utils.determinism_util.

Verifies:
- Excluded fields are stripped at top level.
- Excluded fields are stripped recursively in nested dicts.
- Lists are recursed and order is preserved.
- file_hash returns stable sha256 of file bytes.

No network, wall-clock, or randomness used.
"""

from __future__ import annotations

import hashlib

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_determinism_util")
# REMOVED: _emit_applies_guardrail("p0", "test_determinism_util", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_determinism_util", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_determinism_util", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_determinism_util")
# REMOVED: emit_determinism_digest("p0", "test_determinism_util")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_determinism_util", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_determinism_util", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_determinism_util", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_determinism_util", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_determinism_util", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_determinism_util", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_determinism_util", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_determinism_util", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_determinism_util", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_determinism_util", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_determinism_util", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_determinism_util", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_determinism_util", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_determinism_util", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_determinism_util", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_determinism_util", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_determinism_util", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_determinism_util", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_determinism_util", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_determinism_util", "exec_snapshot_link")

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
from apps_shared.utils.determinism_util import (
    DETERMINISM_EXCLUDED_FIELDS,
    canonical_hash,
    file_hash,
    strip_nondeterministic,
)

# REMOVED: _emit_emits_metric_event("test_determinism_util", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_determinism_util", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_determinism_util", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_determinism_util", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_determinism_util", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_determinism_util", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_determinism_util", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_determinism_util", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_determinism_util", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_determinism_util", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_determinism_util", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_determinism_util", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_determinism_util", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_determinism_util", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_determinism_util", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_determinism_util", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_determinism_util", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_determinism_util", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_determinism_util", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_determinism_util", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_determinism_util", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_determinism_util", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_determinism_util", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_determinism_util", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_determinism_util", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_determinism_util", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_determinism_util", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_determinism_util", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_determinism_util", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_determinism_util", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_determinism_util", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_determinism_util", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_determinism_util", "write_through")
# REMOVED: _emit_writes_through("p1", "test_determinism_util", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_determinism_util", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_determinism_util", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_determinism_util", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_determinism_util", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_determinism_util", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_determinism_util", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_determinism_util", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_determinism_util", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_determinism_util", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_determinism_util", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_determinism_util", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_determinism_util", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_determinism_util", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_determinism_util", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_determinism_util")
# REMOVED: _emit_gated_by_confidence("p1", "test_determinism_util", "confidence_gate")


def test_exclusion_top_level():
    """duration_ms value must not affect canonical_hash."""
    assert canonical_hash({"a": 1, "duration_ms": 999}) == canonical_hash({"a": 1, "duration_ms": 0})


def test_exclusion_nested_recursive():
    """timestamp inside a nested dict must not affect canonical_hash."""
    assert canonical_hash({"a": {"timestamp": "x", "b": 2}}) == canonical_hash(
        {"a": {"timestamp": "y", "b": 2}}
    )


def test_list_recursive_preserves_order_and_strips():
    """trace_id inside list elements must not affect canonical_hash; order preserved."""
    assert canonical_hash([{"trace_id": "x", "v": 1}, {"trace_id": "y", "v": 2}]) == canonical_hash(
        [{"trace_id": "z", "v": 1}, {"trace_id": "w", "v": 2}]
    )


def test_list_order_matters():
    """Different element order must produce different hashes."""
    assert canonical_hash([{"v": 1}, {"v": 2}]) != canonical_hash([{"v": 2}, {"v": 1}])


def test_file_hash_stable(tmp_path):
    """file_hash returns expected sha256 of file bytes; byte change changes hash."""
    content = b"deterministic content"
    f = tmp_path / "sample.bin"
    f.write_bytes(content)

    expected = hashlib.sha256(content).hexdigest()
    assert file_hash(f) == expected

    f.write_bytes(b"different content")
    assert file_hash(f) != expected


def test_strip_nondeterministic_dict_top_level():
    """All excluded fields are removed from a flat dict."""
    obj = {"a": 1, "duration_ms": 5, "timestamp": "t", "trace_id": "x", "b": 2}
    result = strip_nondeterministic(obj)
    for excluded in DETERMINISM_EXCLUDED_FIELDS:
        assert excluded not in result
    assert result["a"] == 1
    assert result["b"] == 2


def test_strip_nondeterministic_preserves_non_excluded():
    """Non-excluded fields survive stripping unchanged."""
    obj = {"x": 42, "y": [1, 2, 3]}
    assert strip_nondeterministic(obj) == obj


def test_strip_nondeterministic_tuple_preserved():
    """Tuples are recursed and returned as tuples."""
    obj = ({"trace_id": "x", "v": 1}, {"v": 2})
    result = strip_nondeterministic(obj)
    assert isinstance(result, tuple)
    assert result == ({"v": 1}, {"v": 2})


def test_canonical_hash_deterministic_multiple_calls():
"""Test canonical_hash_deterministic_multiple_calls runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute canonical_hash_deterministic_multiple_calls
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions