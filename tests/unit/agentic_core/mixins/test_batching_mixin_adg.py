"""ADG-driven tests for agentic_core/mixins/batching_mixin.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.mixins.batching_mixin  # noqa: F401


def test_module_importable():
        import agentic_core.mixins.batching_mixin  # noqa: F401
        """Module batching_mixin must be importable."""
        assert agentic_core.mixins.batching_mixin is not None

    assert agentic_core.mixins.batching_mixin is not None
