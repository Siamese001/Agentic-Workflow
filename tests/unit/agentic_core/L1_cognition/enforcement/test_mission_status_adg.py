"""ADG-driven tests for L1_cognition/enforcement/mission_status.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_mission_status_adg")
_emit_applies_guardrail("p0", "test_mission_status_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_mission_status_adg", "policy_binding")
_emit_snapshots_state("p0", "test_mission_status_adg", "state_snapshot")
emit_replay_key("p0", "test_mission_status_adg")
emit_determinism_digest("p0", "test_mission_status_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.enforcement.mission_status import (
    MissionPlan,
    MissionStatus,
)


class TestMissionStatus:
    def test_is_enum(self):
        import enum
        assert issubclass(MissionStatus, enum.Enum)

    def test_pending_value(self):
        assert MissionStatus.PENDING.value == "pending"

    def test_completed_value(self):
        assert MissionStatus.COMPLETED.value == "completed"

    def test_failed_value(self):
        assert MissionStatus.FAILED.value == "failed"


class TestMissionPlan:
    def test_creates_with_defaults(self):
        plan = MissionPlan(mission_id="m-001")
        assert plan.mission_id == "m-001"
        assert plan.phases == []
        assert plan.steps == []
        assert plan.status == "pending"

    def test_creates_with_objective(self):
        plan = MissionPlan(mission_id="m-002", objective="build feature")
        assert plan.objective == "build feature"

    def test_has_execute(self):
        assert hasattr(MissionPlan, "execute")
