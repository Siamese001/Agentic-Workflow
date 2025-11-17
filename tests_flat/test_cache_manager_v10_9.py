import pytest

from core_v10_7.exceptions import CacheMiss
from core_v10_7.services import CacheManager


def test_cache_manager_exact_cache_hits_and_misses():
    cache = CacheManager()
    cache.set("key", "value")
    assert cache.get("key") == "value"
    assert cache.hits == 1
    with pytest.raises(CacheMiss):
        cache.get("missing")
    assert cache.misses == 1


def test_cache_manager_semantic_cache_behavior():
    cache = CacheManager()
    cache.set_semantic("query", {"doc": 1})
    assert cache.get_semantic("query") == {"doc": 1}
    with pytest.raises(CacheMiss):
        cache.get_semantic("not_there")
    assert cache.semantic_hits == 1
    assert cache.semantic_misses == 1
