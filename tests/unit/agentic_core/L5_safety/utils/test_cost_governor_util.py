"""Smoke tests for cost_governor_util — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.cost_governor_util")


def test_module_imports_clean():
    assert mod is not None


def test_BudgetExceededError_present():
    assert hasattr(mod, "BudgetExceededError")
    assert isinstance(mod.BudgetExceededError, type)


def test_track_cost_callable():
    assert callable(mod.track_cost)
