"""ADG importability contract for system_learning/types/snapshot_types.py."""
from __future__ import annotations

import system_learning.types.snapshot_types  # noqa: F401


def test_module_importable():
    """Module snapshot_types must be importable."""
    assert system_learning.types.snapshot_types is not None
