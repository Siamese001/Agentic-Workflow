"""ADG-driven tests for agentic_core/L5_safety/security/secure_secrets.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.security.secure_secrets  # noqa: F401


def test_module_importable():
    """Module secure_secrets must be importable."""
    assert agentic_core.L5_safety.security.secure_secrets is not None
