"""ADG-driven tests for agentic_core/L0_routing/scripts/base_tool_script.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.base_tool_script  # noqa: F401


def test_module_importable():
    """Module base_tool_script must be importable."""
    assert agentic_core.L0_routing.scripts.base_tool_script is not None
