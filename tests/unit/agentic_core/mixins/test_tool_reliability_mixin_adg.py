"""ADG importability contract for agentic_core/mixins/tool_reliability_mixin.py."""
from __future__ import annotations

import agentic_core.mixins.tool_reliability_mixin  # noqa: F401


def test_module_importable():
    """Module tool_reliability_mixin must be importable."""
    assert agentic_core.mixins.tool_reliability_mixin is not None
