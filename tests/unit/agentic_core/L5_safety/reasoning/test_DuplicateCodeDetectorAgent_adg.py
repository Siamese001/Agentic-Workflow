"""ADG-driven tests for agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.reasoning.DuplicateCodeDetectorAgent  # noqa: F401


def test_module_importable():
    """Module DuplicateCodeDetectorAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.DuplicateCodeDetectorAgent is not None
