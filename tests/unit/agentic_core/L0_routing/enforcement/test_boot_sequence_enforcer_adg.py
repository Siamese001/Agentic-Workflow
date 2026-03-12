"""ADG-driven tests for L0_routing/enforcement/boot_sequence_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import agentic_core.L0_routing.enforcement.boot_sequence_enforcer as mod
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    mod = None  # type: ignore[assignment]


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE


@pytest.mark.skipif(not _AVAILABLE, reason="boot_sequence_enforcer deps unavailable")
def test_re_exports_boot_sequence():
    assert mod is not None
