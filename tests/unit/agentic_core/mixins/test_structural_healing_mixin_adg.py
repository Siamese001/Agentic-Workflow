"""ADG-driven tests for agentic_core/mixins/structural_healing_mixin.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.mixins.structural_healing_mixin  # noqa: F401


def test_module_importable():
    import agentic_core.mixins.structural_healing_mixin  # noqa: F401
    """Module structural_healing_mixin must be importable."""
    assert agentic_core.mixins.structural_healing_mixin is not None
