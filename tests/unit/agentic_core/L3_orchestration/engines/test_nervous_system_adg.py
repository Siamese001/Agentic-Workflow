"""ADG-driven tests for agentic_core/L3_orchestration/engines/nervous_system.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L3_orchestration.engines.nervous_system  # noqa: F401


def test_module_importable():
    """Module nervous_system must be importable."""
    assert agentic_core.L3_orchestration.engines.nervous_system is not None
