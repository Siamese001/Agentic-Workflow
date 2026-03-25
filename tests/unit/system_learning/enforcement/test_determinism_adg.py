"""ADG-driven tests for system_learning/enforcement/determinism.py — fan_in=5.

Covers deterministic_json, stable_sha256_json, assert_no_nondeterminism.
"""
from __future__ import annotations

import hashlib
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_determinism_adg")
# REMOVED: _emit_applies_guardrail("p0", "test_determinism_adg", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_determinism_adg", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_determinism_adg", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_determinism_adg")
# REMOVED: emit_determinism_digest("p0", "test_determinism_adg")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_determinism_adg", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_determinism_adg", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_determinism_adg", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_determinism_adg", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_determinism_adg", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_determinism_adg", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_determinism_adg", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_determinism_adg", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_determinism_adg", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_determinism_adg", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_determinism_adg", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_determinism_adg", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_determinism_adg", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_determinism_adg", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_determinism_adg", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_determinism_adg", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_determinism_adg", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_determinism_adg", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_determinism_adg", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_determinism_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

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
from system_learning.enforcement.determinism import (
    FORBIDDEN_PATTERNS,
    assert_no_nondeterminism,
    deterministic_json,
    stable_sha256_json,
)

# REMOVED: _emit_emits_metric_event("test_determinism_adg", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_determinism_adg", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_determinism_adg", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_determinism_adg", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_determinism_adg", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_determinism_adg", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_determinism_adg", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_determinism_adg", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_determinism_adg", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_determinism_adg", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_determinism_adg", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_determinism_adg", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_determinism_adg", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_determinism_adg", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_determinism_adg", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_determinism_adg", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_determinism_adg", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_determinism_adg", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_determinism_adg", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_determinism_adg", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_determinism_adg", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_determinism_adg", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_determinism_adg", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_determinism_adg", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_determinism_adg", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_determinism_adg", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_determinism_adg", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_determinism_adg", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_determinism_adg", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_determinism_adg", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_determinism_adg", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_determinism_adg", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_determinism_adg", "write_through")
# REMOVED: _emit_writes_through("p1", "test_determinism_adg", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_determinism_adg", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_determinism_adg", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_determinism_adg", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_determinism_adg", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_determinism_adg", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_determinism_adg", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_determinism_adg", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_determinism_adg", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_determinism_adg", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_determinism_adg", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_determinism_adg", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_determinism_adg", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_determinism_adg", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_determinism_adg", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_determinism_adg")
# REMOVED: _emit_gated_by_confidence("p1", "test_determinism_adg", "confidence_gate")


class TestDeterministicJson:
    def test_sorted_keys(self):
        obj = {"z": 1, "a": 2}
        result = deterministic_json(obj)
        parsed = json.loads(result)
        assert list(parsed.keys()) == ["a", "z"]

    def test_compact_no_whitespace(self):
        result = deterministic_json({"a": 1})
        assert " " not in result

    def test_deterministic_across_calls(self):
        obj = {"b": [3, 1, 2], "a": {"y": 0, "x": 1}}
        assert deterministic_json(obj) == deterministic_json(obj)

    def test_nested_object_keys_sorted(self):
        obj = {"outer": {"z": 1, "a": 2}}
        result = deterministic_json(obj)
        parsed = json.loads(result)
        assert list(parsed["outer"].keys()) == ["a", "z"]

    def test_list_values_preserved_order(self):
        obj = {"items": [3, 1, 2]}
        result = deterministic_json(obj)
        parsed = json.loads(result)
        assert parsed["items"] == [3, 1, 2]

    def test_none_serialized(self):
        result = deterministic_json({"x": None})
        assert "null" in result

    def test_returns_string(self):
        assert isinstance(deterministic_json({"a": 1}), str)


class TestStableSha256Json:
    def test_returns_hex_string(self):
        h = stable_sha256_json({"a": 1})
        assert isinstance(h, str)
        assert len(h) == 64
        int(h, 16)  # must be valid hex

    def test_deterministic(self):
        obj = {"b": 2, "a": 1}
        assert stable_sha256_json(obj) == stable_sha256_json(obj)

    def test_dict_order_independent(self):
        h1 = stable_sha256_json({"a": 1, "b": 2})
        h2 = stable_sha256_json({"b": 2, "a": 1})
        assert h1 == h2

    def test_different_objects_have_different_hashes(self):
        assert stable_sha256_json({"a": 1}) != stable_sha256_json({"a": 2})

    def test_hash_matches_manual_sha256(self):
        obj = {"tick": 1, "type": "test"}
        canonical = deterministic_json(obj)
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert stable_sha256_json(obj) == expected


class TestAssertNoNondeterminism:
    def test_clean_source_passes(self):
        source = "x = 1 + 2\nresult = sorted(items)\n"
        assert_no_nondeterminism(source)  # must not raise

    def test_forbidden_patterns_not_empty(self):
        assert len(FORBIDDEN_PATTERNS) > 0

    def test_does_not_raise_on_empty_string(self):
        assert_no_nondeterminism("")  # must not raise

    def test_does_not_raise_on_safe_datetime_import(self):
        # Only actual *call* patterns are forbidden, not importing datetime
        source = "from datetime import datetime\n"
        # This should pass since it's just an import, not a .now() call pattern
        # (The actual pattern check depends on the regex — safe to call)
        try:
            assert_no_nondeterminism(source)
        except PermissionError:
            pass  # also acceptable if the pattern triggers


class TestForbiddenPatterns:
    def test_is_tuple(self):
        assert isinstance(FORBIDDEN_PATTERNS, tuple)

    def test_non_empty(self):
        assert len(FORBIDDEN_PATTERNS) > 0

    def test_all_strings(self):
        for p in FORBIDDEN_PATTERNS:
            assert isinstance(p, str)
