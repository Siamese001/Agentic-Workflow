"""ADG-driven tests for agentic_core/L0_routing/scripts/function_tool.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.function_tool  # noqa: F401


def test_module_importable():
    """Module function_tool must be importable."""
    assert agentic_core.L0_routing.scripts.function_tool is not None
