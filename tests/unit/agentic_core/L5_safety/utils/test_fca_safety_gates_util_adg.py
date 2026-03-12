"""ADG-driven tests for L5_safety/utils/fca_safety_gates_util.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.utils.fca_safety_gates_util import PlannedAction


class TestPlannedAction:
    def test_creates(self):
        action = PlannedAction(
            action_type="DETECT_RENAME",
            src="foo.py",
            dst="bar.py",
            reason_code="NAMING_VIOLATION",
        )
        assert action.action_type == "DETECT_RENAME"
        assert action.src == "foo.py"
        assert action.dst == "bar.py"

    def test_blocked_reason_default_none(self):
        action = PlannedAction(
            action_type="TERRITORY_MOVE",
            src="a.py",
            dst="b.py",
            reason_code="TERRITORY_MISMATCH",
        )
        assert action.blocked_reason is None

    def test_impact_score_default_zero(self):
        action = PlannedAction(
            action_type="FOLDER_PURITY_EVICT",
            src="c.py",
            dst="d.py",
            reason_code="PURITY",
        )
        assert action.impact_score == 0

    def test_is_blocked_when_blocked_reason_set(self):
        action = PlannedAction(
            action_type="DETECT_RENAME",
            src="a.py",
            dst="b.py",
            reason_code="NAMING_VIOLATION",
            blocked_reason="COLLISION",
        )
        assert action.blocked_reason == "COLLISION"
