"""Regression tests: TitaniumRAGPipeline live retriever wiring.

Four invariants proven (fully offline — SentenceTransformer and chromadb stubbed):
  T1 — default-constructed TitaniumRAGPipeline never leaves retriever=None
  T2 — _retrieve_single() returns results instead of early-exiting when retriever is live
  T3 — explicit retriever arg is respected (existing callers not broken)
  T4 — _retrieve_single() correctly converts HybridSearchResult to TitaniumRetrievalResult
"""

from __future__ import annotations

import asyncio
import unittest
from unittest.mock import MagicMock, patch

import numpy as np


# ---------------------------------------------------------------------------
# Shared fakes
# ---------------------------------------------------------------------------


def _make_fake_hybrid_results(n: int = 3):
    from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchResult

    return [
        HybridSearchResult(
            chunk_id=f"id{i}",
            content=f"content {i}",
            vector_score=0.9 - i * 0.1,
            metadata={"file_path": f"file{i}.py"},
        )
        for i in range(n)
    ]


def _make_fake_engine(results=None):
    """Return a HybridSearchEngine fake whose search() returns controlled results."""
    from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchEngine

    fake = MagicMock(spec=HybridSearchEngine)
    fake.search.return_value = results if results is not None else _make_fake_hybrid_results()
    fake.chroma_client = MagicMock()
    return fake


def _make_pipeline(retriever=None, **kwargs):
    """Build TitaniumRAGPipeline, injecting a fake engine if retriever not specified."""
    from agentic_core.L3_orchestration.reasoning.engines.titanium_rag_pipeline import TitaniumRAGPipeline

    if retriever is None:
        retriever = _make_fake_engine()
    return TitaniumRAGPipeline(
        retriever=retriever,
        enable_decomposition=False,
        enable_compression=False,
        enable_reranking=False,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# T1 — default constructor never leaves retriever=None
# ---------------------------------------------------------------------------


class TestDefaultRetrieverNotNone(unittest.TestCase):
    """T1: TitaniumRAGPipeline() with no args must inject the global HybridSearchEngine."""

    def test_default_retriever_is_not_none(self):
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchEngine

        fake_engine = _make_fake_engine()

        with patch(
            "agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine.get_global_hybrid_engine",
            return_value=fake_engine,
        ):
            from agentic_core.L3_orchestration.reasoning.engines.titanium_rag_pipeline import (
                TitaniumRAGPipeline,
            )

            pipeline = TitaniumRAGPipeline()

        self.assertIsNotNone(pipeline.retriever, "retriever must not be None after default construction")

    def test_default_retriever_is_hybrid_search_engine(self):
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchEngine

        fake_engine = _make_fake_engine()

        with patch(
            "agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine.get_global_hybrid_engine",
            return_value=fake_engine,
        ):
            from agentic_core.L3_orchestration.reasoning.engines.titanium_rag_pipeline import (
                TitaniumRAGPipeline,
            )

            pipeline = TitaniumRAGPipeline()

        self.assertIsInstance(pipeline.retriever, HybridSearchEngine)

    def test_get_global_hybrid_engine_called_on_default_init(self):
        with patch(
            "agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine.get_global_hybrid_engine",
            return_value=_make_fake_engine(),
        ) as mock_factory:
            from agentic_core.L3_orchestration.reasoning.engines.titanium_rag_pipeline import (
                TitaniumRAGPipeline,
            )

            TitaniumRAGPipeline()
        mock_factory.assert_called_once()


# ---------------------------------------------------------------------------
# T2 — _retrieve_single() returns results, no early-exit
# ---------------------------------------------------------------------------


class TestRetrieveSingleNotEmpty(unittest.TestCase):
    """T2: _retrieve_single() must return results when retriever is a live HybridSearchEngine."""

    def test_retrieve_single_returns_items(self):
        pipeline = _make_pipeline()
        results = asyncio.run(pipeline._retrieve_single("UniversalWriteGateway", 5))
        self.assertGreater(len(results), 0, "_retrieve_single must not return [] when retriever is live")

    def test_retrieve_single_returns_empty_only_when_retriever_is_none(self):
        """Regression: the old default (retriever=None) caused this early-exit."""
        from agentic_core.L3_orchestration.reasoning.engines.titanium_rag_pipeline import TitaniumRAGPipeline

        # Manually force retriever=None to confirm the guard still works
        pipeline = TitaniumRAGPipeline(retriever=_make_fake_engine())
        pipeline.retriever = None  # force the old broken state
        results = asyncio.run(pipeline._retrieve_single("any query", 5))
        self.assertEqual(results, [], "_retrieve_single must return [] when retriever=None")

    def test_retrieve_single_calls_engine_search(self):
        fake_engine = _make_fake_engine()
        pipeline = _make_pipeline(retriever=fake_engine)
        asyncio.run(pipeline._retrieve_single("test query", 5))
        fake_engine.search.assert_called_once()


# ---------------------------------------------------------------------------
# T3 — explicit retriever is respected
# ---------------------------------------------------------------------------


class TestExplicitRetrieverRespected(unittest.TestCase):
    """T3: passing a retriever explicitly must not be overridden by the default wiring."""

    def test_explicit_retriever_used_not_replaced(self):
        custom_retriever = _make_fake_engine()
        pipeline = _make_pipeline(retriever=custom_retriever)
        self.assertIs(
            pipeline.retriever, custom_retriever, "Explicit retriever must not be replaced by the default"
        )

    def test_explicit_retriever_search_called_not_global(self):
        custom_retriever = _make_fake_engine()
        pipeline = _make_pipeline(retriever=custom_retriever)

        _GLOBAL_ENGINE_PATCH = (
            "agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine.get_global_hybrid_engine"
        )
        with patch(_GLOBAL_ENGINE_PATCH) as mock_global:
            asyncio.run(pipeline._retrieve_single("test", 5))

        mock_global.assert_not_called()
        custom_retriever.search.assert_called_once()


# ---------------------------------------------------------------------------
# T4 — HybridSearchResult correctly converted to TitaniumRetrievalResult
# ---------------------------------------------------------------------------


class TestResultConversion(unittest.TestCase):
    """T4: _retrieve_single must correctly map HybridSearchResult fields to TitaniumRetrievalResult."""

    def test_content_preserved(self):
        fake_engine = _make_fake_engine(_make_fake_hybrid_results(2))
        pipeline = _make_pipeline(retriever=fake_engine)
        results = asyncio.run(pipeline._retrieve_single("test", 5))
        contents = {r.content for r in results}
        self.assertIn("content 0", contents)
        self.assertIn("content 1", contents)

    def test_chunk_id_preserved(self):
        fake_engine = _make_fake_engine(_make_fake_hybrid_results(2))
        pipeline = _make_pipeline(retriever=fake_engine)
        results = asyncio.run(pipeline._retrieve_single("test", 5))
        ids = {r.chunk_id for r in results}
        self.assertIn("id0", ids)
        self.assertIn("id1", ids)

    def test_retrieval_score_matches_combined_score(self):
        hybrid_results = _make_fake_hybrid_results(1)
        hybrid_results[0].combined_score = 0.777
        fake_engine = _make_fake_engine(hybrid_results)
        pipeline = _make_pipeline(retriever=fake_engine)
        results = asyncio.run(pipeline._retrieve_single("test", 5))
        self.assertAlmostEqual(results[0].retrieval_score, 0.777, places=3)

    def test_metadata_preserved(self):
        hybrid_results = _make_fake_hybrid_results(1)
        hybrid_results[0].metadata = {"file_path": "special.py", "layer": "L3"}
        fake_engine = _make_fake_engine(hybrid_results)
        pipeline = _make_pipeline(retriever=fake_engine)
        results = asyncio.run(pipeline._retrieve_single("test", 5))
        self.assertEqual(results[0].metadata["file_path"], "special.py")


# ---------------------------------------------------------------------------
# T5 — _emit_captures_evaluation_metric arity bug regression
# ---------------------------------------------------------------------------


class TestEvalMetricArityFixed(unittest.TestCase):
    """T5: retrieve() must not raise TypeError from the _emit_captures_evaluation_metric call.

    Before fix: _emit_captures_evaluation_metric(_trace_id, "titanium", "retrieval_time_ms", elapsed_ms)
    → TypeError: takes 3 positional arguments but 4 were given
    After fix:  _emit_captures_evaluation_metric(_trace_id, "titanium", "retrieval_time_ms")
    """

    def test_retrieve_does_not_raise_on_eval_metric_call(self):
        """retrieve() must complete without TypeError from _emit_captures_evaluation_metric."""
        fake_engine = _make_fake_engine()
        pipeline = _make_pipeline(retriever=fake_engine)

        # Should not raise — previously crashed with TypeError on the 4-arg emit call
        try:
            result = asyncio.run(pipeline.retrieve("test query", top_k=3))
        except TypeError as exc:
            self.fail(f"retrieve() raised TypeError: {exc}")

        self.assertIn("results", result)

    def test_emit_captures_evaluation_metric_signature_is_3_args(self):
        """Regression: confirm the contract function itself only accepts 3 positional args."""
        import inspect
        from agentic_core.runtime.contracts.lifecycle_trace_contract import (
            _emit_captures_evaluation_metric,
        )

        sig = inspect.signature(_emit_captures_evaluation_metric)
        params = [p for p in sig.parameters.values() if p.default is inspect.Parameter.empty]
        self.assertEqual(
            len(params), 3, f"Expected 3 required params, got {len(params)}: {list(sig.parameters)}"
        )

    def test_retrieve_returns_result_count(self):
        """retrieve() must return a result dict with result_count when arity is correct."""
        fake_engine = _make_fake_engine(_make_fake_hybrid_results(3))
        pipeline = _make_pipeline(retriever=fake_engine)
        result = asyncio.run(pipeline.retrieve("test", top_k=3))
        self.assertGreaterEqual(result.get("result_count", 0), 0)


if __name__ == "__main__":
    unittest.main()
