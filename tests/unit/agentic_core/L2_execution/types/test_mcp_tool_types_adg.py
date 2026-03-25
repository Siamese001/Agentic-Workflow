"""ADG contract tests for L2_execution/types/mcp_tool_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.types.mcp_tool_types  # noqa: F401


def test_module_importable():
    """Module mcp_tool_types must be importable."""
    assert agentic_core.L2_execution.types.mcp_tool_types is not None
