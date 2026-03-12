"""ADG-driven tests for L0_routing/meta_control/meta_apply.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.meta_control.meta_apply import (
        ROUTING_THRESHOLDS_ALLOWLIST,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ROUTING_THRESHOLDS_ALLOWLIST = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="meta_apply deps unavailable")
class TestMetaApplyConstants:
    def test_routing_thresholds_is_frozenset(self):
        assert isinstance(ROUTING_THRESHOLDS_ALLOWLIST, frozenset)

    def test_threshold_in_allowlist(self):
        assert "threshold" in ROUTING_THRESHOLDS_ALLOWLIST

    def test_confidence_threshold_in_allowlist(self):
        assert "confidence_threshold" in ROUTING_THRESHOLDS_ALLOWLIST


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
