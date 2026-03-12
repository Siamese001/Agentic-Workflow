"""ADG-driven tests for L1_cognition/types/budget_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.budget_types import ToolCallBudget


class TestToolCallBudget:
    def test_creates_with_defaults(self):
        budget = ToolCallBudget()
        assert budget._minimum == 0
        assert budget._maximum == 20

    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ToolCallBudget)

    def test_guidance_default_empty(self):
        budget = ToolCallBudget()
        assert budget._guidance == {}
