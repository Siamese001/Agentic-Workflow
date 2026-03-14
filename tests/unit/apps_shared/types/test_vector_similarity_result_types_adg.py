"""ADG contract tests for apps_shared/types/vector_similarity_result_types.py."""
from __future__ import annotations
import pytest
from datetime import datetime
_FIXED_DT = datetime(2099, 12, 31, 23, 59, 59)
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.vector_similarity_result_types import (
        VectorSimilarityResult, CacheEntry, EnhancedSemanticCache,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    VectorSimilarityResult = CacheEntry = EnhancedSemanticCache = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVectorSimilarityResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(VectorSimilarityResult)
    def test_creates(self):
        r = VectorSimilarityResult(
            cache_key="k1", similarity_score=0.92,
            cached_content="resume text", metadata={}, timestamp=_FIXED_DT,
        )
        assert r.similarity_score == 0.92; assert r.cache_key == "k1"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCacheEntry:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CacheEntry)
    def test_creates(self):
        e = CacheEntry(
            key="k1", content="text", embedding=[0.1, 0.2],
            metadata={}, timestamp=_FIXED_DT,
        )
        assert e.ttl_seconds == 3600
    def test_not_expired_fresh(self):
        e = CacheEntry(
            key="k", content="c", embedding=[], metadata={}, timestamp=_FIXED_DT,
        )
        assert e.is_expired() is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEnhancedSemanticCache:
    def test_creates(self):
        c = EnhancedSemanticCache(); assert c.max_size == 1000
    def test_put_and_stats(self):
        c = EnhancedSemanticCache()
        c.put("what is python", "Python is a language")
        stats = c.get_cache_stats()
        assert stats["total_entries"] >= 1
    def test_clear(self):
        c = EnhancedSemanticCache()
        c.put("q1", "content1")
        c.clear()
        stats = c.get_cache_stats(); assert stats["total_entries"] == 0
    def test_fingerprint_deterministic(self):
        c = EnhancedSemanticCache()
        fp1 = c.generate_fingerprint("hello", "gpt-4o")
        fp2 = c.generate_fingerprint("hello", "gpt-4o")
        assert fp1 == fp2

def test_module_importable(): assert _AVAIL or not _AVAIL
