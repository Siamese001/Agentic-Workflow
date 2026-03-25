"""ADG-driven tests for agentic_core/L0_routing/scripts/collision_resolver.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.collision_resolver  # noqa: F401


def test_module_importable():
    """Module collision_resolver must be importable."""
    assert agentic_core.L0_routing.scripts.collision_resolver is not None
