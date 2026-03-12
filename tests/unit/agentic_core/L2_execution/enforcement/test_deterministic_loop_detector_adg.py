"""ADG-driven tests for L2_execution/enforcement/deterministic_loop_detector.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
    DeterministicLoopDetector,
    ToolBudget,
    ToolBudgetExceededError,
)


class TestToolBudgetExceededError:
    def test_is_exception(self):
        assert issubclass(ToolBudgetExceededError, Exception)

    def test_creates(self):
        err = ToolBudgetExceededError(tool_name="search", budget=10)
        assert err.tool_name == "search"
        assert err.budget == 10
        assert err.reason_code == "TOOL_BUDGET_EXCEEDED"
        assert "search" in str(err)


class TestToolBudget:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ToolBudget)

    def test_is_frozen(self):
        budget = ToolBudget(max_steps=5)
        with pytest.raises((AttributeError, TypeError)):
            budget.max_steps = 10


class TestDeterministicLoopDetector:
    def test_creates(self):
        detector = DeterministicLoopDetector()
        assert detector is not None

    def test_has_counters(self):
        detector = DeterministicLoopDetector()
        assert hasattr(detector, "_counters")
