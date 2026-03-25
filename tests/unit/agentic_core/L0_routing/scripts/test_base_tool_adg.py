"""ADG-driven tests for agentic_core/L0_routing/scripts/base_tool.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.base_tool  # noqa: F401


def test_module_importable():
    """Module base_tool must be importable."""
    assert agentic_core.L0_routing.scripts.base_tool is not None
