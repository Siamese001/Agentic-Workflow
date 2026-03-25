"""ADG-driven tests for agentic_core/L0_routing/scripts/core_synthesis_executor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.core_synthesis_executor  # noqa: F401


def test_module_importable():
    """Module core_synthesis_executor must be importable."""
    assert agentic_core.L0_routing.scripts.core_synthesis_executor is not None
