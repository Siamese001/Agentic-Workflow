"""P4 MCP optimization tests — read_gateway.py (mcp6_* filesystem reads)."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.tools.read_gateway  # noqa: F401


def test_module_importable():
    """Module read_gateway must be importable."""
    assert agentic_core.L2_execution.tools.read_gateway is not None
