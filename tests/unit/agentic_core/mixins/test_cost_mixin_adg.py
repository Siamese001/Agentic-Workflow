"""ADG importability contract for agentic_core/mixins/cost_mixin.py."""
from __future__ import annotations

import agentic_core.mixins.cost_mixin  # noqa: F401


def test_module_importable():
    """Module cost_mixin must be importable."""
    assert agentic_core.mixins.cost_mixin is not None
