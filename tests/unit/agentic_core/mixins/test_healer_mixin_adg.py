"""ADG importability contract for agentic_core/mixins/healer_mixin.py."""
from __future__ import annotations

import agentic_core.mixins.healer_mixin  # noqa: F401


def test_module_importable():
    """Module healer_mixin must be importable."""
    assert agentic_core.mixins.healer_mixin is not None
