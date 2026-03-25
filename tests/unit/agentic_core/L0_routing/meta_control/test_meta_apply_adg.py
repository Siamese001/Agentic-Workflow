"""ADG-driven tests for L0_routing/meta_control/meta_apply.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.meta_control.meta_apply  # noqa: F401


def test_module_importable():
    """Module meta_apply must be importable."""
    assert agentic_core.L0_routing.meta_control.meta_apply is not None
