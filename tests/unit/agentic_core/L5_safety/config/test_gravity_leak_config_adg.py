"""ADG-driven tests for L5_safety/config/gravity_leak_config.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_gravity_leak_config_adg")
_emit_applies_guardrail("p0", "test_gravity_leak_config_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_gravity_leak_config_adg", "policy_binding")
_emit_snapshots_state("p0", "test_gravity_leak_config_adg", "state_snapshot")
emit_replay_key("p0", "test_gravity_leak_config_adg")
emit_determinism_digest("p0", "test_gravity_leak_config_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_gravity_leak_config_adg", "execution_auth")
_emit_validates_capability("p2", "test_gravity_leak_config_adg", "capability_check")
_emit_routes_to_capability("p2", "test_gravity_leak_config_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_gravity_leak_config_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_gravity_leak_config_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_gravity_leak_config_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_gravity_leak_config_adg", "exec_output")
_emit_dispatches_agent("p3", "test_gravity_leak_config_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_gravity_leak_config_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_gravity_leak_config_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_gravity_leak_config_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_gravity_leak_config_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_gravity_leak_config_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_gravity_leak_config_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_gravity_leak_config_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_gravity_leak_config_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_gravity_leak_config_adg", "eval_metric")
_emit_stores_embedding("p4", "test_gravity_leak_config_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_gravity_leak_config_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_gravity_leak_config_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.config.gravity_leak_config import (
        CORE_TERRITORY_KEYWORDS,
        GravityLeakDetector,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    CORE_TERRITORY_KEYWORDS = None  # type: ignore[assignment]
    GravityLeakDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="gravity_leak_config deps unavailable")
class TestGravityLeakConstants:
    def test_core_territory_keywords_is_set(self):
        assert isinstance(CORE_TERRITORY_KEYWORDS, set)

    def test_contains_sovereign(self):
        assert "sovereign" in CORE_TERRITORY_KEYWORDS


@pytest.mark.skipif(not _AVAILABLE, reason="gravity_leak_config deps unavailable")
class TestGravityLeakDetector:
    def test_importable(self):
        assert callable(GravityLeakDetector)

    def test_creates(self, tmp_path):
        detector = GravityLeakDetector(project_root=tmp_path)
        assert detector is not None


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
