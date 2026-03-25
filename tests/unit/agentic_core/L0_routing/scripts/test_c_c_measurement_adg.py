"""ADG-driven tests for agentic_core/L0_routing/scripts/c_c_measurement.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.c_c_measurement  # noqa: F401


def test_module_importable():
    """Module c_c_measurement must be importable."""
    assert agentic_core.L0_routing.scripts.c_c_measurement is not None
