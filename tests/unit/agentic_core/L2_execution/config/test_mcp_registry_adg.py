"""ADG-driven tests for L2_execution/config/mcp_registry.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.config.mcp_registry  # noqa: F401


def test_module_importable():
    """Module mcp_registry must be importable."""
    assert agentic_core.L2_execution.config.mcp_registry is not None
