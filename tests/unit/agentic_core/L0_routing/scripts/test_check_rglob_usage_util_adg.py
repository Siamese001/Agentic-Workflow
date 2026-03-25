"""ADG-driven tests for agentic_core/L0_routing/scripts/check_rglob_usage_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.check_rglob_usage_util  # noqa: F401


def test_module_importable():
    """Module check_rglob_usage_util must be importable."""
    assert agentic_core.L0_routing.scripts.check_rglob_usage_util is not None
