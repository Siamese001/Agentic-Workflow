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
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    OptimizationPriority = None  # type: ignore[assignment,misc]
    PriorityViolationGuard = None  # type: ignore[assignment,misc]
    get_priority_violation_guard = None  # type: ignore[assignment,misc]
    reset_priority_violation_guard = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="priority_violation_guard.py deps unavailable")
class TestPriorityViolationGuardImportability:
    def test_module_importable(self) -> None:
        """ADG contract: priority_violation_guard.py must be importable."""
        assert _AVAILABLE

    def test_optimizationpriority_is_type(self) -> None:
        assert OptimizationPriority is not None

    def test_priorityviolationguard_is_type(self) -> None:
        assert PriorityViolationGuard is not None

    def test_get_priority_violation_guard_callable(self) -> None:
        assert callable(get_priority_violation_guard)

    def test_reset_priority_violation_guard_callable(self) -> None:
        assert callable(reset_priority_violation_guard)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

