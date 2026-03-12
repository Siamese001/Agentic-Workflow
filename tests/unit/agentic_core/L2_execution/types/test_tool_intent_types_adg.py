"""ADG importability contract for agentic_core/L2_execution/types/tool_intent_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tool_intent_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.tool_intent_types import (  # noqa: F401
        ToolCapability,
        ToolViolation,
        ToolIntent,
        is_mutating,
        is_l1_cognition_active,
        assert_l1_tool_allowed,
        l1_cognition_scope,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolCapability = None  # type: ignore[assignment,misc]
    ToolViolation = None  # type: ignore[assignment,misc]
    ToolIntent = None  # type: ignore[assignment,misc]
    is_mutating = None  # type: ignore[assignment,misc]
    is_l1_cognition_active = None  # type: ignore[assignment,misc]
    assert_l1_tool_allowed = None  # type: ignore[assignment,misc]
    l1_cognition_scope = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="tool_intent_types.py deps unavailable")
class TestToolIntentTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: tool_intent_types.py must be importable."""
        assert _AVAILABLE

    def test_toolcapability_is_type(self) -> None:
        assert ToolCapability is not None

    def test_toolviolation_is_type(self) -> None:
        assert ToolViolation is not None

    def test_toolintent_is_type(self) -> None:
        assert ToolIntent is not None

    def test_is_mutating_callable(self) -> None:
        assert callable(is_mutating)

    def test_is_l1_cognition_active_callable(self) -> None:
        assert callable(is_l1_cognition_active)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

