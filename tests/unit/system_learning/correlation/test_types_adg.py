"""ADG importability contract for system_learning/correlation/types.py."""
from __future__ import annotations

def test_module_importable():
    """Module types must be importable."""
    import system_learning.correlation.types
    assert system_learning.correlation.types is not None
