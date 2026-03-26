"""ADG importability contract for agentic_core/mixins/ssot_mixin_stack.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.mixins.ssot_mixin_stack  # noqa: F401


def test_module_importable():
    import agentic_core.mixins.ssot_mixin_stack  # noqa: F401
    """Module ssot_mixin_stack must be importable."""
    assert agentic_core.mixins.ssot_mixin_stack is not None
