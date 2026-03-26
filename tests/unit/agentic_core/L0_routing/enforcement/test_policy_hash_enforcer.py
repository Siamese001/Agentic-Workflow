"""
Unit tests for PolicyHashEnforcer (Gap 2 — policy hash at L0 routing entry).
"""

from __future__ import annotations

import hashlib
import json

import pytest

#  # MOVED: from agentic_core.L0_routing.enforcement.policy_hash_enforcer import (
    PolicyHashEnforcer,
    PolicyHashViolation,
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

# REMOVED: _emit_emits_metric_event("test_policy_hash_enforcer", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_policy_hash_enforcer", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_policy_hash_enforcer", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_policy_hash_enforcer", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_policy_hash_enforcer", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_policy_hash_enforcer", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_policy_hash_enforcer", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_policy_hash_enforcer", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_policy_hash_enforcer", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_policy_hash_enforcer", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_policy_hash_enforcer", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_policy_hash_enforcer", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_policy_hash_enforcer", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_policy_hash_enforcer", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_policy_hash_enforcer", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_policy_hash_enforcer", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_policy_hash_enforcer", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_policy_hash_enforcer", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_policy_hash_enforcer", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_policy_hash_enforcer", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_policy_hash_enforcer", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_policy_hash_enforcer", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_policy_hash_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_policy_hash_enforcer", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_policy_hash_enforcer", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_policy_hash_enforcer", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_policy_hash_enforcer", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_policy_hash_enforcer", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_policy_hash_enforcer")
# REMOVED: _emit_applies_guardrail("p0", "test_policy_hash_enforcer", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_policy_hash_enforcer", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_policy_hash_enforcer", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_policy_hash_enforcer", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_policy_hash_enforcer", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_policy_hash_enforcer", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_policy_hash_enforcer", "write_through")
# REMOVED: _emit_writes_through("p1", "test_policy_hash_enforcer", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_policy_hash_enforcer", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_policy_hash_enforcer", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_policy_hash_enforcer", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_policy_hash_enforcer", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_policy_hash_enforcer", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_policy_hash_enforcer", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_policy_hash_enforcer", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_policy_hash_enforcer", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_policy_hash_enforcer", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_policy_hash_enforcer", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_policy_hash_enforcer", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_policy_hash_enforcer", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_policy_hash_enforcer", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_policy_hash_enforcer", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_policy_hash_enforcer")
# REMOVED: _emit_gated_by_confidence("p1", "test_policy_hash_enforcer", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_policy_hash_enforcer")
# REMOVED: emit_determinism_digest("p0", "test_policy_hash_enforcer")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_policy_hash_enforcer", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_policy_hash_enforcer", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_policy_hash_enforcer", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_policy_hash_enforcer", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_policy_hash_enforcer", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_policy_hash_enforcer", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_policy_hash_enforcer", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_policy_hash_enforcer", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_policy_hash_enforcer", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_policy_hash_enforcer", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_policy_hash_enforcer", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_policy_hash_enforcer", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_policy_hash_enforcer", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_policy_hash_enforcer", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_policy_hash_enforcer", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_policy_hash_enforcer", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_policy_hash_enforcer", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_policy_hash_enforcer", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_policy_hash_enforcer", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_policy_hash_enforcer", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_root(config: dict) -> str:
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(canonical).hexdigest().lower()


class _FakePacket:
    def __init__(self, instruction_id: str = "test-id", policy_hash: str = "") -> None:
        self.instruction_id = instruction_id
        self.policy_hash = policy_hash


_POLICY_CONFIG = {"version": "1.0", "rules": ["deny_all_writes"]}
_ROOT = _make_root(_POLICY_CONFIG)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construction_rejects_empty_root() -> None:
        from agentic_core.L0_routing.enforcement.policy_hash_enforcer import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        with pytest.raises(ValueError, match="non-empty active_merkle_root"):
            PolicyHashEnforcer("")

        PolicyHashEnforcer("")


def test_construction_rejects_whitespace_root() -> None:
    with pytest.raises(ValueError, match="non-empty active_merkle_root"):
        PolicyHashEnforcer("   ")


def test_construction_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="Unknown mode"):
        PolicyHashEnforcer(_ROOT, mode="SOFT_FAIL")


def test_construction_stores_lowercased_root() -> None:
    enforcer = PolicyHashEnforcer(_ROOT.upper())
    assert enforcer.active_merkle_root == _ROOT.lower()


# ---------------------------------------------------------------------------
# validate() — non-raising path
# ---------------------------------------------------------------------------


def test_validate_pass_when_hash_matches() -> None:
"""Test validate_pass_when_hash_matches contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

# Act
# TODO: Validate schema
validation_result = None  # Replace with actual validation

"""Test validate_fail_when_hash_absent contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

# Act
# TODO: Validate schema
validation_result = None  # Replace with actual validation

"""Test validate_fail_when_hash_wrong contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

# Act
# TODO: Validate schema
validation_result = None  # Replace with actual validation

# Assert - Schema Contract
assert validation_result is not None, "Schema validation should produce a result"
"""Test validate_accepts_uppercase_packet_hash contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

# Act
# TODO: Validate schema
validation_result = None  # Replace with actual validation
"""Test validate_result_format_contains_status contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

# Act
# TODO: Validate schema
validation_result = None  # Replace with actual validation

"""Test validate_missing_attribute_treated_as_empty contract compliance."""
# Arrange
# TODO: Set up test data
test_data = {}  # Replace with actual test data

# Act
# TODO: Validate schema
validation_result = None  # Replace with actual validation

# Assert - Schema Contract
assert validation_result is not None, "Schema validation should produce a result"
assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
# TODO: Add specific schema validation assertions
# assert validation_result.get("valid", False), "Data should conform to schema"


def test_enforce_passes_when_hash_matches() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(policy_hash=_ROOT)
    enforcer.enforce(packet)  # must not raise


def test_enforce_raises_on_missing_hash() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(policy_hash="")
    with pytest.raises(PolicyHashViolation, match="absent"):
        enforcer.enforce(packet)


def test_enforce_raises_on_wrong_hash() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(policy_hash="b" * 64)
    with pytest.raises(PolicyHashViolation, match="mismatch"):
        enforcer.enforce(packet)


def test_enforce_violation_carries_packet_id() -> None:
    enforcer = PolicyHashEnforcer(_ROOT)
    packet = _FakePacket(instruction_id="my-packet", policy_hash="")
    exc = None
    try:
        enforcer.enforce(packet)
    except PolicyHashViolation as e:
        exc = e
    assert exc is not None
    assert exc.packet_id == "my-packet"


def test_enforce_log_only_does_not_raise() -> None:
    enforcer = PolicyHashEnforcer(_ROOT, mode="LOG_ONLY")
    packet = _FakePacket(policy_hash="")
    enforcer.enforce(packet)  # must not raise even with missing hash


# ---------------------------------------------------------------------------
# derive_root()
# ---------------------------------------------------------------------------


def test_derive_root_is_deterministic() -> None:
    config = {"a": 1, "b": [2, 3]}
    root1 = PolicyHashEnforcer.derive_root(config)
    root2 = PolicyHashEnforcer.derive_root(config)
    assert root1 == root2


def test_derive_root_matches_manual_sha256() -> None:
    config = {"version": "2", "rules": []}
    expected = _make_root(config)
    assert PolicyHashEnforcer.derive_root(config) == expected


def test_derive_root_is_key_order_independent() -> None:
    """derive_root uses sort_keys — dict key order must not matter."""
    config_a = {"b": 2, "a": 1}
    config_b = {"a": 1, "b": 2}
    assert PolicyHashEnforcer.derive_root(config_a) == PolicyHashEnforcer.derive_root(config_b)


def test_enforcer_works_with_derived_root() -> None:
    config = {"policy_version": "3", "deny_writes": True}
    root = PolicyHashEnforcer.derive_root(config)
    enforcer = PolicyHashEnforcer(root)
    packet = _FakePacket(policy_hash=root)
    enforcer.enforce(packet)  # must not raise
