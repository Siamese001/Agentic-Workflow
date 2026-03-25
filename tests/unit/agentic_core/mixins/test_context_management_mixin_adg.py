"""ADG importability contract for agentic_core/mixins/context_management_mixin.py."""
from __future__ import annotations

import agentic_core.mixins.context_management_mixin  # noqa: F401


def test_module_importable():
    """Module context_management_mixin must be importable."""
    assert agentic_core.mixins.context_management_mixin is not None
