"""Foundational behavioral tests for agentic_core/knowledge/research_cache/cache_store_util.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.knowledge.research_cache.cache_store_util  # noqa: F401


def test_module_importable():
    """Module cache_store_util must be importable."""
    assert agentic_core.knowledge.research_cache.cache_store_util is not None
