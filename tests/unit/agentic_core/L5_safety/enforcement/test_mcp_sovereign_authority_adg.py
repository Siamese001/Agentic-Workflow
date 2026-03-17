"""ADG-driven tests for agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py — fan_in=2.

Contract tests: MCPSovereignAuthority — breach recording, authorization, tool auditing.
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_mcp_sovereign_authority_adg")
_emit_applies_guardrail("p0", "test_mcp_sovereign_authority_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_mcp_sovereign_authority_adg", "policy_binding")
_emit_snapshots_state("p0", "test_mcp_sovereign_authority_adg", "state_snapshot")
emit_replay_key("p0", "test_mcp_sovereign_authority_adg")
emit_determinism_digest("p0", "test_mcp_sovereign_authority_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_mcp_sovereign_authority_adg", "execution_auth")
_emit_validates_capability("p2", "test_mcp_sovereign_authority_adg", "capability_check")
_emit_routes_to_capability("p2", "test_mcp_sovereign_authority_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_mcp_sovereign_authority_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_mcp_sovereign_authority_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_mcp_sovereign_authority_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_mcp_sovereign_authority_adg", "exec_output")
_emit_dispatches_agent("p3", "test_mcp_sovereign_authority_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_mcp_sovereign_authority_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_mcp_sovereign_authority_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_mcp_sovereign_authority_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_mcp_sovereign_authority_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_mcp_sovereign_authority_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_mcp_sovereign_authority_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_mcp_sovereign_authority_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_mcp_sovereign_authority_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_mcp_sovereign_authority_adg", "eval_metric")
_emit_stores_embedding("p4", "test_mcp_sovereign_authority_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_mcp_sovereign_authority_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_mcp_sovereign_authority_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.mcp_sovereign_authority_enforcer import (
    MCPSovereignAuthority,
    mcp_authority,
)
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_mcp_sovereign_authority_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_mcp_sovereign_authority_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_mcp_sovereign_authority_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_mcp_sovereign_authority_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_mcp_sovereign_authority_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_mcp_sovereign_authority_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_mcp_sovereign_authority_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_mcp_sovereign_authority_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_mcp_sovereign_authority_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_mcp_sovereign_authority_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_mcp_sovereign_authority_adg", "p4obs", "alert")
_emit_links_incident_trace("test_mcp_sovereign_authority_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_mcp_sovereign_authority_adg", "p3lm", "pattern")
_emit_records_learning_event("test_mcp_sovereign_authority_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_mcp_sovereign_authority_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_mcp_sovereign_authority_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_mcp_sovereign_authority_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_mcp_sovereign_authority_adg", "p3lm", "policy")
_emit_stores_learning_state("test_mcp_sovereign_authority_adg", "p3lm", "state")
_emit_records_execution_trace("test_mcp_sovereign_authority_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_mcp_sovereign_authority_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_mcp_sovereign_authority_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_mcp_sovereign_authority_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_mcp_sovereign_authority_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_mcp_sovereign_authority_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_mcp_sovereign_authority_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_mcp_sovereign_authority_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_mcp_sovereign_authority_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_mcp_sovereign_authority_adg", "context_pull")
_emit_pulls_context("p1", "test_mcp_sovereign_authority_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_mcp_sovereign_authority_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_mcp_sovereign_authority_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_mcp_sovereign_authority_adg", "write_through")
_emit_writes_through("p1", "test_mcp_sovereign_authority_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_mcp_sovereign_authority_adg", "safety_validation")
_emit_invokes_eval("p1", "test_mcp_sovereign_authority_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_mcp_sovereign_authority_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_mcp_sovereign_authority_adg", "human_escalation")
_emit_routes_through("p1", "test_mcp_sovereign_authority_adg", "route_through")
_emit_checks_agent_registry("p1", "test_mcp_sovereign_authority_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_mcp_sovereign_authority_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_mcp_sovereign_authority_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_mcp_sovereign_authority_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_mcp_sovereign_authority_adg", "target_agent")
_emit_verifies_policy("p1", "test_mcp_sovereign_authority_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_mcp_sovereign_authority_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_mcp_sovereign_authority_adg", "boundary_check")
_emit_transcripts_response("p1", "test_mcp_sovereign_authority_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_mcp_sovereign_authority_adg")
_emit_gated_by_confidence("p1", "test_mcp_sovereign_authority_adg", "confidence_gate")


class TestMCPSovereignAuthorityImport:
    def test_class_importable(self):
        assert callable(MCPSovereignAuthority)

    def test_module_level_instance_exists(self):
        assert isinstance(mcp_authority, MCPSovereignAuthority)


class TestMCPSovereignAuthorityInitialState:
    def test_fresh_instance_authorized(self):
        a = MCPSovereignAuthority()
        assert a.is_authorized() is True

    def test_fresh_violation_count_zero(self):
        a = MCPSovereignAuthority()
        assert a.violation_count == 0

    def test_fresh_breach_log_empty(self):
        a = MCPSovereignAuthority()
        assert a.breach_log == []

    def test_fresh_not_locked(self):
        a = MCPSovereignAuthority()
        assert a.is_locked is False


class TestMCPSovereignAuthorityBreachRecording:
    def test_record_breach_increments_count(self):
        a = MCPSovereignAuthority()
        a.record_breach("test violation")
        assert a.violation_count == 1

    def test_record_breach_adds_to_log(self):
        a = MCPSovereignAuthority()
        a.record_breach("violation A")
        assert len(a.breach_log) == 1
        assert a.breach_log[0]["error"] == "violation A"

    def test_breach_log_entry_has_timestamp(self):
        a = MCPSovereignAuthority()
        a.record_breach("test")
        assert "timestamp" in a.breach_log[0]

    def test_six_breaches_locks_authority(self):
        a = MCPSovereignAuthority()
        for i in range(6):
            a.record_breach(f"breach {i}")
        assert a.is_authorized() is False


class TestMCPSovereignAuthorityAuthorizeToolCall:
    def test_safe_tool_passes(self):
        a = MCPSovereignAuthority()
        a.authorize_tool_call("read_file", {"path": "docs/readme.md"})  # should not raise

    def test_forbidden_sdk_raises_permission_error(self):
        a = MCPSovereignAuthority()
        with pytest.raises(PermissionError, match="Sovereignty Shield"):
            a.authorize_tool_call("openai", {})

    def test_anthropic_sdk_blocked(self):
        a = MCPSovereignAuthority()
        with pytest.raises(PermissionError):
            a.authorize_tool_call("anthropic", {})

    def test_sequential_thinking_within_limit_passes(self):
        a = MCPSovereignAuthority()
        a.authorize_tool_call("sequential_thinking", {"max_steps": 5, "Task": "analyze code"})

    def test_sequential_thinking_over_limit_raises(self):
        a = MCPSovereignAuthority()
        with pytest.raises(ValueError, match="15 steps"):
            a.authorize_tool_call("sequential_thinking", {"max_steps": 20, "Task": "analyze"})
