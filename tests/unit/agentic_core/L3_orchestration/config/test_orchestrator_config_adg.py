"""ADG-driven tests for L3 orchestrator_config — fan_in=1."""
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
)

_emit_records_execution_trace("p0", "evidence", "test_orchestrator_config_adg")
_emit_applies_guardrail("p0", "test_orchestrator_config_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_orchestrator_config_adg", "policy_binding")
_emit_snapshots_state("p0", "test_orchestrator_config_adg", "state_snapshot")
emit_replay_key("p0", "test_orchestrator_config_adg")
emit_determinism_digest("p0", "test_orchestrator_config_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_orchestrator_config_adg", "execution_auth")
_emit_validates_capability("p2", "test_orchestrator_config_adg", "capability_check")
_emit_routes_to_capability("p2", "test_orchestrator_config_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_orchestrator_config_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_orchestrator_config_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_orchestrator_config_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_orchestrator_config_adg", "exec_output")
_emit_dispatches_agent("p3", "test_orchestrator_config_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_orchestrator_config_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_orchestrator_config_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_orchestrator_config_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_orchestrator_config_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_orchestrator_config_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_orchestrator_config_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_orchestrator_config_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_orchestrator_config_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_orchestrator_config_adg", "eval_metric")
_emit_stores_embedding("p4", "test_orchestrator_config_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_orchestrator_config_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_orchestrator_config_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L3_orchestration.config.orchestrator_config import OrchestratorConfig


class TestOrchestratorConfigDefaults:
    def test_creates_with_defaults(self):
        cfg = OrchestratorConfig()
        assert cfg is not None

    def test_mission_id_default(self):
        cfg = OrchestratorConfig()
        assert cfg.mission_id == "default-mission"

    def test_max_iterations_default_10(self):
        cfg = OrchestratorConfig()
        assert cfg.max_iterations == 10

    def test_max_phases_default_none(self):
        cfg = OrchestratorConfig()
        assert cfg.max_phases is None

    def test_enable_tri_brain_default_false(self):
        cfg = OrchestratorConfig()
        assert cfg.enable_tri_brain is False

    def test_enable_reflection_default_true(self):
        cfg = OrchestratorConfig()
        assert cfg.enable_reflection is True

    def test_retry_on_failure_default_true(self):
        cfg = OrchestratorConfig()
        assert cfg.retry_on_failure is True

    def test_max_retries_default_3(self):
        cfg = OrchestratorConfig()
        assert cfg.max_retries == 3

    def test_parallel_actions_default_false(self):
        cfg = OrchestratorConfig()
        assert cfg.parallel_actions is False

    def test_metadata_default_empty(self):
        cfg = OrchestratorConfig()
        assert cfg.metadata == {}


class TestOrchestratorConfigToDict:
    def test_to_dict_returns_dict(self):
        cfg = OrchestratorConfig()
        d = cfg.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_has_mission_id(self):
        cfg = OrchestratorConfig(mission_id="test-mission")
        d = cfg.to_dict()
        assert d["mission_id"] == "test-mission"

    def test_to_dict_has_max_iterations(self):
        cfg = OrchestratorConfig(max_iterations=5)
        d = cfg.to_dict()
        assert d["max_iterations"] == 5

    def test_custom_values_preserved(self):
        cfg = OrchestratorConfig(
            mission_id="custom",
            enable_tri_brain=True,
            parallel_actions=True,
        )
        assert cfg.enable_tri_brain is True
        assert cfg.parallel_actions is True
