"""ADG importability contract for system_learning/arbitration/types.py."""
from __future__ import annotations



def test_module_importable():
    """Module types must be importable."""
    import system_learning.arbitration.types  # noqa: F401

    assert system_learning.arbitration.types is not None
