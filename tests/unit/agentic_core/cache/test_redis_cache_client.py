"""Foundational behavioral tests for agentic_core/cache/redis_cache_client.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.cache.redis_cache_client  # noqa: F401


def test_module_importable():
    """Module redis_cache_client must be importable."""
    assert agentic_core.cache.redis_cache_client is not None
