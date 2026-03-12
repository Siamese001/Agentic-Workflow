"""ADG-driven tests for L1_cognition/enforcement/mission_status.py — fan_in=0."""
from __future__ import annotations

import pytest

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
