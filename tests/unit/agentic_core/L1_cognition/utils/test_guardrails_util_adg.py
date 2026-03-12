"""ADG-driven tests for agentic_core/L1_cognition/utils/guardrails_util.py — fan_in=2.

Contract tests: CacheGuardrails defaults, MetaLearningGuardrails validation methods.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.utils.guardrails_util import (
    CacheGuardrails,
    MetaLearningGuardrails,
)


class TestCacheGuardrails:
    def test_importable(self):
        assert callable(CacheGuardrails)

    def test_default_ttl_positive(self):
        g = CacheGuardrails()
        assert g.default_ttl > 0

    def test_max_ttl_gt_min_ttl(self):
        g = CacheGuardrails()
        assert g.max_ttl > g.min_ttl

    def test_default_similarity_threshold_in_range(self):
        g = CacheGuardrails()
        assert 0.0 < g.default_similarity_threshold <= 1.0

    def test_max_healing_depth_positive(self):
        g = CacheGuardrails()
        assert g.max_healing_depth > 0


class TestMetaLearningGuardrailsValidateCacheKey:
    def setup_method(self):
        self.ml = MetaLearningGuardrails()

    def test_valid_key_passes(self):
        assert self.ml.validate_cache_key("meta_learning:pattern-001") is True

    def test_empty_key_fails(self):
        assert self.ml.validate_cache_key("") is False

    def test_none_key_fails(self):
        assert self.ml.validate_cache_key(None) is False  # type: ignore[arg-type]

    def test_too_long_key_fails(self):
        assert self.ml.validate_cache_key("a" * 257) is False

    def test_path_traversal_fails(self):
        assert self.ml.validate_cache_key("../secret") is False

    def test_slash_prefix_fails(self):
        assert self.ml.validate_cache_key("/etc/passwd") is False

    def test_special_chars_fail(self):
        assert self.ml.validate_cache_key("key with spaces") is False

    def test_alphanumeric_colon_dash_passes(self):
        assert self.ml.validate_cache_key("cache:key-name_01") is True


class TestMetaLearningGuardrailsValidateCacheValue:
    def setup_method(self):
        self.ml = MetaLearningGuardrails()

    def test_none_value_passes(self):
        assert self.ml.validate_cache_value(None) is True

    def test_small_dict_passes(self):
        assert self.ml.validate_cache_value({"k": "v"}) is True

    def test_large_value_fails(self):
        big_str = "x" * (101 * 1024)
        assert self.ml.validate_cache_value(big_str) is False

    def test_non_serializable_fails(self):
        class Unserializable:
            pass
        assert self.ml.validate_cache_value(Unserializable()) is False


class TestMetaLearningGuardrailsValidateTTL:
    def setup_method(self):
        self.ml = MetaLearningGuardrails()

    def test_valid_ttl_returned(self):
        result = self.ml.validate_ttl(3600)
        assert result == 3600

    def test_none_ttl_returns_default(self):
        result = self.ml.validate_ttl(None)
        assert result == self.ml.guardrails.default_ttl

    def test_too_large_ttl_clamped(self):
        result = self.ml.validate_ttl(999999)
        assert result <= self.ml.guardrails.max_ttl

    def test_too_small_ttl_clamped(self):
        result = self.ml.validate_ttl(1)
        assert result >= self.ml.guardrails.min_ttl
