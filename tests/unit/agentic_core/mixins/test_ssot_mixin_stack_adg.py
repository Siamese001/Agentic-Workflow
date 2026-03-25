"""ADG importability contract for agentic_core/mixins/ssot_mixin_stack.py."""
from __future__ import annotations

import agentic_core.mixins.ssot_mixin_stack  # noqa: F401


def test_module_importable():
    """Module ssot_mixin_stack must be importable."""
    assert agentic_core.mixins.ssot_mixin_stack is not None
