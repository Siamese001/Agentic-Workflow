"""ADG-driven tests for L5_safety/enforcement/hierarchy_validator_enforcer.py — fan_in=1."""
from __future__ import annotations

import json

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

_emit_records_execution_trace("p0", "evidence", "test_hierarchy_validator_enforcer_adg")
_emit_applies_guardrail("p0", "test_hierarchy_validator_enforcer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_hierarchy_validator_enforcer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_hierarchy_validator_enforcer_adg", "state_snapshot")
emit_replay_key("p0", "test_hierarchy_validator_enforcer_adg")
emit_determinism_digest("p0", "test_hierarchy_validator_enforcer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hierarchy_validator_enforcer_adg", "execution_auth")
_emit_validates_capability("p2", "test_hierarchy_validator_enforcer_adg", "capability_check")
_emit_routes_to_capability("p2", "test_hierarchy_validator_enforcer_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_hierarchy_validator_enforcer_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_hierarchy_validator_enforcer_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hierarchy_validator_enforcer_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_hierarchy_validator_enforcer_adg", "exec_output")
_emit_dispatches_agent("p3", "test_hierarchy_validator_enforcer_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hierarchy_validator_enforcer_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hierarchy_validator_enforcer_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hierarchy_validator_enforcer_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_hierarchy_validator_enforcer_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hierarchy_validator_enforcer_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hierarchy_validator_enforcer_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hierarchy_validator_enforcer_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hierarchy_validator_enforcer_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hierarchy_validator_enforcer_adg", "eval_metric")
_emit_stores_embedding("p4", "test_hierarchy_validator_enforcer_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hierarchy_validator_enforcer_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hierarchy_validator_enforcer_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.hierarchy_validator_enforcer import HierarchyValidator

_MINIMAL_CONFIG = {
    "version": "1.0",
    "layers": {
        "agentic_core.L0_routing*": 0,
        "agentic_core.L1_cognition*": 1,
        "agentic_core.L5_safety*": 5,
    },
    "forbidden_cross_imports": {},
    "allowed_cross_imports": {},
}


@pytest.fixture
def config_file(tmp_path):
    p = tmp_path / "layer_hierarchy.json"
    p.write_text(json.dumps(_MINIMAL_CONFIG), encoding="utf-8")
    return p


class TestHierarchyValidator:
    def test_creates_from_valid_config(self, config_file):
        v = HierarchyValidator(config_file)
        assert v is not None

    def test_config_hash_is_string(self, config_file):
        v = HierarchyValidator(config_file)
        assert isinstance(v.config_hash, str)
        assert len(v.config_hash) == 64  # sha256 hex

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            HierarchyValidator(tmp_path / "nonexistent.json")

    def test_raises_on_missing_required_fields(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text(json.dumps({"version": "1.0"}), encoding="utf-8")
        with pytest.raises(ValueError, match="missing required fields"):
            HierarchyValidator(p)

    def test_get_layer_level_known_module(self, config_file):
        v = HierarchyValidator(config_file)
        level = v.get_layer_level("agentic_core.L0_routing.utils")
        assert level == 0

    def test_get_layer_level_unknown_module(self, config_file):
        v = HierarchyValidator(config_file)
        level = v.get_layer_level("external_lib.foo")
        assert level == -1

    def test_is_import_allowed_downward(self, config_file):
        v = HierarchyValidator(config_file)
        # L5 (level 5) importing L0 (level 0) is allowed (higher can import lower)
        assert v.is_import_allowed(
            "agentic_core.L5_safety.foo",
            "agentic_core.L0_routing.bar",
        ) is True
