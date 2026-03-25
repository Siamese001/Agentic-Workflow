"""ADG-driven tests for agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.enforcement.sovereign_filesystem_mcp  # noqa: F401


def test_module_importable():
    """Module sovereign_filesystem_mcp must be importable."""
    assert agentic_core.L2_execution.enforcement.sovereign_filesystem_mcp is not None
