"""ADG-driven tests for agentic_core/L2_execution/tools/figma_mcp_client.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.tools.figma_mcp_client  # noqa: F401


def test_module_importable():
    """Module figma_mcp_client must be importable."""
    assert agentic_core.L2_execution.tools.figma_mcp_client is not None
