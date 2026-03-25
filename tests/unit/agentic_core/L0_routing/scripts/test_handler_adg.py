"""ADG-driven tests for agentic_core/L0_routing/scripts/handler.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.handler  # noqa: F401


def test_module_importable():
    """Module handler must be importable."""
    assert agentic_core.L0_routing.scripts.handler is not None
