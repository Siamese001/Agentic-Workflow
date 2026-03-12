"""ADG-driven tests for L1_cognition/enforcement/budget_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.enforcement.budget_enforcer import EnforceBudgetLimits


class TestEnforceBudgetLimits:
    def test_importable(self):
        assert callable(EnforceBudgetLimits)

    def test_creates(self):
        obj = EnforceBudgetLimits()
        assert obj is not None
