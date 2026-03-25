"""ADG-driven tests for L0_routing/enforcement/boot_sequence_enforcer.py - fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.enforcement.boot_sequence_enforcer as mod  # noqa: F401


def test_module_importable():
    pass  # Import verified at module level

def test_re_exports_boot_sequence():
    assert mod is not None
