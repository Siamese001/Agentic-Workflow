"""ADG importability contract for agentic_core/runtime/types/__init__.py."""
from __future__ import annotations

import agentic_core.runtime.types.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module types must be importable."""
    assert _mod is not None
