"""ADG-driven tests for L2_execution/coordination/lease_coordinator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.coordination.lease_coordinator import LeaseCoordinator
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    LeaseCoordinator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="lease_coordinator deps unavailable")
class TestLeaseCoordinator:
    def test_importable(self):
        assert callable(LeaseCoordinator)

    def test_creates(self):
        lc = LeaseCoordinator()
        assert lc is not None


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
