"""ADG-driven tests for agentic_core/L5_safety/enforcement/sealed_interface_check_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.enforcement.sealed_interface_check_enforcer  # noqa: F401


def test_module_importable():
    """Module sealed_interface_check_enforcer must be importable."""
    assert agentic_core.L5_safety.enforcement.sealed_interface_check_enforcer is not None
