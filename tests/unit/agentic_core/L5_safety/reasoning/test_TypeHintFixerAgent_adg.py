"""ADG-driven tests for agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.reasoning.TypeHintFixerAgent  # noqa: F401


def test_module_importable():
    """Module TypeHintFixerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.TypeHintFixerAgent is not None
