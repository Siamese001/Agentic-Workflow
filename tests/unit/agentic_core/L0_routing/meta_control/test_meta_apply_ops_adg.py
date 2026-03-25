"""ADG-driven tests for L0_routing/meta_control/meta_apply_ops.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.meta_control.meta_apply_ops  # noqa: F401


def test_module_importable():
    """Module meta_apply_ops must be importable."""
    assert agentic_core.L0_routing.meta_control.meta_apply_ops is not None
