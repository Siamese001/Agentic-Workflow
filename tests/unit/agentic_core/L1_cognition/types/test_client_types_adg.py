"""ADG-driven tests for agentic_core/L1_cognition/types/client_types.py — fan_in=2.

Contract tests: HealingPattern, CacheEntry, and module-level constants.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.client_types import (
    CACHE_KEY_PREFIX,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TTL_SECONDS,
    MAX_HEALING_DEPTH,
    PINECONE_NAMESPACE_PREFIX,
    CacheEntry,
    HealingPattern,
)


class TestConstants:
    def test_similarity_threshold_float(self):
        assert isinstance(DEFAULT_SIMILARITY_THRESHOLD, float)
        assert 0.0 < DEFAULT_SIMILARITY_THRESHOLD <= 1.0

    def test_ttl_positive(self):
        assert DEFAULT_TTL_SECONDS > 0

    def test_max_healing_depth_positive(self):
        assert MAX_HEALING_DEPTH > 0

    def test_cache_key_prefix_string(self):
        assert isinstance(CACHE_KEY_PREFIX, str)
        assert CACHE_KEY_PREFIX

    def test_pinecone_namespace_prefix_string(self):
        assert isinstance(PINECONE_NAMESPACE_PREFIX, str)


class TestHealingPattern:
    def _make(self, **kw) -> HealingPattern:
        return HealingPattern(
            pattern_id=kw.get("pattern_id", "p-001"),
            violation_type=kw.get("violation_type", "LAYER_BREACH"),
            error_signature=kw.get("error_signature", "sig-abc"),
            healing_strategy=kw.get("healing_strategy", {"action": "move_file"}),
        )

    def test_valid_creation(self):
        p = self._make()
        assert p.pattern_id == "p-001"
        assert p.violation_type == "LAYER_BREACH"

    def test_default_success_count(self):
        p = self._make()
        assert p.success_count == 1

    def test_embedding_defaults_none(self):
        p = self._make()
        assert p.embedding is None

    def test_to_dict_has_required_keys(self):
        p = self._make()
        d = p.to_dict()
        for key in ("pattern_id", "violation_type", "error_signature", "healing_strategy"):
            assert key in d

    def test_from_dict_roundtrip(self):
        p = self._make()
        d = p.to_dict()
        p2 = HealingPattern.from_dict(d)
        assert p2.pattern_id == p.pattern_id
        assert p2.violation_type == p.violation_type

    def test_from_dict_empty_uses_defaults(self):
        p = HealingPattern.from_dict({})
        assert p.pattern_id == ""
        assert p.success_count == 1


class TestCacheEntry:
    def test_valid_creation(self):
        entry = CacheEntry(key="test_key", value={"data": 42})
        assert entry.key == "test_key"
        assert entry.value == {"data": 42}

    def test_default_ttl(self):
        entry = CacheEntry(key="k", value="v")
        assert entry.ttl == DEFAULT_TTL_SECONDS

    def test_hit_count_defaults_zero(self):
        entry = CacheEntry(key="k", value="v")
        assert entry.hit_count == 0

    def test_is_expired_fresh_entry(self):
        entry = CacheEntry(key="k", value="v", ttl=9999)
        assert entry.is_expired() is False

    def test_is_expired_old_entry(self):
        import time
        entry = CacheEntry(key="k", value="v", ttl=0, created_at=time.time() - 10)
        assert entry.is_expired() is True
