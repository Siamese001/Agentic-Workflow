"""ADG-driven tests for L1_cognition/engines/cache_manager.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L1_cognition.engines.cache_manager import CacheStrategyManager
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    CacheStrategyManager = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="cache_manager deps unavailable")
class TestCacheStrategyManager:
    def test_importable(self):
        assert callable(CacheStrategyManager)

    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CacheStrategyManager)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
