"""ADG importability contract for agentic_core/mixins/ssot_rate_limit_mixin.py."""
from __future__ import annotations

import agentic_core.mixins.ssot_rate_limit_mixin  # noqa: F401


def test_module_importable():
    """Module ssot_rate_limit_mixin must be importable."""
    assert agentic_core.mixins.ssot_rate_limit_mixin is not None
