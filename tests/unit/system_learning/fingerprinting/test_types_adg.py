"""ADG importability contract for system_learning/fingerprinting/types.py."""
from __future__ import annotations



def test_module_importable():
    """Module types must be importable."""
    import system_learning.fingerprinting.types  # noqa: F401

    assert system_learning.fingerprinting.types is not None
