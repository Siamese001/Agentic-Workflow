"""ADG-driven tests for L5_safety/config/detection_signal_config.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_detection_signal_config_adg")
_emit_applies_guardrail("p0", "test_detection_signal_config_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_detection_signal_config_adg", "policy_binding")
_emit_snapshots_state("p0", "test_detection_signal_config_adg", "state_snapshot")
emit_replay_key("p0", "test_detection_signal_config_adg")
emit_determinism_digest("p0", "test_detection_signal_config_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_detection_signal_config_adg", "execution_auth")
_emit_validates_capability("p2", "test_detection_signal_config_adg", "capability_check")
_emit_routes_to_capability("p2", "test_detection_signal_config_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_detection_signal_config_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_detection_signal_config_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_detection_signal_config_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_detection_signal_config_adg", "exec_output")
_emit_dispatches_agent("p3", "test_detection_signal_config_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_detection_signal_config_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_detection_signal_config_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_detection_signal_config_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_detection_signal_config_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_detection_signal_config_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_detection_signal_config_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_detection_signal_config_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_detection_signal_config_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_detection_signal_config_adg", "eval_metric")
_emit_stores_embedding("p4", "test_detection_signal_config_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_detection_signal_config_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_detection_signal_config_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.config.detection_signal_config import (
    ImpactAssessment,
    ImpactScope,
    Severity,
)


class TestSeverity:
    def test_critical_highest(self):
        assert Severity.CRITICAL.value > Severity.HIGH.value

    def test_info_lowest(self):
        assert Severity.INFO.value == 0

    def test_has_all_levels(self):
        for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
            assert hasattr(Severity, level)


class TestImpactScope:
    def test_system_wide_value(self):
        assert ImpactScope.SYSTEM_WIDE.value == "system_wide"

    def test_file_value(self):
        assert ImpactScope.FILE.value == "file"

    def test_has_all_scopes(self):
        for scope in ("SYSTEM_WIDE", "DOMAIN", "COMPONENT", "FILE", "ISOLATED"):
            assert hasattr(ImpactScope, scope)


class TestImpactAssessment:
    def test_importable(self):
        assert callable(ImpactAssessment)

    def test_creates_with_defaults(self):
        ia = ImpactAssessment()
        assert ia.scope == ImpactScope.FILE

    def test_creates_with_scope(self):
        ia = ImpactAssessment(scope=ImpactScope.COMPONENT)
        assert ia.scope == ImpactScope.COMPONENT

    def test_blast_radius_default_zero(self):
        ia = ImpactAssessment()
        assert ia.estimated_blast_radius == 0

    def test_recovery_complexity_default(self):
        ia = ImpactAssessment()
        assert ia.recovery_complexity == "low"

    def test_to_dict_returns_dict(self):
        ia = ImpactAssessment(scope=ImpactScope.DOMAIN)
        d = ia.to_dict()
        assert isinstance(d, dict)
        assert d["scope"] == "domain"
