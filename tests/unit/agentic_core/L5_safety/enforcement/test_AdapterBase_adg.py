"""ADG importability contract for agentic_core/L5_safety/enforcement/AdapterBase.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.enforcement.AdapterBase  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.enforcement.AdapterBase  # noqa: F401
    """Module AdapterBase must be importable."""
    assert agentic_core.L5_safety.enforcement.AdapterBase is not None
