"""ADG-driven tests for agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.reasoning.StructuralEngineerAgent  # noqa: F401


def test_module_importable():
    """Module StructuralEngineerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.StructuralEngineerAgent is not None
