"""ADG importability contract for agentic_core/prompt_governance/__init__.py."""
from __future__ import annotations

import agentic_core.prompt_governance.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module prompt_governance must be importable."""
    assert _mod is not None
