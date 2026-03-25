"""ADG-driven tests for agentic_core/L5_safety/reasoning/DocumentationAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.reasoning.DocumentationAgent  # noqa: F401


def test_module_importable():
    """Module DocumentationAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.DocumentationAgent is not None
