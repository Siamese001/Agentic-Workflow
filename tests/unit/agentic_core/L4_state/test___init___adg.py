"""ADG importability contract for agentic_core/L4_state/__init__.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L4_state.__init__ as _mod  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.__init__ as _mod  # noqa: F401
    """Module L4_state must be importable."""
    assert _mod is not None
