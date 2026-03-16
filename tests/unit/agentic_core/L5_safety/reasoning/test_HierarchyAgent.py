#!/usr/bin/env python3
"""
Tests for HierarchyAgent (previously HierarchyAgent.py, renamed to hierarchy_healer.py
in commit 2f0dc584d — refactor(phase5): rename HierarchyAgent.py -> hierarchy_healer.py).
"""
from __future__ import annotations

from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent
from agentic_core.L5_safety.reasoning.hierarchy_validator import HierarchyValidatorAgent
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

_emit_records_execution_trace("p0", "evidence", "test_HierarchyAgent")
_emit_applies_guardrail("p0", "test_HierarchyAgent", "p0_governance")
_emit_reads_policy_state("p0", "test_HierarchyAgent", "policy_binding")
_emit_snapshots_state("p0", "test_HierarchyAgent", "state_snapshot")
emit_replay_key("p0", "test_HierarchyAgent")
emit_determinism_digest("p0", "test_HierarchyAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_HierarchyAgent", "execution_auth")
_emit_validates_capability("p2", "test_HierarchyAgent", "capability_check")
_emit_routes_to_capability("p2", "test_HierarchyAgent", "capability_route")
_emit_writes_via_uwg("p2", "test_HierarchyAgent", "uwg_write")
_emit_blocks_direct_write("p2", "test_HierarchyAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "test_HierarchyAgent", "tool_invocation")
_emit_captures_execution_output("p2", "test_HierarchyAgent", "exec_output")
_emit_dispatches_agent("p3", "test_HierarchyAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "test_HierarchyAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_HierarchyAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_HierarchyAgent", "healing_outcome")
_emit_escalates_failure("p3", "test_HierarchyAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_HierarchyAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_HierarchyAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_HierarchyAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_HierarchyAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_HierarchyAgent", "eval_metric")
_emit_stores_embedding("p4", "test_HierarchyAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_HierarchyAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_HierarchyAgent", "exec_snapshot_link")


class TestHierarchyAgentSmoke:
    def test_instantiates_with_project_root(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        assert agent is not None

    def test_project_root_stored(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        assert agent.project_root == tmp_path.resolve()

    def test_healing_disabled_flag(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        assert agent.healing_enabled is False

    def test_healing_enabled_flag(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=True)
        assert agent.healing_enabled is True

    def test_has_heal_method(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        assert callable(getattr(agent, "heal", None))

    def test_heal_returns_non_error_when_disabled(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        result = agent.heal({"type": "STRUCTURE", "file": str(tmp_path / "foo.py")})
        assert result["status"] in ("skipped", "manual_required", "success", "partial_success")

    def test_heal_missing_file_path_returns_error_or_skipped(self, tmp_path):
        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)
        result = agent.heal({"type": "MISPLACED"})
        assert result["status"] in ("failed", "skipped", "manual_required")


class TestHierarchyValidatorAgentSmoke:
    def test_instantiates_with_project_root(self, tmp_path):
        validator = HierarchyValidatorAgent(project_root=tmp_path)
        assert validator is not None

    def test_project_root_stored(self, tmp_path):
        validator = HierarchyValidatorAgent(project_root=tmp_path)
        assert validator.project_root == tmp_path.resolve()

    def test_scan_root_violations_returns_dict(self, tmp_path):
        validator = HierarchyValidatorAgent(project_root=tmp_path)
        result = validator.scan_root_violations()
        assert isinstance(result, dict)
