"""Foundational behavioral tests for agentic_core/cache/cache_key_builders.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.cache.cache_key_builders  # noqa: F401


def test_module_importable():
    """Module cache_key_builders must be importable."""
    assert agentic_core.cache.cache_key_builders is not None
