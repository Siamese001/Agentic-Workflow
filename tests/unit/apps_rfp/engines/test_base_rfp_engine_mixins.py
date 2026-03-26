"""Tests verifying SemanticCacheMixin + EmbeddingMixin wiring on BaseRfpEngine.

All tests run with EMBEDDING_ENABLED=false to stay CI-safe.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


class TestBaseRfpEngineMixins(unittest.TestCase):
    """Verify mixin wiring on BaseRfpEngine."""

    def _make_engine(self):
                return input_data

        return ConcreteRfpEngine()

    def test_inherits_semantic_cache_mixin(self):
                from apps_rfp.engines.base_rfp_engine import BaseRfpEngine
                class ConcreteRfpEngine(BaseRfpEngine):
                    def execute(self, input_data):
                        return input_data
                from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin
                from apps_rfp.engines.base_rfp_engine import BaseRfpEngine
                from apps_rfp.engines.base_rfp_engine import BaseRfpEngine
                self.assertTrue(issubclass(BaseRfpEngine, SemanticCacheMixin))
                from agentic_core.mixins.embedding_mixin import EmbeddingMixin
                from apps_rfp.engines.base_rfp_engine import BaseRfpEngine
                from apps_rfp.engines.base_rfp_engine import BaseRfpEngine
                self.assertTrue(issubclass(BaseRfpEngine, EmbeddingMixin))

        self.assertTrue(issubclass(BaseRfpEngine, SemanticCacheMixin))

    def test_inherits_embedding_mixin(self):
        self.assertTrue(issubclass(BaseRfpEngine, EmbeddingMixin))

    def test_semantic_namespace_set(self):
        engine = self._make_engine()
        self.assertEqual(engine._semantic_namespace, "apps_rfp")

    def test_semantic_recall_reachable(self):
        engine = self._make_engine()
        mock_cache = MagicMock()
        mock_cache.recall.return_value = None
        with patch(
            "agentic_core.L4_state.memory.semantic_cache_manager.SemanticCacheManager.get_instance",
            return_value=mock_cache,
        ):
            result = engine.semantic_recall("query", engine._semantic_namespace)
        mock_cache.recall.assert_called_once_with("query", "apps_rfp")
        self.assertIsNone(result)

    def test_semantic_learn_reachable(self):
        engine = self._make_engine()
        mock_cache = MagicMock()
        with patch(
            "agentic_core.L4_state.memory.semantic_cache_manager.SemanticCacheManager.get_instance",
            return_value=mock_cache,
        ):
            engine.semantic_learn("ctx", engine._semantic_namespace, {"k": "v"})
        mock_cache.learn.assert_called_once()

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
