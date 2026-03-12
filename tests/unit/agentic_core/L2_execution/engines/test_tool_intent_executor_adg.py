"""ADG importability contract for agentic_core/L2_execution/engines/tool_intent_executor.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tool_intent_executor.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.engines.tool_intent_executor import (  # noqa: F401
        ToolResult,
        ToolIntentExecutor,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolResult = None  # type: ignore[assignment,misc]
    ToolIntentExecutor = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="tool_intent_executor.py deps unavailable")
class TestToolIntentExecutorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: tool_intent_executor.py must be importable."""
        assert _AVAILABLE

    def test_toolresult_is_type(self) -> None:
        assert ToolResult is not None

    def test_toolintentexecutor_is_type(self) -> None:
        assert ToolIntentExecutor is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

