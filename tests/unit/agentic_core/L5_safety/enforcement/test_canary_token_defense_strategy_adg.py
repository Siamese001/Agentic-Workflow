"""ADG-driven tests for agentic_core/L5_safety/enforcement/canary_token_defense_strategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.enforcement.canary_token_defense_strategy  # noqa: F401


def test_module_importable():
    """Module canary_token_defense_strategy must be importable."""
    assert agentic_core.L5_safety.enforcement.canary_token_defense_strategy is not None
