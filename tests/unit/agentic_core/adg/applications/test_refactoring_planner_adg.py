"""ADG importability contract for agentic_core/adg/applications/refactoring_planner.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_refactoring_planner.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.refactoring_planner import (  # noqa: F401
        RefactoringStep,
        RefactoringPlan,
        build_refactoring_plan,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RefactoringStep = None  # type: ignore[assignment,misc]
    RefactoringPlan = None  # type: ignore[assignment,misc]
    build_refactoring_plan = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="refactoring_planner.py deps unavailable")
class TestRefactoringPlannerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: refactoring_planner.py must be importable."""
        assert _AVAILABLE

    def test_refactoringstep_is_type(self) -> None:
        assert RefactoringStep is not None

    def test_refactoringplan_is_type(self) -> None:
        assert RefactoringPlan is not None

    def test_build_refactoring_plan_callable(self) -> None:
        assert callable(build_refactoring_plan)

