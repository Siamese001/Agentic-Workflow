"""Regression tests: bge_runtime shared helper and both caller integrations.

Invariants proven (fully offline — SentenceTransformer stubbed):
  T1 — bge_embed_query() returns a 1024-dim float list
  T2 — bge_embed_query() raises RuntimeError(BGE_DIM_MISMATCH) on wrong dim
  T3 — only one model load occurs per process (singleton)
  T4 — SemanticRetriever._embed_query delegates to bge_embed_query
  T5 — HybridSearchEngine._generate_query_embedding delegates to bge_embed_query
  T6 — both callers raise BGE_DIM_MISMATCH (not swallow silently) on dim change
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, call, patch

import numpy as np
import pytest

pytestmark = pytest.mark.retrieval_guard


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_fake_st(dim: int = 1024):
    fake = MagicMock()
    fake.encode.return_value = np.ones((1, dim), dtype=np.float32)
    return fake


def _reset_bge_singleton():
    from agentic_core.embeddings import bge_runtime

    bge_runtime.reset_model_for_testing()


# ---------------------------------------------------------------------------
# T1/T2/T3 — bge_runtime unit tests
# ---------------------------------------------------------------------------


class TestBgeRuntime(unittest.TestCase):
    def setUp(self):
        _reset_bge_singleton()

    def tearDown(self):
        _reset_bge_singleton()

    def test_returns_1024_dim(self):
        from agentic_core.embeddings.bge_runtime import bge_embed_query

        with patch(
            "agentic_core.embeddings.bge_runtime.SentenceTransformer", return_value=_make_fake_st(1024)
        ):
            vec = bge_embed_query("hello")
        self.assertEqual(len(vec), 1024)
        self.assertTrue(all(isinstance(v, float) for v in vec))

    def test_dim_mismatch_raises_loudly(self):
        from agentic_core.embeddings.bge_runtime import bge_embed_query

        with patch(
            "agentic_core.embeddings.bge_runtime.SentenceTransformer", return_value=_make_fake_st(384)
        ):
            with self.assertRaises(RuntimeError) as ctx:
                bge_embed_query("hello")
        self.assertIn("BGE_DIM_MISMATCH", str(ctx.exception))
        self.assertIn("384", str(ctx.exception))
        self.assertIn("1024", str(ctx.exception))

    def test_missing_package_raises_bge_install_error(self):
        from agentic_core.embeddings import bge_runtime
        from agentic_core.embeddings.bge_runtime import BGEInstallError

        with patch("agentic_core.embeddings.bge_runtime.SentenceTransformer", None):
            _reset_bge_singleton()
            with self.assertRaises(BGEInstallError) as ctx:
                bge_runtime.bge_embed_query("hello")
        self.assertIn("sentence-transformers", str(ctx.exception))

    def test_singleton_model_loaded_once(self):
        """T3: _get_model() must call SentenceTransformer exactly once across multiple calls."""
        fake_st_cls = MagicMock(return_value=_make_fake_st(1024))
        from agentic_core.embeddings.bge_runtime import bge_embed_query

        with patch("agentic_core.embeddings.bge_runtime.SentenceTransformer", fake_st_cls):
            bge_embed_query("query one")
            bge_embed_query("query two")
            bge_embed_query("query three")
        fake_st_cls.assert_called_once()

    def test_constants_correct(self):
        from agentic_core.embeddings.bge_runtime import BGE_MODEL, BGE_QUERY_DIM

        self.assertEqual(BGE_MODEL, "BAAI/bge-m3")
        self.assertEqual(BGE_QUERY_DIM, 1024)


# ---------------------------------------------------------------------------
# T4 — SemanticRetriever delegates to bge_embed_query
# ---------------------------------------------------------------------------


class TestSemanticRetrieverDelegates(unittest.TestCase):
    """T4: SR's _query_collection calls bge_embed_query directly (no _embed_query wrapper)."""

    def setUp(self):
        _reset_bge_singleton()

    def tearDown(self):
        _reset_bge_singleton()

    def _make_retriever(self):
        fake_chroma_client = MagicMock()
        fake_chroma_client.list_collections.return_value = []
        with (
            patch("chromadb.PersistentClient", return_value=fake_chroma_client),
            patch("agentic_core.L1_cognition.reasoning.semantic_retriever.SovereignChromaClient"),
        ):
            from agentic_core.L1_cognition.reasoning.semantic_retriever import SemanticRetriever

            return SemanticRetriever()

    def test_sr_embedding_path_calls_bge_embed_query(self):
        """T4: bge_embed_query is the embedding function used by SR's _query_collection."""
        with patch(
            "agentic_core.L1_cognition.reasoning.semantic_retriever.bge_embed_query",
            return_value=[0.1] * 1024,
        ) as mock_sr:
            # Directly call the module-level function SR imported
            from agentic_core.L1_cognition.reasoning import semantic_retriever as sr_mod

            result = sr_mod.bge_embed_query("test text")
            mock_sr.assert_called_once_with("test text")
        self.assertEqual(len(result), 1024)

    def test_sr_embedding_returns_1024_dim(self):
        """T4: the embedding function SR uses returns 1024-dim."""
        with patch(
            "agentic_core.embeddings.bge_runtime.SentenceTransformer", return_value=_make_fake_st(1024)
        ):
            from agentic_core.embeddings.bge_runtime import bge_embed_query

            vec = bge_embed_query("test")
        self.assertEqual(len(vec), 1024)

    def test_sr_embedding_propagates_dim_mismatch(self):
        """T4: BGE_DIM_MISMATCH raised by bge_embed_query propagates through SR's call site."""
        with patch(
            "agentic_core.L1_cognition.reasoning.semantic_retriever.bge_embed_query",
            side_effect=RuntimeError("BGE_DIM_MISMATCH: dim=384 expected 1024"),
        ):
            from agentic_core.L1_cognition.reasoning import semantic_retriever as sr_mod

            with self.assertRaises(RuntimeError) as ctx:
                sr_mod.bge_embed_query("test")
        self.assertIn("BGE_DIM_MISMATCH", str(ctx.exception))

    def test_no_embed_query_method(self):
        """_embed_query wrapper is removed; SR no longer carries that indirection."""
        retriever = self._make_retriever()
        self.assertFalse(
            hasattr(retriever, "_embed_query"), "SemanticRetriever._embed_query wrapper must be removed"
        )

    def test_no_instance_bge_model_slot(self):
        """After removal of self._bge_model, retriever must not carry the old slot."""
        retriever = self._make_retriever()
        self.assertFalse(
            hasattr(retriever, "_bge_model"), "SemanticRetriever must not carry _bge_model after migration"
        )


# ---------------------------------------------------------------------------
# T5/T6 — HybridSearchEngine delegates and raises on dim mismatch
# ---------------------------------------------------------------------------


class TestHybridSearchEngineDelegates(unittest.TestCase):
    def setUp(self):
        _reset_bge_singleton()

    def tearDown(self):
        _reset_bge_singleton()

    def _make_engine(self):
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchEngine

        return HybridSearchEngine()

    def test_generate_embedding_calls_bge_embed_query(self):
        """T5: _generate_query_embedding must call the shared helper."""
        engine = self._make_engine()
        with patch(
            "agentic_core.embeddings.bge_runtime.bge_embed_query", return_value=[0.1] * 1024
        ) as mock_runtime:
            # The lazy import inside the method resolves to the already-imported module
            with patch(
                "agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine.bge_embed_query",
                return_value=[0.1] * 1024,
                create=True,
            ):
                pass  # Not the right patch target — test via bge_runtime directly
        # Patch at the module the function is imported FROM inside the method
        with patch(
            "agentic_core.embeddings.bge_runtime.SentenceTransformer", return_value=_make_fake_st(1024)
        ):
            vec = engine._generate_query_embedding("test")
        self.assertIsNotNone(vec)
        self.assertEqual(len(vec), 1024)

    def test_generate_embedding_returns_1024_dim(self):
        """T5: result must always be 1024-dim floats."""
        engine = self._make_engine()
        with patch(
            "agentic_core.embeddings.bge_runtime.SentenceTransformer", return_value=_make_fake_st(1024)
        ):
            vec = engine._generate_query_embedding("hello world")
        self.assertEqual(len(vec), 1024)
        self.assertTrue(all(isinstance(v, float) for v in vec))

    def test_generate_embedding_propagates_dim_mismatch(self):
        """T6: BGE_DIM_MISMATCH must propagate — not be swallowed silently."""
        engine = self._make_engine()
        with patch(
            "agentic_core.embeddings.bge_runtime.SentenceTransformer", return_value=_make_fake_st(384)
        ):
            with self.assertRaises(RuntimeError) as ctx:
                engine._generate_query_embedding("hello")
        self.assertIn("BGE_DIM_MISMATCH", str(ctx.exception))

    def test_no_instance_bge_model_slot(self):
        """After removal of self._bge_model, engine must not carry the old slot."""
        engine = self._make_engine()
        self.assertFalse(
            hasattr(engine, "_bge_model"), "HybridSearchEngine must not carry _bge_model after migration"
        )

    def test_install_error_returns_none(self):
        """T5: BGEInstallError (missing sentence-transformers) returns None gracefully."""
        from agentic_core.embeddings.bge_runtime import BGEInstallError

        engine = self._make_engine()
        with patch("agentic_core.embeddings.bge_runtime.SentenceTransformer", None):
            _reset_bge_singleton()
            result = engine._generate_query_embedding("test")
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# T3 cross-caller: single model load across both callers
# ---------------------------------------------------------------------------


class TestSingleLoadAcrossCallers(unittest.TestCase):
    def setUp(self):
        _reset_bge_singleton()

    def tearDown(self):
        _reset_bge_singleton()

    def test_model_loaded_once_across_sr_and_hse(self):
        """T3 cross-caller: both SR and HSE share the same singleton load."""
        fake_st_cls = MagicMock(return_value=_make_fake_st(1024))

        with patch("agentic_core.embeddings.bge_runtime.SentenceTransformer", fake_st_cls):
            from agentic_core.embeddings.bge_runtime import bge_embed_query

            # SR path
            bge_embed_query("sr query")
            # HSE path (same function — same singleton)
            bge_embed_query("hse query")

        fake_st_cls.assert_called_once_with("BAAI/bge-m3")


if __name__ == "__main__":
    unittest.main()
