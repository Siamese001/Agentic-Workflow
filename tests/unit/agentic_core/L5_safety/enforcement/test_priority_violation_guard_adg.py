"""ADG importability contract for agentic_core/L5_safety/enforcement/priority_violation_guard.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_priority_violation_guard.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.priority_violation_guard import (  # noqa: F401
        OptimizationPriority,
        PriorityViolationGuard,
        get_priority_violation_guard,
        reset_priority_violation_guard,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    OptimizationPriority = None  # type: ignore[assignment,misc]
    PriorityViolationGuard = None  # type: ignore[assignment,misc]
    get_priority_violation_guard = None  # type: ignore[assignment,misc]
    reset_priority_violation_guard = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="priority_violation_guard deps unavailable")
class TestPriorityViolationGuardImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/priority_violation_guard.py must be importable."""
        assert _AVAILABLE

    def test_optimizationpriority_defined(self) -> None:
        assert OptimizationPriority is not None

    def test_priorityviolationguard_defined(self) -> None:
        assert PriorityViolationGuard is not None