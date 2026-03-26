"""ADG importability contract for agentic_core/prompt_governance/__init__.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.prompt_governance.__init__ as _mod  # noqa: F401


def test_module_importable():
    import agentic_core.prompt_governance.__init__ as _mod  # noqa: F401
    """Module prompt_governance must be importable."""
    assert _mod is not None
