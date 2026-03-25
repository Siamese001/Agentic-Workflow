"""ADG importability contract for agentic_core/L2_execution/enforcement/__init__.py."""
from __future__ import annotations

import agentic_core.L2_execution.enforcement.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module enforcement must be importable."""
    assert _mod is not None
