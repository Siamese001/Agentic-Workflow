"""Regression tests: HybridSearchEngine global BGE vector path.

Four invariants proven (fully offline — SentenceTransformer and chromadb stubbed):
  T1 — get_global_hybrid_engine() injects a real chroma_client (not None)
  T2 — _generate_query_embedding() returns a 1024-dim float vector
  T3 — hybrid_search() calls engine.search() with correct positional args (no top_k kwarg)
  T4 — vector leg returns results from the live Chroma client path (not early-exit)
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import numpy as np


# ---------------------------------------------------------------------------
# Shared fake helpers
# ---------------------------------------------------------------------------


def _make_fake_st(dim: int = 1024):
    fake = MagicMock()
    fake.encode.return_value = np.ones((1, dim), dtype=np.float32)
    return fake


def _make_fake_chroma_client(dim: int = 1024):
    """Return a chromadb.PersistentClient fake whose single collection holds dim-dim vectors."""
    fake_col = MagicMock()
    fake_col.get.return_value = {"embeddings": np.ones((1, dim), dtype=np.float32)}
    fake_col.query.return_value = {
        "ids": [["id1", "id2"]],
        "documents": [["doc one", "doc two"]],
        "metadatas": [[{"file_path": "a.py"}, {"file_path": "b.py"}]],
        "distances": [[0.1, 0.2]],
    }
    fake_client = MagicMock()
    fake_client.get_collection.return_value = fake_col
    return fake_client, fake_col


def _reset_global_engine():
    """Force the singleton to re-initialize on next call."""
    import agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine as mod

    mod._global_hybrid_engine = None


# ---------------------------------------------------------------------------
# T1 — get_global_hybrid_engine() no longer leaves chroma_client=None
# ---------------------------------------------------------------------------


class TestGlobalEngineHasChromaClient(unittest.TestCase):
    """T1: the global singleton must inject a real chromadb client."""

    def setUp(self):
        _reset_global_engine()

    def tearDown(self):
        _reset_global_engine()

    def test_chroma_client_is_not_none(self):
        fake_client, _ = _make_fake_chroma_client()
        with patch("chromadb.PersistentClient", return_value=fake_client):
            from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
                get_global_hybrid_engine,
            )

            engine = get_global_hybrid_engine()
        self.assertIsNotNone(
            engine.chroma_client,
            "chroma_client must not be None after get_global_hybrid_engine()",
        )

    def test_chroma_client_type_is_injected_client(self):
        fake_client, _ = _make_fake_chroma_client()
        with patch("chromadb.PersistentClient", return_value=fake_client):
            from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
                get_global_hybrid_engine,
            )

            engine = get_global_hybrid_engine()
        self.assertIs(engine.chroma_client, fake_client)

    def test_global_engine_is_singleton(self):
        fake_client, _ = _make_fake_chroma_client()
        with patch("chromadb.PersistentClient", return_value=fake_client):
            from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
                get_global_hybrid_engine,
            )

            e1 = get_global_hybrid_engine()
            e2 = get_global_hybrid_engine()
        self.assertIs(e1, e2, "get_global_hybrid_engine() must return the same object on repeated calls")


# ---------------------------------------------------------------------------
# T2 — _generate_query_embedding() returns 1024-dim floats
# ---------------------------------------------------------------------------


class TestGenerateQueryEmbedding(unittest.TestCase):
    """T2: embedding generator must produce exactly 1024-dim float vectors."""

    def _make_engine(self):
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchEngine

        engine = HybridSearchEngine()
        engine._bge_model = _make_fake_st(1024)
        return engine

    def test_returns_1024_dim(self):
        engine = self._make_engine()
        vec = engine._generate_query_embedding("test query")
        self.assertIsNotNone(vec)
        self.assertEqual(len(vec), 1024)

    def test_returns_float_list(self):
        engine = self._make_engine()
        vec = engine._generate_query_embedding("test query")
        self.assertTrue(all(isinstance(v, float) for v in vec), "All embedding values must be Python floats")

    def test_returns_none_on_import_error(self):
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchEngine

        engine = HybridSearchEngine()
        # Simulate sentence_transformers missing
        with patch("builtins.__import__", side_effect=ImportError("no module")):
            # _bge_model is None so it will try to import
            result = engine._generate_query_embedding("test")
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# T3 — hybrid_search() calls engine.search() with correct args
# ---------------------------------------------------------------------------


class TestHybridSearchConvenienceWrapper(unittest.TestCase):
    """T3: hybrid_search() must forward args correctly — no top_k kwarg."""

    def setUp(self):
        _reset_global_engine()

    def tearDown(self):
        _reset_global_engine()

    def test_hybrid_search_calls_search_correctly(self):
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import hybrid_search

        fake_client, _ = _make_fake_chroma_client()
        with patch("chromadb.PersistentClient", return_value=fake_client):
            _reset_global_engine()
            from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
                get_global_hybrid_engine,
            )

            engine = get_global_hybrid_engine()

        engine.search = MagicMock(return_value=[])
        engine._bge_model = _make_fake_st(1024)

        # Patch the global engine so hybrid_search uses our spy
        import agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine as mod

        original = mod._global_hybrid_engine
        mod._global_hybrid_engine = engine
        try:
            hybrid_search("test query", collection_name="code_chunks")
            engine.search.assert_called_once_with("test query", None, "code_chunks")
        finally:
            mod._global_hybrid_engine = original

    def test_hybrid_search_does_not_pass_top_k(self):
        """Regression: the old wrapper passed top_k as a kwarg which search() doesn't accept."""
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchEngine

        engine = HybridSearchEngine()

        # search() must accept (query, query_embedding, collection_name) — no top_k
        import inspect

        sig = inspect.signature(engine.search)
        self.assertNotIn("top_k", sig.parameters, "search() must not have a top_k parameter")

    def test_hybrid_search_default_collection_is_code_chunks(self):
        """Default collection_name in hybrid_search must be code_chunks (BGE-aligned)."""
        import agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine as mod

        fake_engine = MagicMock()
        fake_engine.search.return_value = []
        original = mod._global_hybrid_engine
        mod._global_hybrid_engine = fake_engine
        try:
            mod.hybrid_search("some query")
            call_args = fake_engine.search.call_args
            # Third positional arg is collection_name
            self.assertEqual(call_args.args[2], "code_chunks")
        finally:
            mod._global_hybrid_engine = original


# ---------------------------------------------------------------------------
# T4 — vector leg returns results, no early-exit
# ---------------------------------------------------------------------------


class TestVectorLegNotDead(unittest.TestCase):
    """T4: with a real chroma_client injected, _vector_search must produce results."""

    def _make_engine_with_chroma(self, dim: int = 1024):
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchEngine

        fake_client, fake_col = _make_fake_chroma_client(dim)
        engine = HybridSearchEngine(chroma_client=fake_client)
        engine._bge_model = _make_fake_st(1024)
        return engine, fake_col

    def test_vector_search_returns_results_when_client_present(self):
        engine, _ = self._make_engine_with_chroma()
        results = engine._vector_search("test", None, "code_chunks", None)
        self.assertGreater(len(results), 0, "_vector_search must not early-return when chroma_client is set")

    def test_vector_search_early_exits_only_when_client_is_none(self):
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchEngine

        engine = HybridSearchEngine(chroma_client=None)
        results = engine._vector_search("test", None, "code_chunks", None)
        self.assertEqual(results, {}, "_vector_search must return empty dict when chroma_client is None")

    def test_search_produces_vector_sourced_results(self):
        engine, _ = self._make_engine_with_chroma()
        results = engine.search("UniversalWriteGateway", collection_name="code_chunks")
        vec_results = [r for r in results if r.source == "vector"]
        self.assertGreater(
            len(vec_results), 0, "search() must include vector-sourced results when client is present"
        )

    def test_vector_results_have_positive_scores(self):
        engine, _ = self._make_engine_with_chroma()
        results = engine.search("test", collection_name="code_chunks")
        vec_results = [r for r in results if r.source == "vector"]
        for r in vec_results:
            self.assertGreater(r.vector_score, 0.0, f"vector_score must be positive, got {r.vector_score}")


if __name__ == "__main__":
    unittest.main()
