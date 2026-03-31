"""ADG importability contract for system_learning/snapshots/snapshot_factory.py."""
from __future__ import annotations

def test_module_importable():
    """Module snapshot_factory must be importable."""
    import system_learning.snapshots.snapshot_factory
    assert system_learning.snapshots.snapshot_factory is not None
