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
