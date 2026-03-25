"""ADG-driven tests for agentic_core/L5_safety/validators/HygieneGuardianAgent.py — fan_in=2."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.validators.HygieneGuardianAgent  # noqa: F401


def test_module_importable():
    """Module HygieneGuardianAgent must be importable."""
    assert agentic_core.L5_safety.validators.HygieneGuardianAgent is not None
