"""ADG-driven tests for agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.reasoning.CodeDeduplicationAgent  # noqa: F401


def test_module_importable():
    """Module CodeDeduplicationAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.CodeDeduplicationAgent is not None
