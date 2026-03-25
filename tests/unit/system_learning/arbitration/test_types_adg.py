"""ADG importability contract for system_learning/arbitration/types.py."""
from __future__ import annotations

import system_learning.arbitration.types  # noqa: F401


def test_module_importable():
    """Module types must be importable."""
    assert system_learning.arbitration.types is not None
