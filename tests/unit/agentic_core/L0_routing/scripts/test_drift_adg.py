"""ADG-driven tests for agentic_core/L0_routing/scripts/drift.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.drift  # noqa: F401


def test_module_importable():
    """Module drift must be importable."""
    assert agentic_core.L0_routing.scripts.drift is not None
