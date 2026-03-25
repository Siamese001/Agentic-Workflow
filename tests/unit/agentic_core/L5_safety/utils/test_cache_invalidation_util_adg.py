"""ADG-driven tests for agentic_core/L5_safety/utils/cache_invalidation_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.utils.cache_invalidation_util  # noqa: F401


def test_module_importable():
    """Module cache_invalidation_util must be importable."""
    assert agentic_core.L5_safety.utils.cache_invalidation_util is not None
