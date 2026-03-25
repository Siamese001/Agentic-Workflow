"""ADG-driven tests for agentic_core/L3_orchestration/engines/action_router.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L3_orchestration.engines.action_router  # noqa: F401


def test_module_importable():
    """Module action_router must be importable."""
    assert agentic_core.L3_orchestration.engines.action_router is not None
