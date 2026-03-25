"""ADG-driven tests for agentic_core/L0_routing/scripts/verify_territory_counts_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.verify_territory_counts_util  # noqa: F401


def test_module_importable():
    """Module verify_territory_counts_util must be importable."""
    assert agentic_core.L0_routing.scripts.verify_territory_counts_util is not None
