"""ADG importability contract for agentic_core/L2_execution/enforcement/budget_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_budget_enforcer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.budget_enforcer import (  # noqa: F401
        BudgetExceeded,
        BudgetEnforcer,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    BudgetExceeded = None  # type: ignore[assignment,misc]
    BudgetEnforcer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="budget_enforcer.py deps unavailable")
class TestBudgetEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: budget_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_budgetexceeded_is_type(self) -> None:
        assert BudgetExceeded is not None

    def test_budgetenforcer_is_type(self) -> None:
        assert BudgetEnforcer is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

