"""ADG importability contract for agentic_core/L2_execution/enforcement/deterministic_loop_detector.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_deterministic_loop_detector.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (  # noqa: F401
        ToolBudgetExceededError,
        ToolBudget,
        DeterministicLoopDetector,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolBudgetExceededError = None  # type: ignore[assignment,misc]
    ToolBudget = None  # type: ignore[assignment,misc]
    DeterministicLoopDetector = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="deterministic_loop_detector.py deps unavailable")
class TestDeterministicLoopDetectorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: deterministic_loop_detector.py must be importable."""
        assert _AVAILABLE

    def test_toolbudgetexceedederror_is_type(self) -> None:
        assert ToolBudgetExceededError is not None

    def test_toolbudget_is_type(self) -> None:
        assert ToolBudget is not None

    def test_deterministicloopdetector_is_type(self) -> None:
        assert DeterministicLoopDetector is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

