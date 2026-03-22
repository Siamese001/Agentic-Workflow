"""Unit tests for runtime_state_digest deterministic digest."""

from __future__ import annotations

import copy

import pytest

from agentic_core.L0_routing.scripts.runtime_state_digest import (
    EXCLUDE_PATHS,
    compute_runtime_state_digest,
    runtime_state_digest_view,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_runtime_state_digest", "p4obs", "metric_1")
_emit_emits_metric_event("test_runtime_state_digest", "p4obs", "metric_2")
_emit_emits_metric_event("test_runtime_state_digest", "p4obs", "metric_3")
_emit_emits_metric_event("test_runtime_state_digest", "p4obs", "metric_4")
_emit_emits_metric_event("test_runtime_state_digest", "p4obs", "metric_5")
_emit_emits_metric_event("test_runtime_state_digest", "p4obs", "metric_6")
_emit_records_incident_event("test_runtime_state_digest", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_runtime_state_digest", "p4obs", "anomaly")
_emit_writes_observability_log("test_runtime_state_digest", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_runtime_state_digest", "p4obs", "mon_state")
_emit_triggers_alert("test_runtime_state_digest", "p4obs", "alert")
_emit_links_incident_trace("test_runtime_state_digest", "p4obs", "trace_link")
_emit_captures_pattern("test_runtime_state_digest", "p3lm", "pattern")
_emit_records_learning_event("test_runtime_state_digest", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_runtime_state_digest", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_runtime_state_digest", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_runtime_state_digest", "p3lm", "routing")
_emit_improves_agent_policy("test_runtime_state_digest", "p3lm", "policy")
_emit_stores_learning_state("test_runtime_state_digest", "p3lm", "state")
_emit_records_execution_trace("test_runtime_state_digest", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_runtime_state_digest", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_runtime_state_digest", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_runtime_state_digest", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_runtime_state_digest", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_runtime_state_digest", "env_read", "p2_env_1")
_emit_reads_environ("test_runtime_state_digest", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_runtime_state_digest", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_runtime_state_digest", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_runtime_state_digest")
_emit_applies_guardrail("p0", "test_runtime_state_digest", "p0_governance")
_emit_reads_policy_state("p0", "test_runtime_state_digest", "policy_binding")
_emit_snapshots_state("p0", "test_runtime_state_digest", "state_snapshot")
_emit_pulls_context("p1", "test_runtime_state_digest", "context_pull")
_emit_pulls_context("p1", "test_runtime_state_digest", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_runtime_state_digest", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_runtime_state_digest", "uwg_term_secondary")
_emit_writes_through("p1", "test_runtime_state_digest", "write_through")
_emit_writes_through("p1", "test_runtime_state_digest", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_runtime_state_digest", "safety_validation")
_emit_invokes_eval("p1", "test_runtime_state_digest", "eval_call")
_emit_proposal_commits_routing("p1", "test_runtime_state_digest", "routing_commit")
_emit_escalates_to_human("p1", "test_runtime_state_digest", "human_escalation")
_emit_routes_through("p1", "test_runtime_state_digest", "route_through")
_emit_checks_agent_registry("p1", "test_runtime_state_digest", "agent_registry")
_emit_validates_agent_capability("p1", "test_runtime_state_digest", "capability")
_emit_dispatches_execution_plan("p1", "test_runtime_state_digest", "exec_plan")
_emit_agent_executes_agent("p1", "test_runtime_state_digest", "sub_agent")
_emit_routes_to_agent("p1", "test_runtime_state_digest", "target_agent")
_emit_verifies_policy("p1", "test_runtime_state_digest", "policy_check")
_emit_observes_runtime_state("p1", "test_runtime_state_digest", "runtime_state")
_emit_verifies_boundary("p1", "test_runtime_state_digest", "boundary_check")
_emit_transcripts_response("p1", "test_runtime_state_digest", "transcript")
_emit_hard_fails_untranscripted("p1", "test_runtime_state_digest")
_emit_gated_by_confidence("p1", "test_runtime_state_digest", "confidence_gate")
emit_replay_key("p0", "test_runtime_state_digest")
emit_determinism_digest("p0", "test_runtime_state_digest")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_runtime_state_digest", "execution_auth")
_emit_validates_capability("p2", "test_runtime_state_digest", "capability_check")
_emit_routes_to_capability("p2", "test_runtime_state_digest", "capability_route")
_emit_writes_via_uwg("p2", "test_runtime_state_digest", "uwg_write")
_emit_blocks_direct_write("p2", "test_runtime_state_digest", "direct_write_block")
_emit_records_tool_invocation("p2", "test_runtime_state_digest", "tool_invocation")
_emit_captures_execution_output("p2", "test_runtime_state_digest", "exec_output")
_emit_dispatches_agent("p3", "test_runtime_state_digest", "agent_dispatch")
_emit_coordinates_agents("p3", "test_runtime_state_digest", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_runtime_state_digest", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_runtime_state_digest", "healing_outcome")
_emit_escalates_failure("p3", "test_runtime_state_digest", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_runtime_state_digest", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_runtime_state_digest", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_runtime_state_digest", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_runtime_state_digest", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_runtime_state_digest", "eval_metric")
_emit_stores_embedding("p4", "test_runtime_state_digest", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_runtime_state_digest", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_runtime_state_digest", "exec_snapshot_link")

pytestmark = pytest.mark.unit

# ── Fixtures ────────────────────────────────────────────────────────

_BASE_STATE: dict = {
    "status": "completed",
    "start_time": "2026-02-19T19:00:00",
    "end_time": "2026-02-19T19:01:00",
    "current_agent": None,
    "current_layer": None,
    "agents_order": ["location", "classification"],
    "completed_agents": [
        {
            "agent": "location",
            "time": "2026-02-19T19:00:10",
            "success": True,
            "details": "",
        },
        {
            "agent": "classification",
            "time": "2026-02-19T19:00:30",
            "success": True,
            "details": "",
        },
    ],
    "events": [
        {
            "time": "2026-02-19T19:00:00",
            "type": "info",
            "message": "Mission started",
        },
        {
            "time": "2026-02-19T19:00:10",
            "type": "agent_start",
            "message": "location",
        },
    ],
    "meta_learning": {"enabled": False},
    "compliance_scores": {},
    "decisions_made": [],
    "compliance_report": {},
    "gravity_violations": [{"type": "GRAVITY", "violations_found": 384}],
}


# ── Test 1: timestamp variance does not change digest ───────────────


def test_timestamp_variance_same_digest():
    """Two states identical except for excluded timestamp fields
    must produce the same digest."""
    state_a = copy.deepcopy(_BASE_STATE)
    state_b = copy.deepcopy(_BASE_STATE)

    # Vary every excluded timestamp
    state_b["start_time"] = "2099-12-31T23:59:59"
    state_b["end_time"] = "2099-12-31T23:59:59"
    state_b["events"][0]["time"] = "2099-12-31T23:59:59"
    state_b["events"][1]["time"] = "2099-12-31T23:59:59"
    state_b["completed_agents"][0]["time"] = "2099-12-31T23:59:59"
    state_b["completed_agents"][1]["time"] = "2099-12-31T23:59:59"

    assert compute_runtime_state_digest(state_a) == (compute_runtime_state_digest(state_b))


# ── Test 2: semantic variance changes digest ────────────────────────


def test_semantic_variance_changes_digest():
    """Changing a meaningful field must produce a different digest."""
    state_a = copy.deepcopy(_BASE_STATE)
    state_b = copy.deepcopy(_BASE_STATE)

    state_b["gravity_violations"][0]["violations_found"] = 0

    assert compute_runtime_state_digest(state_a) != (compute_runtime_state_digest(state_b))


# ── Test 3: input immutability ──────────────────────────────────────


def test_digest_view_does_not_mutate_input():
    """runtime_state_digest_view must not mutate the input dict."""
    original = copy.deepcopy(_BASE_STATE)
    frozen = copy.deepcopy(original)

    runtime_state_digest_view(original)

    assert original == frozen


# ── Test 4: digest field self-exclusion ─────────────────────────────


def test_digest_field_excluded_from_own_computation():
    """Adding runtime_state_digest_sha256 to state must not
    change the digest value."""
    state_a = copy.deepcopy(_BASE_STATE)
    digest_without = compute_runtime_state_digest(state_a)

    state_a["runtime_state_digest_sha256"] = "bogus_old_value"
    digest_with = compute_runtime_state_digest(state_a)

    assert digest_without == digest_with


# ── Test 5: EXCLUDE_PATHS completeness ──────────────────────────────


def test_exclude_paths_contains_expected_entries():
    """Sanity check that EXCLUDE_PATHS has the required entries."""
    assert "start_time" in EXCLUDE_PATHS
    assert "end_time" in EXCLUDE_PATHS
    assert "events[*].time" in EXCLUDE_PATHS
    assert "completed_agents[*].time" in EXCLUDE_PATHS
    assert "runtime_state_digest_sha256" in EXCLUDE_PATHS
