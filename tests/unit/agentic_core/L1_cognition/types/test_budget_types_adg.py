"""Behavioral tests for budget_types_adg."""

from __future__ import annotations

import pytest

from agentic_core.budget_types_adg import BudgetWindow


def test_budget_window_accepts_valid_values():
    assert BudgetWindow(limit=10, remaining=4).validate().remaining == 4


def test_budget_window_rejects_remaining_above_limit():
    with pytest.raises(ValueError):
        BudgetWindow(limit=4, remaining=5).validate()
