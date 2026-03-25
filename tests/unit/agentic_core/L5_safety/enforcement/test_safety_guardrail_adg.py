"""ADG-driven tests for agentic_core/L5_safety/enforcement/safety_guardrail.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.enforcement.safety_guardrail  # noqa: F401


def test_module_importable():
    """Module safety_guardrail must be importable."""
    assert agentic_core.L5_safety.enforcement.safety_guardrail is not None
