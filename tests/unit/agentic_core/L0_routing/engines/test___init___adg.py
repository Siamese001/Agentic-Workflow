"""ADG importability contract for agentic_core/L0_routing/engines/__init__.py."""
from __future__ import annotations

import agentic_core.L0_routing.engines.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module engines must be importable."""
    assert _mod is not None
