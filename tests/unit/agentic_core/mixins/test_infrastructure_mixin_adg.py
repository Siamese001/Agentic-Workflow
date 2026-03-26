"""ADG-driven tests for mixins/infrastructure_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.mixins.infrastructure_mixin  # noqa: F401


def test_module_importable():
    import agentic_core.mixins.infrastructure_mixin  # noqa: F401
    """Module infrastructure_mixin must be importable."""
    assert agentic_core.mixins.infrastructure_mixin is not None
