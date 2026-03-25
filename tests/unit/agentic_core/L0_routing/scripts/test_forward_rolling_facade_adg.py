"""ADG-driven tests for agentic_core/L0_routing/scripts/forward_rolling_facade.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.forward_rolling_facade  # noqa: F401


def test_module_importable():
    """Module forward_rolling_facade must be importable."""
    assert agentic_core.L0_routing.scripts.forward_rolling_facade is not None
