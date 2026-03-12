"""ADG-driven tests for L4_state/utils/rag_enhancement_util.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.utils.rag_enhancement_util import (
    CacheSufficiencyResult,
    semantic_cache,
)


class TestCacheSufficiencyResult:
    def test_creates_sufficient(self):
        r = CacheSufficiencyResult(is_sufficient=True, cached_response="hi", confidence=1.0)
        assert r.is_sufficient is True

    def test_creates_insufficient(self):
        r = CacheSufficiencyResult(is_sufficient=False, reason="cache miss")
        assert r.is_sufficient is False
        assert r.reason == "cache miss"

    def test_confidence_default_zero(self):
        r = CacheSufficiencyResult(is_sufficient=False)
        assert r.confidence == 0.0


class TestSemanticCache:
    def test_creates(self):
        cache = semantic_cache()
        assert cache is not None

    def test_get_missing_returns_none(self):
        cache = semantic_cache()
        assert cache.get("missing_key") is None

    def test_set_and_get(self):
        cache = semantic_cache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_check_sufficiency_miss(self):
        cache = semantic_cache()
        result = cache.check_sufficiency("unknown query")
        assert isinstance(result, CacheSufficiencyResult)
        assert result.is_sufficient is False

    def test_check_sufficiency_hit(self):
        cache = semantic_cache()
        cache.set("my query", "cached answer")
        result = cache.check_sufficiency("my query")
        assert result.is_sufficient is True
        assert result.confidence == pytest.approx(1.0)
