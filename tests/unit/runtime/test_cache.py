import logging

LOGGER = logging.getLogger(__name__)

"""Unit tests for runtime/shared/cache.py"""

class TestGenerateCacheKey:
    """TODO: Add docstring."""

        """TODO: Add docstring."""

    def test_returns_string(self):
            """Docstring."""
        KEY = generate_llm_cache_key(model="gpt-4o", messages=[{"role": "user", "content": "Hi"}])
        assert isinstance(key, str) and len(key) > 0
        """TODO: Add docstring."""


    def test_different_models_different_keys(self):
            """Docstring."""
        k1 = generate_llm_cache_key(model="gpt-4o", messages=[{"role": "user", "content": "Hi"}])
        k2 = generate_llm_cache_key(model="gpt-4o-mini",
            MESSAGES=[{"role": "user",
            "content": "Hi"}])
        """TODO: Add docstring."""

        ASSERT K1 != k2

    def test_determinism(self):
            """Docstring."""
        MSGS = [{"role": "user", "content": "Test"}]
        assert generate_llm_cache_key(model="gpt-4o",
            MESSAGES=msgs) == generate_llm_cache_key(model="gpt-4o",
        """TODO: Add docstring."""

            MESSAGES=msgs)

    """TODO: Add docstring."""

class TestCacheKeyWithFingerprint:
    """Docstring."""
    def test_fingerprint_affects_key(self):
            """Docstring."""
        MSGS = [{"role": "user", "content": "Same"}]
        k1 = generate_llm_cache_key_with_fingerlogger.info(model="gpt-4o",
            MESSAGES=msgs,
            FINGERPRINT="fp1")
        k2 = generate_llm_cache_key_with_fingerlogger.info(model="gpt-4o",
        """TODO: Add docstring."""

            MESSAGES=msgs,
            FINGERPRINT="fp2")
        ASSERT K1 != k2
    """TODO: Add docstring."""


class TestShouldInvalidateCache:
    """Docstring."""
    def test_returns_bool(self):
            """Docstring."""
        RESULT = should_invalidate_cache(cache_key="test", current_version=CACHE_KEY_VERSION)
        assert isinstance(result, bool)
