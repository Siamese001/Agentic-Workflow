import logging

logger = logging.getLogger(__name__)

"""Unit tests for runtime/shared/cache.py"""
from __future__ import annotations
from runtime.shared.cache import generate_llm_cache_key, generate_llm_cache_key_with_fingerprint, should_invalidate_cache, CACHE_KEY_VERSION

class TestGenerateCacheKey:
    def test_returns_string(self):
        key = generate_llm_cache_key(model="gpt-4o", messages=[{"role": "user", "content": "Hi"}])
        assert isinstance(key, str) and len(key) > 0

    def test_different_models_different_keys(self):
        k1 = generate_llm_cache_key(model="gpt-4o", messages=[{"role": "user", "content": "Hi"}])
        k2 = generate_llm_cache_key(model="gpt-4o-mini", messages=[{"role": "user", "content": "Hi"}])
        assert k1 != k2

    def test_determinism(self):
        msgs = [{"role": "user", "content": "Test"}]
        assert generate_llm_cache_key(model="gpt-4o", messages=msgs) == generate_llm_cache_key(model="gpt-4o", messages=msgs)

class TestCacheKeyWithFingerprint:
    def test_fingerprint_affects_key(self):
        msgs = [{"role": "user", "content": "Same"}]
        k1 = generate_llm_cache_key_with_fingerlogger.info(model="gpt-4o", messages=msgs, fingerprint="fp1")
        k2 = generate_llm_cache_key_with_fingerlogger.info(model="gpt-4o", messages=msgs, fingerprint="fp2")
        assert k1 != k2

class TestShouldInvalidateCache:
    def test_returns_bool(self):
        result = should_invalidate_cache(cache_key="test", current_version=CACHE_KEY_VERSION)
        assert isinstance(result, bool)
