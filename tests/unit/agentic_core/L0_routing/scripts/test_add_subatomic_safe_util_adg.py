"""ADG-driven tests for agentic_core/L0_routing/scripts/add_subatomic_safe_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.add_subatomic_safe_util  # noqa: F401


def test_module_importable():
    """Module add_subatomic_safe_util must be importable."""
    assert agentic_core.L0_routing.scripts.add_subatomic_safe_util is not None
