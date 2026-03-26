"""ADG importability contract for agentic_core/prompt_governance/core/__init__.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.prompt_governance.core.__init__ as _mod  # noqa: F401


def test_module_importable():
        import agentic_core.prompt_governance.core.__init__ as _mod  # noqa: F401
        """Module core must be importable."""
        assert _mod is not None

    assert _mod is not None
