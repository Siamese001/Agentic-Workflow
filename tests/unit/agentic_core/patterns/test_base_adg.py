"""ADG importability contract for agentic_core/patterns/base.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.patterns.base  # noqa: F401


def test_module_importable():
    import agentic_core.patterns.base  # noqa: F401
    """Module base must be importable."""
    assert agentic_core.patterns.base is not None
