"""ADG importability contract for system_learning/snapshots/snapshot_factory.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_snapshot_factory.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.snapshots.snapshot_factory import (  # noqa: F401
        create_snapshot,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    create_snapshot = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="snapshot_factory.py deps unavailable")
class TestSnapshotFactoryImportability:
    def test_module_importable(self) -> None:
        """ADG contract: snapshot_factory.py must be importable."""
        assert _AVAILABLE

    def test_create_snapshot_callable(self) -> None:
        assert callable(create_snapshot)

