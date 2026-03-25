"""ADG-driven tests for agentic_core/mixins/healing_mixin.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.mixins.healing_mixin  # noqa: F401


def test_module_importable():
    """Module healing_mixin must be importable."""
    assert agentic_core.mixins.healing_mixin is not None
