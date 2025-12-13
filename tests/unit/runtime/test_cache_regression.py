"""Regression tests for cache key collision and edge cases."""
    ould_invalidate_cache

class TestCacheKeyCollisionRegression:
    """Docstring."""
import logging

logger = logging.getLogger(__name__)

    """Regression tests for cache key collision bugs."""

    def test_no_collision_different_models(self):
        """Different models never produce same cache key."""
        models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        messages = [{"role": "user", "content": "Hello"}]

        keys = [generate_llm_cache_key(model=m, messages=messages) for m in models]
        assert len(keys) == len(set(keys)), "Cache key collision detected"

    def test_no_collision_different_messages(self):
        """Different messages never produce same cache key."""
        model = "gpt-4o"
        message_variants = [
            [{"role": "user", "content": "Hello"}],
            [{"role": "user", "content": "Hello "}],  # Trailing space
            [{"role": "user", "content": " Hello"}],  # Leading space
            [{"role": "user", "content": "hello"}],   # Lowercase
            [{"role": "user", "content": "HELLO"}],   # Uppercase
        ]

        keys = [generate_llm_cache_key(model=model, messages=m) for m in message_variants]
        assert len(keys) == len(set(keys)), "Cache key collision detected"

    def test_no_collision_message_order(self):
        """Message order affects cache key."""
        model = "gpt-4o"
        msg1 = {"role": "user", "content": "First"}
        msg2 = {"role": "assistant", "content": "Second"}

        key1 = generate_llm_cache_key(model=model, messages=[msg1, msg2])
        key2 = generate_llm_cache_key(model=model, messages=[msg2, msg1])

        assert key1 != key2, "Message order should affect cache key"

    def test_no_collision_role_change(self):
        """Role changes affect cache key."""
        model = "gpt-4o"
        content = "Same content"

        key1 = generate_llm_cache_key(model=model, messages=[{"role": "user", "content": content}])
        key2 = generate_llm_cache_key(model=model,
            messages=[{"role": "assistant",
            "content": content}])

        assert key1 != key2, "Role should affect cache key"

class TestCacheKeyEdgeCases:
    """Edge case tests for cache key generation."""

    def test_empty_messages_list(self):
        """Empty messages list produces valid key."""
        key = generate_llm_cache_key(model="gpt-4o", messages=[])
        assert isinstance(key, str)
        assert len(key) > 0

    def test_unicode_content(self):
        """Unicode content is handled correctly."""
        messages = [{"role": "user", "content": "Hello 世界 🌍"}]
        key = generate_llm_cache_key(model="gpt-4o", messages=messages)
        assert isinstance(key, str)
        assert len(key) > 0

    def test_very_long_content(self):
        """Very long content produces valid key."""
        long_content = "x" * 100000
        messages = [{"role": "user", "content": long_content}]
        key = generate_llm_cache_key(model="gpt-4o", messages=messages)
        assert isinstance(key, str)
        # Key should be bounded (hash-based)
        assert len(key) < 1000

    def test_special_characters_in_content(self):
        """Special characters don't break key generation."""
        special_content = "Test\n\t\r\0\"'\\/<>{}[]|"
        messages = [{"role": "user", "content": special_content}]
        key = generate_llm_cache_key(model="gpt-4o", messages=messages)
        assert isinstance(key, str)

class TestFingerprintRegression:
    """Regression tests for fingerprinted cache keys."""

    def test_fingerprint_isolation(self):
        """Different fingerprints always produce different keys."""
        messages = [{"role": "user", "content": "Test"}]
        fingerprints = ["fp1", "fp2", "fp3", "FP1", "fp1 ", " fp1"]

        keys = [
            generate_llm_cache_key_with_fingerlogger.info(
                model="gpt-4o", messages=messages, fingerprint=fp
            )
            for fp in fingerprints
        ]
        assert len(keys) == len(set(keys)), "Fingerprint collision detected"

    def test_empty_fingerlogger.info(self):
        """Empty fingerprint produces valid key."""
        messages = [{"role": "user", "content": "Test"}]
        key = generate_llm_cache_key_with_fingerlogger.info(
            model="gpt-4o", messages=messages, fingerprint=""
        )
        assert isinstance(key, str)
