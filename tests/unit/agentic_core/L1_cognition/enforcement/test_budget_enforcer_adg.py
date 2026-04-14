"""Smoke tests for the budget enforcer surface."""

from __future__ import annotations

import pytest

from L1_cognition.test_support import assert_module_surface


@pytest.mark.unit
def test_budget_enforcer_surface():
    assert_module_surface(
        "agentic_core.budget_enforcer_adg",
        "BudgetEnforcerAdg",
        "validate_budget_enforcer_adg",
    )
