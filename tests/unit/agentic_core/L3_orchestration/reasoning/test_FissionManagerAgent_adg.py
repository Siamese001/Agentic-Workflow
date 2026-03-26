"""ADG-driven tests for agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L3_orchestration.reasoning.FissionManagerAgent  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.reasoning.FissionManagerAgent  # noqa: F401
    """Module FissionManagerAgent must be importable."""
    assert agentic_core.L3_orchestration.reasoning.FissionManagerAgent is not None
