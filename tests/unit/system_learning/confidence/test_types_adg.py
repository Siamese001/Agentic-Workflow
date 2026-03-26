"""ADG importability contract for system_learning/confidence/types.py."""
from __future__ import annotations



def test_module_importable():
    """Module types must be importable."""
    import system_learning.confidence.types  # noqa: F401

    assert system_learning.confidence.types is not None
