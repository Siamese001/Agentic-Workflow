"""ADG-driven tests for agentic_core/L3_orchestration/enforcement/rl_strategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L3_orchestration.enforcement.rl_strategy  # noqa: F401


def test_module_importable():
    """Module rl_strategy must be importable."""
    assert agentic_core.L3_orchestration.enforcement.rl_strategy is not None
