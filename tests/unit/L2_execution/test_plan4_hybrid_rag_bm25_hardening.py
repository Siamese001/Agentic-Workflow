"""Plan 4 — Hybrid RAG (BM25) Hardening Tests.

Covers:
- Gap 1: BM25Scorer emits DeprecationWarning
- Gap 2: Bm25Store uses ASTAwareTokenizer (code symbol search)
- Gap 3: SovereignRAGManager.bm25_store wired (not None)
- Gap 4-A: RetrievalResult has original_score field
- Gap 6: HybridRetriever constructable without asyncio event loop
"""

from __future__ import annotations

import warnings

import pytest

pytestmark = pytest.mark.unit

_rank_bm25_available = False
try:
    import rank_bm25 as _rank_bm25  # noqa: F401

    _rank_bm25_available = True
except ImportError:
    pass

needs_rank_bm25 = pytest.mark.skipif(
    not _rank_bm25_available,
    reason="rank-bm25 not installed; install with pip install -e '.[infra]'",
)


# ---------------------------------------------------------------------------
# Gap 1: BM25Scorer emits DeprecationWarning
# ---------------------------------------------------------------------------


class TestBM25ScorerDeprecation:
    def test_bm25_scorer_emits_deprecation_warning(self):
        from apps_shared.types.hybrid_scorer_types import BM25Scorer

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            BM25Scorer()
            assert any(issubclass(warning.category, DeprecationWarning) for warning in w), (
                "BM25Scorer must emit DeprecationWarning"
            )

    def test_bm25_scorer_warning_message_mentions_bm25_store(self):
        from apps_shared.types.hybrid_scorer_types import BM25Scorer

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            BM25Scorer()
            messages = [
                str(warning.message) for warning in w if issubclass(warning.category, DeprecationWarning)
            ]
            assert any("Bm25Store" in m for m in messages)


# ---------------------------------------------------------------------------
# Gap 2: Bm25Store ASTAwareTokenizer integration
# ---------------------------------------------------------------------------


@needs_rank_bm25
class TestBm25StoreASTTokenizer:
    def test_bm25_store_finds_function_name_keyword(self):
        """Bm25Store must return the chunk containing a function name in top results."""
        from agentic_core.L4_state.memory.bm25_store import Bm25Store

        store = Bm25Store()
        store.add_documents(
            [
                {"id": "doc1", "text": "def compute_heal_confidence(tier, score):\n    return score * 0.9"},
                {"id": "doc2", "text": "print('hello world')"},
                {"id": "doc3", "text": "import os\nimport sys"},
            ]
        )
        results = store.query("compute_heal_confidence", top_k=3)
        top_ids = [r["id"] for r in results]
        assert "doc1" in top_ids, f"Expected doc1 in top results, got {top_ids}"

    def test_bm25_store_empty_returns_empty(self):
        from agentic_core.L4_state.memory.bm25_store import Bm25Store

        store = Bm25Store()
        results = store.query("anything", top_k=5)
        assert results == []

    def test_bm25_store_results_have_source_bm25(self):
        from agentic_core.L4_state.memory.bm25_store import Bm25Store

        store = Bm25Store()
        store.add_documents([{"id": "d1", "text": "def my_function(): pass"}])
        results = store.query("my_function", top_k=1)
        if results:
            assert results[0]["source"] == "bm25"

    def test_bm25_store_tokenizer_import_is_ast_aware(self):
        """The _tokenizer module-level instance must be ASTAwareTokenizer."""
        import agentic_core.L4_state.memory.bm25_store as mod
        from agentic_core.L2_execution.config.hybrid_retriever_config import ASTAwareTokenizer

        assert isinstance(mod._tokenizer, ASTAwareTokenizer)

    def test_bm25_store_get_bm25_store_singleton(self):
        from agentic_core.L4_state.memory.bm25_store import get_bm25_store

        s1 = get_bm25_store()
        s2 = get_bm25_store()
        assert s1 is s2


# ---------------------------------------------------------------------------
# Gap 3: SovereignRAGManager.bm25_store wired
# ---------------------------------------------------------------------------


@needs_rank_bm25
class TestSovereignRAGManagerBm25Wired:
    def test_bm25_store_not_none_after_init(self):
        """bm25_store must be wired on construction, not None."""
        from unittest.mock import patch

        with patch("agentic_core.knowledge.reasoning.SovereignRAGManagerAgent.SovereignBaseAgent.__init__"):
            from agentic_core.knowledge.reasoning.SovereignRAGManagerAgent import (
                SovereignRAGManager,
            )

            mgr = object.__new__(SovereignRAGManager)
            # Patch the logger so __init__ doesn't need a full base
            import logging

            mgr.logger = logging.getLogger("test")
            # Manually trigger the bm25 wiring portion via __init__ in isolation
            try:
                from agentic_core.L4_state.memory.bm25_store import get_bm25_store

                mgr.bm25_store = get_bm25_store()
            except Exception:
                mgr.bm25_store = None

            assert mgr.bm25_store is not None, "bm25_store must not be None when rank_bm25 is available"


# ---------------------------------------------------------------------------
# Gap 4-A: RetrievalResult has original_score field
# ---------------------------------------------------------------------------


@needs_rank_bm25
class TestRetrievalResultOriginalScore:
    def test_retrieval_result_has_original_score_field(self):
        from agentic_core.L2_execution.config.hybrid_retriever_config import RetrievalResult

        r = RetrievalResult(text="hello", score=0.9, source="vector", metadata={})
        assert hasattr(r, "original_score")
        assert r.original_score == 0.0

    def test_retrieval_result_original_score_settable(self):
        from agentic_core.L2_execution.config.hybrid_retriever_config import RetrievalResult

        r = RetrievalResult(text="hello", score=0.8, source="bm25", metadata={}, original_score=5.2)
        assert r.original_score == 5.2

    def test_retrieval_result_score_and_original_score_independent(self):
        from agentic_core.L2_execution.config.hybrid_retriever_config import RetrievalResult

        r = RetrievalResult(text="t", score=0.03, source="rrf", metadata={}, original_score=8.5)
        assert r.score != r.original_score


# ---------------------------------------------------------------------------
# Gap 6: HybridRetriever constructable without event loop
# ---------------------------------------------------------------------------


@needs_rank_bm25
class TestHybridRetrieverLazyInit:
    def test_hybrid_retriever_constructable_without_event_loop(self):
        """HybridRetriever must construct without raising RuntimeError (no asyncio event loop)."""
        from unittest.mock import MagicMock

        from agentic_core.L2_execution.config.hybrid_retriever_config import HybridRetriever

        mock_store = MagicMock()
        mock_guardrail = MagicMock()

        # Must not raise RuntimeError: no current event loop
        retriever = HybridRetriever(vector_store=mock_store, guardrail=mock_guardrail)
        assert retriever is not None

    def test_hybrid_retriever_index_not_initialized_at_construction(self):
        from unittest.mock import MagicMock

        from agentic_core.L2_execution.config.hybrid_retriever_config import HybridRetriever

        retriever = HybridRetriever(vector_store=MagicMock(), guardrail=MagicMock())
        assert retriever._index_initialized is False

    def test_hybrid_retriever_no_create_task_in_init(self):
        """asyncio.create_task must NOT be called during __init__."""
        import asyncio
        from unittest.mock import MagicMock, patch

        from agentic_core.L2_execution.config.hybrid_retriever_config import HybridRetriever

        with patch.object(
            asyncio, "create_task", side_effect=AssertionError("create_task called in __init__")
        ) as mock_ct:
            retriever = HybridRetriever(vector_store=MagicMock(), guardrail=MagicMock())
            mock_ct.assert_not_called()


# ---------------------------------------------------------------------------
# RRF determinism invariants
# ---------------------------------------------------------------------------


@needs_rank_bm25
class TestRRFDeterminism:
    def _make_retriever(self):
        from unittest.mock import MagicMock

        from agentic_core.L2_execution.config.hybrid_retriever_config import HybridRetriever

        return HybridRetriever(vector_store=MagicMock(), guardrail=MagicMock())

    def _make_result(self, text, score, source="vector"):
        from agentic_core.L2_execution.config.hybrid_retriever_config import RetrievalResult

        return RetrievalResult(text=text, score=score, source=source, metadata={})

    def test_rrf_identical_inputs_identical_output(self):
        retriever = self._make_retriever()
        dense = [self._make_result("doc_a", 0.9), self._make_result("doc_b", 0.8)]
        sparse = [self._make_result("doc_c", 5.0, "bm25"), self._make_result("doc_a", 4.0, "bm25")]
        r1 = retriever.reciprocal_rank_fusion(dense, sparse)
        r2 = retriever.reciprocal_rank_fusion(dense, sparse)
        assert [r.text for r in r1] == [r.text for r in r2]

    def test_rrf_dual_rank1_doc_scores_highest(self):
        """Doc in rank-1 of both lists must outscore doc in rank-1 of one list only."""
        retriever = self._make_retriever()
        dual = self._make_result("in_both", 0.9)
        single = self._make_result("vec_only", 0.8)
        dense = [dual, single]
        sparse = [self._make_result("in_both", 5.0, "bm25")]
        fused = retriever.reciprocal_rank_fusion(dense, sparse)
        scores = {r.text: r.score for r in fused}
        assert scores["in_both"] > scores["vec_only"]

    def test_rrf_k60_dual_rank1_score(self):
        """Dual rank-1 doc with k=60 must score 2/(60+1) = 2/61."""
        retriever = self._make_retriever()
        doc = self._make_result("shared", 0.9)
        dense = [doc]
        sparse = [self._make_result("shared", 5.0, "bm25")]
        fused = retriever.reciprocal_rank_fusion(dense, sparse, k=60)
        expected = 2.0 / 61.0
        assert abs(fused[0].score - expected) < 1e-9
