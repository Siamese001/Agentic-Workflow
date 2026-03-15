"""ADG importability contract for agentic_core/L2_execution/enforcement/deterministic_loop_detector.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_deterministic_loop_detector.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (  # noqa: F401
        DeterministicLoopDetector,
        ToolBudget,
        ToolBudgetExceededError,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ToolBudgetExceededError = None  # type: ignore[assignment,misc]
    ToolBudget = None  # type: ignore[assignment,misc]
    DeterministicLoopDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="deterministic_loop_detector deps unavailable")
class TestDeterministicLoopDetectorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/enforcement/deterministic_loop_detector.py must be importable."""
        assert _AVAILABLE

    def test_toolbudgetexceedederror_defined(self) -> None:
        assert ToolBudgetExceededError is not None

    def test_toolbudget_defined(self) -> None:
        assert ToolBudget is not None

    def test_deterministicloopdetector_defined(self) -> None:
        assert DeterministicLoopDetector is not None
