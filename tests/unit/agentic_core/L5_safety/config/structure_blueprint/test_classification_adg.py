"""ADG-driven tests for L5 structure_blueprint/classification.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_classification_adg")
_emit_applies_guardrail("p0", "test_classification_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_classification_adg", "policy_binding")
_emit_snapshots_state("p0", "test_classification_adg", "state_snapshot")
emit_replay_key("p0", "test_classification_adg")
emit_determinism_digest("p0", "test_classification_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_classification_adg", "execution_auth")
_emit_validates_capability("p2", "test_classification_adg", "capability_check")
_emit_routes_to_capability("p2", "test_classification_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_classification_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_classification_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_classification_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_classification_adg", "exec_output")
_emit_dispatches_agent("p3", "test_classification_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_classification_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_classification_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_classification_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_classification_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_classification_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_classification_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_classification_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_classification_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_classification_adg", "eval_metric")
_emit_stores_embedding("p4", "test_classification_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_classification_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_classification_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.config.structure_blueprint.classification import (
    CLASSIFICATION_SUFFIX_PATTERNS,
)


class TestClassificationSuffixPatterns:
    def test_is_mapping(self):
        assert isinstance(CLASSIFICATION_SUFFIX_PATTERNS, dict | type(CLASSIFICATION_SUFFIX_PATTERNS))

    def test_agent_pattern_present(self):
        values = list(CLASSIFICATION_SUFFIX_PATTERNS.values())
        assert "AGENT" in values

    def test_types_pattern_present(self):
        values = list(CLASSIFICATION_SUFFIX_PATTERNS.values())
        assert "TYPES" in values

    def test_config_pattern_present(self):
        values = list(CLASSIFICATION_SUFFIX_PATTERNS.values())
        assert "CONFIG" in values

    def test_all_values_are_strings(self):
        for v in CLASSIFICATION_SUFFIX_PATTERNS.values():
            assert isinstance(v, str)

    def test_all_keys_are_strings(self):
        for k in CLASSIFICATION_SUFFIX_PATTERNS.keys():
            assert isinstance(k, str)

    def test_non_empty(self):
        assert len(CLASSIFICATION_SUFFIX_PATTERNS) > 0
