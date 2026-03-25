"""ADG importability contract for system_learning/correlation/types.py."""
from __future__ import annotations

import system_learning.correlation.types  # noqa: F401


def test_module_importable():
    """Module types must be importable."""
    assert system_learning.correlation.types is not None
