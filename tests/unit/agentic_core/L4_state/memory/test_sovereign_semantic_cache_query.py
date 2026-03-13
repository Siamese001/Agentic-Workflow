"""Regression tests for SovereignSemanticCache.query() — P1 fix.

All tests run with EMBEDDING_ENABLED=false to stay CI-safe.
"""

from __future__ import annotations

import os
import unittest
from unittest.mock import MagicMock, patch


def _make_memory_item(key: str, vector: list[float], metadata: dict, namespace: str = ""):
    """Build a MemoryItem for injection into InMemoryVectorStore._storage."""
    import uuid

    from agentic_core.L4_state.types.memory_item_types import MemoryItem

    meta = dict(metadata)
    if namespace:
        meta["namespace"] = namespace
    uid = uuid.uuid5(uuid.NAMESPACE_DNS, key)
    return MemoryItem(id=uid, content=metadata.get("path", key), embedding=vector, metadata=meta)


class TestSovereignSemanticCacheQuery(unittest.TestCase):
    """Tests for the .query() method added in Phase 1."""

    def _make_cache(self):
        """Build a SovereignSemanticCache with mocked Redis (no live connection)."""
        with patch("agentic_core.L4_state.memory.sovereign_semantic_cache.get_redis_client") as mock_redis:
            mock_redis.return_value = MagicMock()
            from agentic_core.L4_state.memory.sovereign_semantic_cache import (
                SovereignSemanticCache,
            )

            cache = SovereignSemanticCache(mission_id="test-mission")
        return cache

    def _inject(self, cache, key: str, vector: list[float], metadata: dict = None, namespace: str = ""):
        """Inject a MemoryItem directly into the underlying _storage dict."""
        item = _make_memory_item(key, vector, metadata or {}, namespace)
        cache._vector_store._storage[key] = item
        if key not in cache._vector_store._ordered_ids:
            cache._vector_store._ordered_ids.append(key)

    def test_query_returns_empty_when_kill_switch_active(self):
        """query() must return [] when EMBEDDING_ENABLED=false."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "false"}):
            cache = self._make_cache()
            self._inject(cache, "key1", [0.1, 0.2, 0.3], {"path": "foo.py"}, "canon-files")
            result = cache.query("some query text")
            self.assertEqual(result, [])

    def test_query_returns_empty_when_store_empty(self):
        """query() must return [] when vector store has no entries."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                return_value=[[0.1, 0.9]],
            ):
                result = cache.query("some query")
            self.assertEqual(result, [])

    def test_query_returns_sorted_results(self):
        """query() must rank results by descending cosine similarity."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            self._inject(cache, "high", [1.0, 0.0], {"path": "high.py"}, "test")
            self._inject(cache, "low", [0.0, 1.0], {"path": "low.py"}, "test")
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                return_value=[[1.0, 0.0]],
            ):
                results = cache.query("q", top_k=10)

            self.assertGreater(len(results), 0)
            scores = [r["score"] for r in results]
            self.assertEqual(scores, sorted(scores, reverse=True))

    def test_query_respects_top_k(self):
        """query() must respect the top_k limit."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            for i in range(1, 11):
                self._inject(cache, f"key{i}", [float(i), 1.0])
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                return_value=[[1.0, 0.5]],
            ):
                results = cache.query("q", top_k=3)
            self.assertLessEqual(len(results), 3)

    def test_query_filters_by_namespace(self):
        """query() must exclude entries whose namespace does not match."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            self._inject(cache, "match", [1.0, 0.0], {"path": "match.py"}, "wanted")
            self._inject(cache, "nomatch", [1.0, 0.0], {"path": "skip.py"}, "other")
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                return_value=[[1.0, 0.0]],
            ):
                results = cache.query("q", namespace="wanted")
            hashes = [r["content_hash"] for r in results]
            self.assertIn("match", hashes)
            self.assertNotIn("nomatch", hashes)

    def test_query_result_schema(self):
        """Each result must contain content_hash, score, and content keys."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            self._inject(cache, "entry", [0.5, 0.5], {"path": "entry.py"})
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                return_value=[[0.5, 0.5]],
            ):
                results = cache.query("q")
            self.assertEqual(len(results), 1)
            r = results[0]
            self.assertIn("content_hash", r)
            self.assertIn("score", r)
            self.assertIn("content", r)

    def test_query_graceful_on_embedder_failure(self):
        """query() must return [] if BGEEmbedder raises, not propagate the error."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            self._inject(cache, "entry", [0.5, 0.5])
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                side_effect=RuntimeError("model unavailable"),
            ):
                result = cache.query("q")
            self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
