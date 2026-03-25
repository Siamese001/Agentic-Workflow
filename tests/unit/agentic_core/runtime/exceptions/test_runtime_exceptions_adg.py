"""ADG importability contract for agentic_core/runtime/exceptions/runtime_exceptions.py.

Auto-generated stub - covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_runtime_exceptions.py (no _adg suffix).
"""
from __future__ import annotations

from agentic_core.runtime.exceptions.runtime_exceptions import (
    AgentRuntimeError,
    HealExecutionError,
    MaxTurnsExceededError,
    PatternExecutionError,
    ToolExecutionError,
    ToolNotFoundError,
)  # noqa: F401


class TestRuntimeExceptionsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/exceptions/runtime_exceptions.py must be importable."""

        pass  # Import verified at module level

    def test_agentruntimeerror_defined(self) -> None:
        assert AgentRuntimeError is not None

    def test_toolexecutionerror_defined(self) -> None:
        assert ToolExecutionError is not None

    def test_toolnotfounderror_defined(self) -> None:
        assert ToolNotFoundError is not None

    def test_healexecutionerror_defined(self) -> None:
        assert HealExecutionError is not None

    def test_patternexecutionerror_defined(self) -> None:
        assert PatternExecutionError is not None

    def test_maxturnsexceedederror_defined(self) -> None:
        assert MaxTurnsExceededError is not None
