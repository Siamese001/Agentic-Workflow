"""ADG importability contract for system_learning/snapshots/snapshot_factory.py."""
from __future__ import annotations

import system_learning.snapshots.snapshot_factory  # noqa: F401


def test_module_importable():
    """Module snapshot_factory must be importable."""
    assert system_learning.snapshots.snapshot_factory is not None
