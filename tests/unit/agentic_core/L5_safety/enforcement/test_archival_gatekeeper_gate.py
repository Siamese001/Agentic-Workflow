"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.enforcement.archival_gatekeeper_gate  # noqa: F401


def test_module_importable():
    """Module archival_gatekeeper_gate must be importable."""
    assert agentic_core.L5_safety.enforcement.archival_gatekeeper_gate is not None
