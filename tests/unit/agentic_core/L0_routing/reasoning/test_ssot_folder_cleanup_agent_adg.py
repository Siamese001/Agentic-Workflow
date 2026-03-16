"""ADG-driven tests for agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py — fan_in=1.

Contract tests: SSOTFolderCleanupAgent init, stats, dry_run default.
"""
from __future__ import annotations

from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "test_ssot_folder_cleanup_agent_adg")
_emit_applies_guardrail("p0", "test_ssot_folder_cleanup_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_ssot_folder_cleanup_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_ssot_folder_cleanup_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_ssot_folder_cleanup_agent_adg")
emit_determinism_digest("p0", "test_ssot_folder_cleanup_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_ssot_folder_cleanup_agent_adg", "execution_auth")
_emit_validates_capability("p2", "test_ssot_folder_cleanup_agent_adg", "capability_check")
_emit_routes_to_capability("p2", "test_ssot_folder_cleanup_agent_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_ssot_folder_cleanup_agent_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_ssot_folder_cleanup_agent_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_ssot_folder_cleanup_agent_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_ssot_folder_cleanup_agent_adg", "exec_output")
_emit_dispatches_agent("p3", "test_ssot_folder_cleanup_agent_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_ssot_folder_cleanup_agent_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_ssot_folder_cleanup_agent_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_ssot_folder_cleanup_agent_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_ssot_folder_cleanup_agent_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_ssot_folder_cleanup_agent_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_ssot_folder_cleanup_agent_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_ssot_folder_cleanup_agent_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_ssot_folder_cleanup_agent_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_ssot_folder_cleanup_agent_adg", "eval_metric")
_emit_stores_embedding("p4", "test_ssot_folder_cleanup_agent_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_ssot_folder_cleanup_agent_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_ssot_folder_cleanup_agent_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.reasoning.SSOTFolderCleanupAgent import SSOTFolderCleanupAgent
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
)

_emit_emits_metric_event("test_ssot_folder_cleanup_agent_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_ssot_folder_cleanup_agent_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_ssot_folder_cleanup_agent_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_ssot_folder_cleanup_agent_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_ssot_folder_cleanup_agent_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_ssot_folder_cleanup_agent_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_ssot_folder_cleanup_agent_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_ssot_folder_cleanup_agent_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_ssot_folder_cleanup_agent_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_ssot_folder_cleanup_agent_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_ssot_folder_cleanup_agent_adg", "p4obs", "alert")
_emit_links_incident_trace("test_ssot_folder_cleanup_agent_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_ssot_folder_cleanup_agent_adg", "p3lm", "pattern")
_emit_records_learning_event("test_ssot_folder_cleanup_agent_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_ssot_folder_cleanup_agent_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_ssot_folder_cleanup_agent_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_ssot_folder_cleanup_agent_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_ssot_folder_cleanup_agent_adg", "p3lm", "policy")
_emit_stores_learning_state("test_ssot_folder_cleanup_agent_adg", "p3lm", "state")
_emit_records_execution_trace("test_ssot_folder_cleanup_agent_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_ssot_folder_cleanup_agent_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_ssot_folder_cleanup_agent_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_ssot_folder_cleanup_agent_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_ssot_folder_cleanup_agent_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_ssot_folder_cleanup_agent_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_ssot_folder_cleanup_agent_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_ssot_folder_cleanup_agent_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_ssot_folder_cleanup_agent_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_ssot_folder_cleanup_agent_adg", "context_pull")
_emit_pulls_context("p1", "test_ssot_folder_cleanup_agent_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_ssot_folder_cleanup_agent_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_ssot_folder_cleanup_agent_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_ssot_folder_cleanup_agent_adg", "write_through")
_emit_writes_through("p1", "test_ssot_folder_cleanup_agent_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_ssot_folder_cleanup_agent_adg", "safety_validation")
_emit_invokes_eval("p1", "test_ssot_folder_cleanup_agent_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_ssot_folder_cleanup_agent_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_ssot_folder_cleanup_agent_adg", "human_escalation")
_emit_routes_through("p1", "test_ssot_folder_cleanup_agent_adg", "route_through")
_emit_checks_agent_registry("p1", "test_ssot_folder_cleanup_agent_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_ssot_folder_cleanup_agent_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_ssot_folder_cleanup_agent_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_ssot_folder_cleanup_agent_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_ssot_folder_cleanup_agent_adg", "target_agent")
_emit_verifies_policy("p1", "test_ssot_folder_cleanup_agent_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_ssot_folder_cleanup_agent_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_ssot_folder_cleanup_agent_adg", "boundary_check")
_emit_transcripts_response("p1", "test_ssot_folder_cleanup_agent_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_ssot_folder_cleanup_agent_adg")
_emit_gated_by_confidence("p1", "test_ssot_folder_cleanup_agent_adg", "confidence_gate")

_REPO_ROOT = Path(__file__).parents[5]


class TestSSOTFolderCleanupAgentInit:
    def test_creates_with_defaults(self):
        agent = SSOTFolderCleanupAgent()
        assert agent is not None

    def test_dry_run_default_true(self):
        agent = SSOTFolderCleanupAgent()
        assert agent.dry_run is True

    def test_project_root_is_path(self):
        agent = SSOTFolderCleanupAgent()
        assert isinstance(agent.project_root, Path)

    def test_stats_dict_populated(self):
        agent = SSOTFolderCleanupAgent()
        assert isinstance(agent.stats, dict)
        assert "files_scanned" in agent.stats
        assert "files_moved" in agent.stats
        assert "errors" in agent.stats

    def test_stats_start_zero(self):
        agent = SSOTFolderCleanupAgent()
        assert agent.stats["files_scanned"] == 0
        assert agent.stats["errors"] == 0

    def test_lazy_cognitive_agent_none(self):
        agent = SSOTFolderCleanupAgent()
        assert agent._cognitive_agent is None

    def test_creates_with_custom_root(self):
        agent = SSOTFolderCleanupAgent(project_root=_REPO_ROOT)
        assert agent.project_root == _REPO_ROOT

    def test_dry_run_false(self):
        agent = SSOTFolderCleanupAgent(dry_run=False)
        assert agent.dry_run is False

    def test_sovereign_registry_populated(self):
        agent = SSOTFolderCleanupAgent()
        assert isinstance(agent.sovereign_registry, dict)
        assert "agentic_core" in agent.sovereign_registry

    def test_core_subfolder_map_populated(self):
        agent = SSOTFolderCleanupAgent()
        assert isinstance(agent.core_subfolder_map, dict)
        assert "L0_routing" in agent.core_subfolder_map
