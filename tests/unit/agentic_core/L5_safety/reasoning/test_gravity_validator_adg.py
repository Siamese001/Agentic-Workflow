"""ADG-driven tests for L5_safety/reasoning/gravity_validator.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.reasoning.gravity_validator  # noqa: F401


def test_module_importable():
    """Module gravity_validator must be importable."""
    assert agentic_core.L5_safety.reasoning.gravity_validator is not None
