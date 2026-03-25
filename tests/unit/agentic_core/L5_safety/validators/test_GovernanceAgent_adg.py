"""ADG-driven tests for agentic_core/L5_safety/validators/GovernanceAgent.py — fan_in=2."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.validators.GovernanceAgent  # noqa: F401


def test_module_importable():
    """Module GovernanceAgent must be importable."""
    assert agentic_core.L5_safety.validators.GovernanceAgent is not None
