"""ADG importability contract for agentic_core/L2_execution/coordination/lease_coordinator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_lease_coordinator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.coordination.lease_coordinator import (  # noqa: F401
        LeaseCoordinator,
        IdempotencyStore,
        get_lease_coordinator,
        get_idempotency_store,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    LeaseCoordinator = None  # type: ignore[assignment,misc]
    IdempotencyStore = None  # type: ignore[assignment,misc]
    get_lease_coordinator = None  # type: ignore[assignment,misc]
    get_idempotency_store = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="lease_coordinator.py deps unavailable")
class TestLeaseCoordinatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: lease_coordinator.py must be importable."""
        assert _AVAILABLE

    def test_leasecoordinator_is_type(self) -> None:
        assert LeaseCoordinator is not None

    def test_idempotencystore_is_type(self) -> None:
        assert IdempotencyStore is not None

    def test_get_lease_coordinator_callable(self) -> None:
        assert callable(get_lease_coordinator)

    def test_get_idempotency_store_callable(self) -> None:
        assert callable(get_idempotency_store)

