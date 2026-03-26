"""ADG importability contract for system_learning/types/snapshot_types.py."""
from __future__ import annotations



def test_module_importable():
    """Module snapshot_types must be importable."""
    import system_learning.types.snapshot_types  # noqa: F401

    assert system_learning.types.snapshot_types is not None