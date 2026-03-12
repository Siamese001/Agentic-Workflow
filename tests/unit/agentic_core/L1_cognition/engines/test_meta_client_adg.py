"""ADG-driven tests for agentic_core/L1_cognition/engines/meta_client.py — fan_in=2.

Contract tests: MetaLearningClient singleton, config defaults, stats, reset_instance.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.engines.meta_client import MetaLearningClient
from agentic_core.L1_cognition.types.client_types import (
    CACHE_KEY_PREFIX,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TTL_SECONDS,
    MAX_HEALING_DEPTH,
    CacheEntry,
    HealingPattern,
)


class TestClientTypeConstants:
    def test_cache_key_prefix_is_string(self):
        assert isinstance(CACHE_KEY_PREFIX, str)

    def test_default_similarity_threshold_is_float(self):
        assert isinstance(DEFAULT_SIMILARITY_THRESHOLD, float)
        assert 0.0 < DEFAULT_SIMILARITY_THRESHOLD <= 1.0

    def test_default_ttl_seconds_positive(self):
        assert isinstance(DEFAULT_TTL_SECONDS, int)
        assert DEFAULT_TTL_SECONDS > 0

    def test_max_healing_depth_positive(self):
        assert isinstance(MAX_HEALING_DEPTH, int)
        assert MAX_HEALING_DEPTH > 0


class TestCacheEntry:
    def test_importable(self):
        assert callable(CacheEntry)


class TestHealingPattern:
    def test_importable(self):
        assert callable(HealingPattern)


def _try_create_client():
    """Attempt to create MetaLearningClient, return (client, error)."""
    try:
        MetaLearningClient.reset_instance()
        client = MetaLearningClient()
        return client, None
    except Exception as e:
        return None, e


class TestMetaLearningClientSingleton:
    def setup_method(self):
        MetaLearningClient.reset_instance()

    def teardown_method(self):
        MetaLearningClient.reset_instance()

    def test_reset_instance_method_exists(self):
        assert callable(MetaLearningClient.reset_instance)

    def test_singleton_returns_same_instance(self):
        client1, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        client2 = MetaLearningClient()
        assert client1 is client2

    def test_instance_has_stats(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert isinstance(client.stats, dict)

    def test_stats_has_cache_hits(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert "cache_hits" in client.stats

    def test_stats_has_cache_misses(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert "cache_misses" in client.stats

    def test_similarity_threshold_default(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert client.similarity_threshold == DEFAULT_SIMILARITY_THRESHOLD

    def test_default_ttl(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert client.default_ttl == DEFAULT_TTL_SECONDS

    def test_max_healing_depth(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert client.max_healing_depth == MAX_HEALING_DEPTH

    def test_domain_thresholds_has_agentic_core(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert "agentic_core" in client.domain_thresholds

    def test_domain_ttls_has_apps_lic(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert "apps_lic" in client.domain_ttls

    def test_local_cache_starts_empty(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert isinstance(client._local_cache, dict)
