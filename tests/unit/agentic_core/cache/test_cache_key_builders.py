"""Test CacheKeyBuilders functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCacheKeyBuilders:
    """Test CacheKeyBuilders functionality."""

    def test_cache_key_builders_imports(self):
        """Test cache_key_builders module imports."""
        from agentic_core import cache_key_builders

        assert cache_key_builders is not None

    def test_cache_key_builders_class(self):
        """Test CacheKeyBuilders class exists."""
        from agentic_core import CacheKeyBuilders

        assert CacheKeyBuilders is not None

    def test_cache_key_builders_callable(self):
        """Test cache_key_builders functions are callable."""
        from agentic_core import validate_cache_key_builders

        assert callable(validate_cache_key_builders)


@pytest.mark.unit
class TestBuildSemanticCacheD2Key:
    """Phase A: build_semantic_cache_d2_key determinism and validation tests."""

    _VALID_HASH = "a" * 64

    def _call(self, **kwargs):
        from agentic_core.cache.cache_key_builders import build_semantic_cache_d2_key

        defaults = {
            "tenant_id": "tenant1",
            "namespace": "ns",
            "embedding_model_id": "bge-m3-v1",
            "corpus_version": self._VALID_HASH,
            "query_hash": self._VALID_HASH,
        }
        defaults.update(kwargs)
        return build_semantic_cache_d2_key(**defaults)

    def test_deterministic_same_inputs(self):
        """Identical inputs always produce identical keys."""
        assert self._call() == self._call()

    def test_key_schema(self):
        """Key matches d2_scache:{t}:{ns}:{model}:{corpus}:{query} schema."""
        key = self._call(
            tenant_id="t1",
            namespace="ns1",
            embedding_model_id="bge-m3-v1",
            corpus_version=self._VALID_HASH,
            query_hash=self._VALID_HASH,
        )
        assert key == f"d2_scache:t1:ns1:bge-m3-v1:{self._VALID_HASH}:{self._VALID_HASH}"

    def test_different_inputs_produce_different_keys(self):
        """Different query hashes produce different keys."""
        h1 = "a" * 64
        h2 = "b" * 64
        assert self._call(query_hash=h1) != self._call(query_hash=h2)

    def test_rejects_empty_tenant_id(self):
        """Empty tenant_id raises ValueError."""
        with pytest.raises(ValueError):
            self._call(tenant_id="")

    def test_rejects_tenant_id_with_colon(self):
        """tenant_id containing colon raises ValueError."""
        with pytest.raises(ValueError):
            self._call(tenant_id="ten:ant")

    def test_rejects_short_corpus_version(self):
        """corpus_version shorter than 64 hex chars raises ValueError."""
        with pytest.raises(ValueError):
            self._call(corpus_version="abc123")

    def test_rejects_non_hex_query_hash(self):
        """query_hash containing non-hex chars raises ValueError."""
        with pytest.raises(ValueError):
            self._call(query_hash="z" * 64)
