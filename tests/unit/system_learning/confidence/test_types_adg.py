"""ADG importability contract for system_learning/confidence/types.py."""
from __future__ import annotations

import system_learning.confidence.types  # noqa: F401


def test_module_importable():
    """Module types must be importable."""
    assert system_learning.confidence.types is not None
