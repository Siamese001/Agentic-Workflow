"""ADG-driven tests for agentic_core/L0_routing/scripts/compare_ui_components_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.compare_ui_components_util  # noqa: F401


def test_module_importable():
    """Module compare_ui_components_util must be importable."""
    assert agentic_core.L0_routing.scripts.compare_ui_components_util is not None
