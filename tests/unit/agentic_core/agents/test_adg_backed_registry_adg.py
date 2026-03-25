"""ADG-driven tests for agentic_core/agents/adg_backed_registry.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.agents.adg_backed_registry  # noqa: F401


def test_module_importable():
    """Module adg_backed_registry must be importable."""
    assert agentic_core.agents.adg_backed_registry is not None
