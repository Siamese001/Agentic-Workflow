"""ADG-driven tests for L0_routing/enforcement/boot_sequence.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.enforcement.boot_sequence  # noqa: F401


def test_module_importable():
    """Module boot_sequence must be importable."""
    assert agentic_core.L0_routing.enforcement.boot_sequence is not None
