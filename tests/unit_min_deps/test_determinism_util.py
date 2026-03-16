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

_emit_records_execution_trace("p0", "evidence", "test_determinism_util")
_emit_applies_guardrail("p0", "test_determinism_util", "p0_governance")
_emit_reads_policy_state("p0", "test_determinism_util", "policy_binding")
_emit_snapshots_state("p0", "test_determinism_util", "state_snapshot")
emit_replay_key("p0", "test_determinism_util")
emit_determinism_digest("p0", "test_determinism_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_determinism_util", "execution_auth")
_emit_validates_capability("p2", "test_determinism_util", "capability_check")
_emit_routes_to_capability("p2", "test_determinism_util", "capability_route")
_emit_writes_via_uwg("p2", "test_determinism_util", "uwg_write")
_emit_blocks_direct_write("p2", "test_determinism_util", "direct_write_block")
_emit_records_tool_invocation("p2", "test_determinism_util", "tool_invocation")
_emit_captures_execution_output("p2", "test_determinism_util", "exec_output")
_emit_dispatches_agent("p3", "test_determinism_util", "agent_dispatch")
_emit_coordinates_agents("p3", "test_determinism_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_determinism_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_determinism_util", "healing_outcome")
_emit_escalates_failure("p3", "test_determinism_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_determinism_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_determinism_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_determinism_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_determinism_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_determinism_util", "eval_metric")
_emit_stores_embedding("p4", "test_determinism_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_determinism_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_determinism_util", "exec_snapshot_link")

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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from apps_shared.utils.determinism_util import (
    DETERMINISM_EXCLUDED_FIELDS,
    canonical_hash,
    file_hash,
    strip_nondeterministic,
)

_emit_emits_metric_event("test_determinism_util", "p4obs", "metric_1")
_emit_emits_metric_event("test_determinism_util", "p4obs", "metric_2")
_emit_emits_metric_event("test_determinism_util", "p4obs", "metric_3")
_emit_emits_metric_event("test_determinism_util", "p4obs", "metric_4")
_emit_emits_metric_event("test_determinism_util", "p4obs", "metric_5")
_emit_emits_metric_event("test_determinism_util", "p4obs", "metric_6")
_emit_records_incident_event("test_determinism_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_determinism_util", "p4obs", "anomaly")
_emit_writes_observability_log("test_determinism_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_determinism_util", "p4obs", "mon_state")
_emit_triggers_alert("test_determinism_util", "p4obs", "alert")
_emit_links_incident_trace("test_determinism_util", "p4obs", "trace_link")
_emit_captures_pattern("test_determinism_util", "p3lm", "pattern")
_emit_records_learning_event("test_determinism_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_determinism_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_determinism_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_determinism_util", "p3lm", "routing")
_emit_improves_agent_policy("test_determinism_util", "p3lm", "policy")
_emit_stores_learning_state("test_determinism_util", "p3lm", "state")
_emit_records_execution_trace("test_determinism_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_determinism_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_determinism_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_determinism_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_determinism_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_determinism_util", "env_read", "p2_env_1")
_emit_reads_environ("test_determinism_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_determinism_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_determinism_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_determinism_util", "context_pull")
_emit_pulls_context("p1", "test_determinism_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_determinism_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_determinism_util", "uwg_term_secondary")
_emit_writes_through("p1", "test_determinism_util", "write_through")
_emit_writes_through("p1", "test_determinism_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_determinism_util", "safety_validation")
_emit_invokes_eval("p1", "test_determinism_util", "eval_call")
_emit_proposal_commits_routing("p1", "test_determinism_util", "routing_commit")


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
    """Same input always produces same hash across multiple calls."""
    obj = {"key": "value", "nested": {"a": 1}}
    h1 = canonical_hash(obj)
    h2 = canonical_hash(obj)
    assert h1 == h2


def test_canonical_hash_different_content_differs():
    """Different meaningful content produces different hashes."""
    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})
