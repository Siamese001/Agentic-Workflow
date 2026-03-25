"""ADG-driven tests for agentic_core/L0_routing/utils/scorched_earth_merge_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.utils.scorched_earth_merge_util  # noqa: F401


def test_module_importable():
    """Module scorched_earth_merge_util must be importable."""
    assert agentic_core.L0_routing.utils.scorched_earth_merge_util is not None
