"""ADG-driven tests for agentic_core/L5_safety/enforcement/healing_invocation_audit_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.enforcement.healing_invocation_audit_enforcer  # noqa: F401


def test_module_importable():
    """Module healing_invocation_audit_enforcer must be importable."""
    assert agentic_core.L5_safety.enforcement.healing_invocation_audit_enforcer is not None
