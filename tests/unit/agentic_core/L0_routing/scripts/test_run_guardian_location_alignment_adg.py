"""ADG-driven tests for agentic_core/L0_routing/scripts/run_guardian_location_alignment.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.run_guardian_location_alignment  # noqa: F401


def test_module_importable():
    """Module run_guardian_location_alignment must be importable."""
    assert agentic_core.L0_routing.scripts.run_guardian_location_alignment is not None
