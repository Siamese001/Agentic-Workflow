"""ADG importability contract for agentic_core/mixins/ssot_meta_learning_mixin.py."""
from __future__ import annotations

import agentic_core.mixins.ssot_meta_learning_mixin  # noqa: F401


def test_module_importable():
    """Module ssot_meta_learning_mixin must be importable."""
    assert agentic_core.mixins.ssot_meta_learning_mixin is not None
