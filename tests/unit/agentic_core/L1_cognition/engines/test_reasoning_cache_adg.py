"""ADG-driven tests for L1_cognition/engines/reasoning_cache.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.engines.reasoning_cache import ReasoningCache


class TestReasoningCache:
    def test_creates_with_defaults(self):
        cache = ReasoningCache()
        assert cache.maxsize == 10000
        assert cache.hits == 0
        assert cache.misses == 0

    def test_creates_with_custom_maxsize(self):
        cache = ReasoningCache(maxsize=100)
        assert cache.maxsize == 100

    def test_has_make_key(self):
        assert hasattr(ReasoningCache, "_make_key")

    def test_cache_starts_empty(self):
        cache = ReasoningCache()
        assert len(cache.cache) == 0

    def test_make_key_is_stable(self):
        cache = ReasoningCache()
        key1 = cache._make_key("problem", {"ctx": 1}, ("gpt-4",))
        key2 = cache._make_key("problem", {"ctx": 1}, ("gpt-4",))
        assert key1 == key2

    def test_make_key_differs_on_different_input(self):
        cache = ReasoningCache()
        key1 = cache._make_key("problem_a", {}, ())
        key2 = cache._make_key("problem_b", {}, ())
        assert key1 != key2
