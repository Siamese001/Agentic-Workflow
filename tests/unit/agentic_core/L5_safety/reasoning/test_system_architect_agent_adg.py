"""ADG-driven tests for agentic_core/L5_safety/reasoning/SystemArchitectAgent.py — fan_in=2.

Contract tests: SystemArchitectAgent init, heal(), get_validation_keys(), check methods.
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

_emit_records_execution_trace("p0", "evidence", "test_system_architect_agent_adg")
_emit_applies_guardrail("p0", "test_system_architect_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_system_architect_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_system_architect_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_system_architect_agent_adg")
emit_determinism_digest("p0", "test_system_architect_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_system_architect_agent_adg", "execution_auth")
_emit_validates_capability("p2", "test_system_architect_agent_adg", "capability_check")
_emit_routes_to_capability("p2", "test_system_architect_agent_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_system_architect_agent_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_system_architect_agent_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_system_architect_agent_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_system_architect_agent_adg", "exec_output")
_emit_dispatches_agent("p3", "test_system_architect_agent_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_system_architect_agent_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_system_architect_agent_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_system_architect_agent_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_system_architect_agent_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_system_architect_agent_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_system_architect_agent_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_system_architect_agent_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_system_architect_agent_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_system_architect_agent_adg", "eval_metric")
_emit_stores_embedding("p4", "test_system_architect_agent_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_system_architect_agent_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_system_architect_agent_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.SystemArchitectAgent import SystemArchitectAgent


class TestSystemArchitectAgentInit:
    def test_creates_with_defaults(self):
        agent = SystemArchitectAgent()
        assert agent is not None

    def test_cached_scan_root_starts_none(self):
        agent = SystemArchitectAgent()
        assert agent._cached_scan_root is None

    def test_cached_module_map_starts_none(self):
        agent = SystemArchitectAgent()
        assert agent._cached_module_map is None

    def test_cached_dependency_graph_starts_none(self):
        agent = SystemArchitectAgent()
        assert agent._cached_dependency_graph is None


class TestSystemArchitectAgentHeal:
    def setup_method(self):
        self.agent = SystemArchitectAgent()

    def test_heal_returns_dict(self):
        result = self.agent.heal({"type": "DEPTH", "file": "agentic_core/L5/foo.py"})
        assert isinstance(result, dict)

    def test_heal_status_manual_required(self):
        result = self.agent.heal({"type": "IMPORT_VIOLATION", "file": "foo.py"})
        assert result["status"] == "manual_required"

    def test_heal_has_reason(self):
        result = self.agent.heal({"type": "DEPTH", "file": "foo.py"})
        assert "reason" in result

    def test_heal_has_suggested_action(self):
        result = self.agent.heal({"type": "DEPTH", "file": "foo.py"})
        assert "suggested_action" in result

    def test_heal_missing_file_still_returns_dict(self):
        result = self.agent.heal({"type": "DEPTH"})
        assert isinstance(result, dict)


class TestSystemArchitectAgentValidationKeys:
    def test_get_validation_keys_returns_list(self):
        agent = SystemArchitectAgent()
        keys = agent.get_validation_keys()
        assert isinstance(keys, list)

    def test_validation_keys_range_40_to_50(self):
        agent = SystemArchitectAgent()
        keys = agent.get_validation_keys()
        assert 40 in keys
        assert 50 in keys

    def test_validation_keys_count(self):
        agent = SystemArchitectAgent()
        keys = agent.get_validation_keys()
        assert len(keys) == 11  # 40..50 inclusive


class TestSystemArchitectAgentCheckMethods:
    def setup_method(self):
        self.agent = SystemArchitectAgent(project_root=Path("."))

    def test_check_core_architecture_method_exists(self):
        assert callable(self.agent.check_core_architecture)

    def test_check_no_deep_nesting_method_exists(self):
        assert callable(self.agent.check_no_deep_nesting)

    def test_check_no_large_files_method_exists(self):
        assert callable(self.agent.check_no_large_files)
