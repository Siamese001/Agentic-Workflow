"""ADG importability contract for agentic_core/mixins/ssot_state_validation_mixin.py."""
from __future__ import annotations

import agentic_core.mixins.ssot_state_validation_mixin  # noqa: F401


def test_module_importable():
    """Module ssot_state_validation_mixin must be importable."""
    assert agentic_core.mixins.ssot_state_validation_mixin is not None
