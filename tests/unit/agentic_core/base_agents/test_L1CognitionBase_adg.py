"""ADG-driven tests for agentic_core/base_agents/L1CognitionBase.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.base_agents.L1CognitionBase  # noqa: F401


def test_module_importable():
    """Module L1CognitionBase must be importable."""
    assert agentic_core.base_agents.L1CognitionBase is not None
