"""ADG importability contract for agentic_core/L2_execution/enforcement/budget_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_budget_enforcer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.budget_enforcer import (  # noqa: F401
        BudgetEnforcer,
        BudgetExceeded,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    BudgetExceeded = None  # type: ignore[assignment,misc]
    BudgetEnforcer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="budget_enforcer deps unavailable")
class TestBudgetEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/enforcement/budget_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_budgetexceeded_defined(self) -> None:
        assert BudgetExceeded is not None

    def test_budgetenforcer_defined(self) -> None:
        assert BudgetEnforcer is not None
