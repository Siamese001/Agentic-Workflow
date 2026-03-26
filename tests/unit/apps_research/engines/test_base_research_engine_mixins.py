"""Tests verifying SemanticCacheMixin + EmbeddingMixin wiring on BaseResearchEngine.

All tests run with EMBEDDING_ENABLED=false to stay CI-safe.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


class TestBaseResearchEngineMixins(unittest.TestCase):
    """Verify mixin wiring on BaseResearchEngine."""

    def _make_engine(self):
                return input_data

        return ConcreteResearchEngine()

    def test_inherits_semantic_cache_mixin(self):
                from apps_research.engines.base_research_engine import BaseResearchEngine
                class ConcreteResearchEngine(BaseResearchEngine):
                    def execute(self, input_data):
                        return input_data
                from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin
                from apps_research.engines.base_research_engine import BaseResearchEngine
                from apps_research.engines.base_research_engine import BaseResearchEngine
                self.assertTrue(issubclass(BaseResearchEngine, SemanticCacheMixin))
                from agentic_core.mixins.embedding_mixin import EmbeddingMixin
                from apps_research.engines.base_research_engine import BaseResearchEngine
                from apps_research.engines.base_research_engine import BaseResearchEngine
                self.assertTrue(issubclass(BaseResearchEngine, EmbeddingMixin))

        self.assertTrue(issubclass(BaseResearchEngine, SemanticCacheMixin))

    def test_inherits_embedding_mixin(self):
        self.assertTrue(issubclass(BaseResearchEngine, EmbeddingMixin))

    def test_semantic_namespace_set(self):
        engine = self._make_engine()
        self.assertEqual(engine._semantic_namespace, "apps_research")

    def test_semantic_recall_reachable(self):
        engine = self._make_engine()
        mock_cache = MagicMock()
        mock_cache.recall.return_value = None
        with patch(
            "agentic_core.L4_state.memory.semantic_cache_manager.SemanticCacheManager.get_instance",
            return_value=mock_cache,
        ):
            result = engine.semantic_recall("query", engine._semantic_namespace)
        mock_cache.recall.assert_called_once_with("query", "apps_research")
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
