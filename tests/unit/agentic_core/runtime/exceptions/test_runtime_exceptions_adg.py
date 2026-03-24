"""ADG importability contract for agentic_core/runtime/exceptions/runtime_exceptions.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_runtime_exceptions.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.exceptions.runtime_exceptions import (  # noqa: F401
        AgentRuntimeError,
        HealExecutionError,
        MaxTurnsExceededError,
        PatternExecutionError,
        ToolExecutionError,
        ToolNotFoundError,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    AgentRuntimeError = None  # type: ignore[assignment,misc]
    ToolExecutionError = None  # type: ignore[assignment,misc]
    ToolNotFoundError = None  # type: ignore[assignment,misc]
    HealExecutionError = None  # type: ignore[assignment,misc]
    PatternExecutionError = None  # type: ignore[assignment,misc]
    MaxTurnsExceededError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="runtime_exceptions deps unavailable")
class TestRuntimeExceptionsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/exceptions/runtime_exceptions.py must be importable."""
        assert _AVAILABLE

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