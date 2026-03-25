"""ADG-driven tests for agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L3_orchestration.reasoning.NervousSystemAgent  # noqa: F401


def test_module_importable():
    """Module NervousSystemAgent must be importable."""
    assert agentic_core.L3_orchestration.reasoning.NervousSystemAgent is not None
