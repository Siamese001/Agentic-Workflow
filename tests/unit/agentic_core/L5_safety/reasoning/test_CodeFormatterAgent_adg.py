"""ADG-driven tests for agentic_core/L5_safety/reasoning/CodeFormatterAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.reasoning.CodeFormatterAgent  # noqa: F401


def test_module_importable():
    """Module CodeFormatterAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.CodeFormatterAgent is not None
