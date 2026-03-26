"""Tests verifying SemanticCacheMixin + EmbeddingMixin wiring on BaseExecEngine.

All tests run with EMBEDDING_ENABLED=false to stay CI-safe.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


class TestBaseExecEngineMixins(unittest.TestCase):
    """Verify mixin wiring on BaseExecEngine."""

    def _make_engine(self):
                return input_data

        return ConcreteExecEngine()

    def test_inherits_semantic_cache_mixin(self):
                from apps_exec.engines.base_exec_engine import BaseExecEngine
                class ConcreteExecEngine(BaseExecEngine):
                    def execute(self, input_data):
                        return input_data
                from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin
                from apps_exec.engines.base_exec_engine import BaseExecEngine
                from apps_exec.engines.base_exec_engine import BaseExecEngine
                self.assertTrue(issubclass(BaseExecEngine, SemanticCacheMixin))
                from agentic_core.mixins.embedding_mixin import EmbeddingMixin
                from apps_exec.engines.base_exec_engine import BaseExecEngine
                from apps_exec.engines.base_exec_engine import BaseExecEngine
                self.assertTrue(issubclass(BaseExecEngine, EmbeddingMixin))

        self.assertTrue(issubclass(BaseExecEngine, SemanticCacheMixin))

    def test_inherits_embedding_mixin(self):
        self.assertTrue(issubclass(BaseExecEngine, EmbeddingMixin))

    def test_semantic_namespace_set(self):
        engine = self._make_engine()
        self.assertEqual(engine._semantic_namespace, "apps_exec")

    def test_semantic_recall_reachable(self):
        engine = self._make_engine()
        mock_cache = MagicMock()
        mock_cache.recall.return_value = None
        with patch(
            "agentic_core.L4_state.memory.semantic_cache_manager.SemanticCacheManager.get_instance",
            return_value=mock_cache,
        ):
            result = engine.semantic_recall("test query", engine._semantic_namespace)
        mock_cache.recall.assert_called_once_with("test query", "apps_exec")
        self.assertIsNone(result)

    def test_semantic_learn_reachable(self):
        engine = self._make_engine()
        mock_cache = MagicMock()
        with patch(
            "agentic_core.L4_state.memory.semantic_cache_manager.SemanticCacheManager.get_instance",
            return_value=mock_cache,
        ):
            engine.semantic_learn("ctx", engine._semantic_namespace, {"result": "x"})
        mock_cache.learn.assert_called_once()

    def test_get_embedding_method_exists(self):
        """get_embedding and get_embeddings_batch must be present on the engine."""
        import inspect

        engine = self._make_engine()
        self.assertTrue(hasattr(engine, "get_embedding"))
        self.assertTrue(inspect.iscoroutinefunction(engine.get_embedding))
        self.assertTrue(hasattr(engine, "get_embeddings_batch"))
        self.assertTrue(inspect.iscoroutinefunction(engine.get_embeddings_batch))

    def test_semantic_stats_reachable(self):
        engine = self._make_engine()
        mock_cache = MagicMock()
        mock_cache.get_statistics.return_value = {"hits": 0, "misses": 0}
        with patch(
            "agentic_core.L4_state.memory.semantic_cache_manager.SemanticCacheManager.get_instance",
            return_value=mock_cache,
        ):
            stats = engine.semantic_stats()
        self.assertIn("hits", stats)


if __name__ == "__main__":
    unittest.main()
