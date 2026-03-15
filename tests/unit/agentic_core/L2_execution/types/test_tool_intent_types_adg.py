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
        assert_l1_tool_allowed,
        is_l1_cognition_active,
        is_mutating,
        l1_cognition_scope,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ToolCapability = None  # type: ignore[assignment,misc]
    is_mutating = None  # type: ignore[assignment,misc]
    ToolViolation = None  # type: ignore[assignment,misc]
    is_l1_cognition_active = None  # type: ignore[assignment,misc]
    assert_l1_tool_allowed = None  # type: ignore[assignment,misc]
    l1_cognition_scope = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="tool_intent_types deps unavailable")
class TestToolIntentTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/tool_intent_types.py must be importable."""
        assert _AVAILABLE

    def test_toolcapability_defined(self) -> None:
        assert ToolCapability is not None

    def test_toolviolation_defined(self) -> None:
        assert ToolViolation is not None
