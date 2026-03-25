"""ADG importability contract for system_learning/types/__init__.py."""
from __future__ import annotations

import system_learning.types.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module types must be importable."""
    assert _mod is not None
