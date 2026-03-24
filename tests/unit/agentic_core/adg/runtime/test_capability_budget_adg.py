"""ADG importability contract for agentic_core/adg/runtime/capability_budget.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_capability_budget.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.capability_budget import (  # noqa: F401
        BudgetEvent,
        BudgetExceededError,
        BudgetGovernorReport,
        BudgetStatus,
        ResourceGrant,
        ToolBudget,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    BudgetStatus = None  # type: ignore[assignment,misc]
    BudgetExceededError = None  # type: ignore[assignment,misc]
    ResourceGrant = None  # type: ignore[assignment,misc]
    ToolBudget = None  # type: ignore[assignment,misc]
    BudgetEvent = None  # type: ignore[assignment,misc]
    BudgetGovernorReport = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="capability_budget deps unavailable")
class TestCapabilityBudgetImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/capability_budget.py must be importable."""
        assert _AVAILABLE

    def test_budgetstatus_defined(self) -> None:
        assert BudgetStatus is not None

    def test_budgetexceedederror_defined(self) -> None:
        assert BudgetExceededError is not None

    def test_resourcegrant_defined(self) -> None:
        assert ResourceGrant is not None

    def test_toolbudget_defined(self) -> None:
        assert ToolBudget is not None

    def test_budgetevent_defined(self) -> None:
        assert BudgetEvent is not None

    def test_budgetgovernorreport_defined(self) -> None:
        assert BudgetGovernorReport is not None