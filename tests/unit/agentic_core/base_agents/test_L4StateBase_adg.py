"""ADG-driven tests for agentic_core/base_agents/L4StateBase.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.base_agents.L4StateBase  # noqa: F401


def test_module_importable():
    """Module L4StateBase must be importable."""
    assert agentic_core.base_agents.L4StateBase is not None
