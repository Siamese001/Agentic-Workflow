"""Foundational behavioral tests for agentic_core/mixins/healer_mixin.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.mixins.healer_mixin  # noqa: F401


def test_module_importable():
    import agentic_core.mixins.healer_mixin  # noqa: F401
    """Module healer_mixin must be importable."""
    assert agentic_core.mixins.healer_mixin is not None
