"""ADG-driven tests for agentic_core/mixins/meta_learning_mixin.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.mixins.meta_learning_mixin  # noqa: F401


def test_module_importable():
    import agentic_core.mixins.meta_learning_mixin  # noqa: F401
    """Module meta_learning_mixin must be importable."""
    assert agentic_core.mixins.meta_learning_mixin is not None
