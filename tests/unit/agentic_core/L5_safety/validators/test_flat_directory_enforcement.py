"""
Tests for FLAT_DIRECTORIES enforcement.

Validates that validate_flat_directory() correctly rejects files nested
inside directories that must be flat (no subfolders).

[CREATED 2026-02-08] RCA: mixins/contracts/ was not caught because no
validator enforced the "flat" flag in SOVEREIGN_TERRITORIES.
"""

from __future__ import annotations

from agentic_core.L5_safety.config.structure_blueprint import (
    AGENTIC_CORE_DIR,
    FLAT_DIRECTORIES,
    validate_flat_directory,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_flat_directory_enforcement", "p4obs", "metric_1")
_emit_emits_metric_event("test_flat_directory_enforcement", "p4obs", "metric_2")
_emit_emits_metric_event("test_flat_directory_enforcement", "p4obs", "metric_3")
_emit_emits_metric_event("test_flat_directory_enforcement", "p4obs", "metric_4")
_emit_emits_metric_event("test_flat_directory_enforcement", "p4obs", "metric_5")
_emit_emits_metric_event("test_flat_directory_enforcement", "p4obs", "metric_6")
_emit_records_incident_event("test_flat_directory_enforcement", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_flat_directory_enforcement", "p4obs", "anomaly")
_emit_writes_observability_log("test_flat_directory_enforcement", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_flat_directory_enforcement", "p4obs", "mon_state")
_emit_triggers_alert("test_flat_directory_enforcement", "p4obs", "alert")
_emit_links_incident_trace("test_flat_directory_enforcement", "p4obs", "trace_link")
_emit_captures_pattern("test_flat_directory_enforcement", "p3lm", "pattern")
_emit_records_learning_event("test_flat_directory_enforcement", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_flat_directory_enforcement", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_flat_directory_enforcement", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_flat_directory_enforcement", "p3lm", "routing")
_emit_improves_agent_policy("test_flat_directory_enforcement", "p3lm", "policy")
_emit_stores_learning_state("test_flat_directory_enforcement", "p3lm", "state")
_emit_records_execution_trace("test_flat_directory_enforcement", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_flat_directory_enforcement", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_flat_directory_enforcement", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_flat_directory_enforcement", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_flat_directory_enforcement", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_flat_directory_enforcement", "env_read", "p2_env_1")
_emit_reads_environ("test_flat_directory_enforcement", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_flat_directory_enforcement", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_flat_directory_enforcement", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_flat_directory_enforcement")
_emit_applies_guardrail("p0", "test_flat_directory_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_flat_directory_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_flat_directory_enforcement", "state_snapshot")
_emit_pulls_context("p1", "test_flat_directory_enforcement", "context_pull")
_emit_pulls_context("p1", "test_flat_directory_enforcement", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_flat_directory_enforcement", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_flat_directory_enforcement", "uwg_term_secondary")
_emit_writes_through("p1", "test_flat_directory_enforcement", "write_through")
_emit_writes_through("p1", "test_flat_directory_enforcement", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_flat_directory_enforcement", "safety_validation")
_emit_invokes_eval("p1", "test_flat_directory_enforcement", "eval_call")
_emit_proposal_commits_routing("p1", "test_flat_directory_enforcement", "routing_commit")
_emit_escalates_to_human("p1", "test_flat_directory_enforcement", "human_escalation")
_emit_routes_through("p1", "test_flat_directory_enforcement", "route_through")
_emit_checks_agent_registry("p1", "test_flat_directory_enforcement", "agent_registry")
_emit_validates_agent_capability("p1", "test_flat_directory_enforcement", "capability")
_emit_dispatches_execution_plan("p1", "test_flat_directory_enforcement", "exec_plan")
_emit_agent_executes_agent("p1", "test_flat_directory_enforcement", "sub_agent")
_emit_routes_to_agent("p1", "test_flat_directory_enforcement", "target_agent")
_emit_verifies_policy("p1", "test_flat_directory_enforcement", "policy_check")
_emit_observes_runtime_state("p1", "test_flat_directory_enforcement", "runtime_state")
_emit_verifies_boundary("p1", "test_flat_directory_enforcement", "boundary_check")
_emit_transcripts_response("p1", "test_flat_directory_enforcement", "transcript")
_emit_hard_fails_untranscripted("p1", "test_flat_directory_enforcement")
_emit_gated_by_confidence("p1", "test_flat_directory_enforcement", "confidence_gate")
emit_replay_key("p0", "test_flat_directory_enforcement")
emit_determinism_digest("p0", "test_flat_directory_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_flat_directory_enforcement", "execution_auth")
_emit_validates_capability("p2", "test_flat_directory_enforcement", "capability_check")
_emit_routes_to_capability("p2", "test_flat_directory_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "test_flat_directory_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "test_flat_directory_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "test_flat_directory_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "test_flat_directory_enforcement", "exec_output")
_emit_dispatches_agent("p3", "test_flat_directory_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "test_flat_directory_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_flat_directory_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_flat_directory_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "test_flat_directory_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_flat_directory_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_flat_directory_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_flat_directory_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_flat_directory_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_flat_directory_enforcement", "eval_metric")
_emit_stores_embedding("p4", "test_flat_directory_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_flat_directory_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_flat_directory_enforcement", "exec_snapshot_link")


class TestFlatDirectories:
    """FLAT_DIRECTORIES constant is correctly defined."""

    def test_mixins_is_flat(self):
        assert "mixins" in FLAT_DIRECTORIES

    def test_base_agents_is_flat(self):
        assert "base_agents" in FLAT_DIRECTORIES

    def test_interfaces_is_flat(self):
        assert "interfaces" in FLAT_DIRECTORIES


class TestValidateFlatDirectory:
    """validate_flat_directory() catches nested files in flat directories."""

    def test_file_directly_in_mixins_is_ok(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "meta_learning_mixin.py")
        assert validate_flat_directory(parts) is None

    def test_file_in_mixins_subfolder_is_violation(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "contracts", "meta_learning_contract.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["domain"] == "mixins"
        assert result["illegal_child"] == "contracts"
        assert "FLAT VIOLATION" in result["message"]

    def test_file_directly_in_base_agents_is_ok(self):
        parts = (AGENTIC_CORE_DIR, "base_agents", "SovereignBaseAgent.py")
        assert validate_flat_directory(parts) is None

    def test_file_in_base_agents_subfolder_is_violation(self):
        parts = (AGENTIC_CORE_DIR, "base_agents", "legacy", "OldBase.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["domain"] == "base_agents"
        assert result["illegal_child"] == "legacy"

    def test_file_directly_in_interfaces_is_ok(self):
        parts = (AGENTIC_CORE_DIR, "interfaces", "IOrchestratorProtocol.py")
        assert validate_flat_directory(parts) is None

    def test_file_in_interfaces_subfolder_is_violation(self):
        parts = (AGENTIC_CORE_DIR, "interfaces", "v2", "INewProtocol.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["domain"] == "interfaces"

    def test_pycache_in_flat_dir_is_allowed(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "__pycache__", "foo.cpython-312.pyc")
        assert validate_flat_directory(parts) is None

    def test_non_flat_directory_is_not_checked(self):
        parts = (AGENTIC_CORE_DIR, "L5_safety", "reasoning", "sub", "file.py")
        assert validate_flat_directory(parts) is None

    def test_deeply_nested_flat_violation(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "a", "b", "file.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["illegal_child"] == "a"
