"""ADG-driven tests for L0_routing/reasoning/RootCustomsAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.reasoning.RootCustomsAgent  # noqa: F401


def test_module_importable():
    """Module RootCustomsAgent must be importable."""
    assert agentic_core.L0_routing.reasoning.RootCustomsAgent is not None
