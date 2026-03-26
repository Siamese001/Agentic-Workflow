"""ADG importability contract for system_learning/types/__init__.py."""
from __future__ import annotations

def test_module_importable():
    """Module types must be importable."""
    import system_learning.types.__init__ as _mod
    assert _mod is not None