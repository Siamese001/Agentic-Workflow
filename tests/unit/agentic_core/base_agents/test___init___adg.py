"""ADG importability contract for agentic_core/base_agents/__init__.py."""
from __future__ import annotations

import agentic_core.base_agents.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module base_agents must be importable."""
    assert _mod is not None
