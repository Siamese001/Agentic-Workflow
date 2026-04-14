"""Regression tests: SemanticRetriever BGE alignment.

Core invariants proven:
  T1 — collection routing targets BGE collections, not repo_* 384-dim collections
  T2 — bge_embed_query returns exactly 1024-dim float vectors
  T3 — stored-dim mismatch raises BGE_DIM_MISMATCH RuntimeError
  T4 — _query_collection never calls SovereignChromaClient.embed_texts()
  T5 — query contracts and hit normalization stay deterministic offline

All tests are fully offline: SentenceTransformer is stubbed with a controlled fake.
No live Chroma store or GPU required.
"""

from __future__ import annotations

import asyncio
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

pytestmark = pytest.mark.retrieval_guard


# ---------------------------------------------------------------------------
# Shared fakes
# ---------------------------------------------------------------------------


def _make_fake_st(dim: int):
    """Return a SentenceTransformer-shaped fake that produces `dim`-dim vectors."""
    fake = MagicMock()
    fake.encode.return_value = np.ones((1, dim), dtype=np.float32)
    return fake


def _make_named_collection(name: str):
    col = MagicMock()
    col.name = name
    return col


def _make_fake_chroma_client(
    collection_dim: int | None = 1024,
    query_payload: dict[str, object] | None = None,
):
    """Return a chromadb.PersistentClient fake with one collection of given dim."""
    fake_col = MagicMock()

    if collection_dim is not None:
        stored = np.ones((1, collection_dim), dtype=np.float32)
        fake_col.get.return_value = {"embeddings": stored}
    else:
        fake_col.get.return_value = {"embeddings": None}

    fake_col.query.return_value = query_payload or {
        "ids": [["id1"]],
        "documents": [["doc content"]],
        "metadatas": [[{"file_path": "x.py"}]],
        "distances": [[0.1]],
    }

    fake_client = MagicMock()
    fake_client.list_collections.return_value = [
        _make_named_collection("code_chunks"),
        _make_named_collection("docs"),
    ]
    fake_client.get_collection.return_value = fake_col
    return fake_client, fake_col


# ---------------------------------------------------------------------------
# Helper: build a SemanticRetriever with all I/O stubbed out
# ---------------------------------------------------------------------------


def _build_retriever(
    st_dim: int = 1024,
    chroma_stored_dim: int | None = 1024,
    query_payload: dict[str, object] | None = None,
):
    """Return (retriever, fake_chroma_col, fake_sovereign_chroma) tuple."""
    from agentic_core.L1_cognition.reasoning.semantic_retriever import SemanticRetriever

    fake_bge_client, fake_col = _make_fake_chroma_client(chroma_stored_dim, query_payload)
    fake_sovereign = MagicMock()
    fake_sovereign.list_collections.return_value = ["code_chunks", "docs"]

    with (
        patch("chromadb.PersistentClient", return_value=fake_bge_client),
        patch("client.chroma_client.SovereignChromaClient", return_value=fake_sovereign),
    ):
        retriever = SemanticRetriever(chroma_persist_dir="/fake/path")

    retriever._bge_model = _make_fake_st(st_dim)
    return retriever, fake_col, fake_sovereign


class TestCollectionRouting(unittest.TestCase):
    """T1: routing table must not reference any repo_* 384-dim collection."""

    _FORBIDDEN = {
        "repo_code_chunks",
        "repo_symbols",
        "repo_arch_docs",
        "repo_adg_graph",
        "repo_incidents_rca",
        "repo_runtime_evidence",
        "repo_tests_guardrails",
    }

    def setUp(self):
        self.retriever, _, _ = _build_retriever()

    def test_no_repo_star_collections_in_routing(self):
        all_targets: set[str] = set()
        for targets in self.retriever.collection_routing.values():
            all_targets.update(targets)
        forbidden_found = all_targets & self._FORBIDDEN
        self.assertSetEqual(
            forbidden_found,
            set(),
            f"Routing still references 384-dim repo_* collections: {forbidden_found}",
        )

    def test_code_chunks_in_code_and_general_routes(self):
        code_routes = {"code_questions", "implementation", "general", "architecture"}
        for key in code_routes:
            targets = self.retriever.collection_routing[key]
            self.assertIn(
                "code_chunks",
                targets,
                f"routing['{key}'] does not include 'code_chunks': {targets}",
            )

    def test_general_route_contains_docs(self):
        self.assertIn("docs", self.retriever.collection_routing["general"])

    def test_documentation_route_contains_docs(self):
        self.assertIn("docs", self.retriever.collection_routing["documentation"])


class TestEmbedQueryDimension(unittest.TestCase):
    """T2: bge_embed_query must always return 1024 dims."""

    def test_embed_query_returns_1024_dim(self):
        with patch(
            "agentic_core.embeddings.bge_runtime.SentenceTransformer",
            return_value=_make_fake_st(1024),
        ):
            from agentic_core.embeddings import bge_runtime

            bge_runtime._bge_model = None
            from agentic_core.embeddings.bge_runtime import bge_embed_query

            vec = bge_embed_query("what does UniversalWriteGateway do?")
        self.assertEqual(len(vec), 1024, f"Expected 1024-dim, got {len(vec)}")

    def test_embed_query_returns_floats(self):
        with patch(
            "agentic_core.embeddings.bge_runtime.SentenceTransformer",
            return_value=_make_fake_st(1024),
        ):
            from agentic_core.embeddings import bge_runtime

            bge_runtime._bge_model = None
            from agentic_core.embeddings.bge_runtime import bge_embed_query

            vec = bge_embed_query("test query")
        self.assertTrue(
            all(isinstance(v, float) for v in vec),
            "All embedding values must be Python floats",
        )

    def test_embed_query_raises_on_wrong_model_dim(self):
        with patch(
            "agentic_core.embeddings.bge_runtime.SentenceTransformer",
            return_value=_make_fake_st(384),
        ):
            from agentic_core.embeddings import bge_runtime

            bge_runtime._bge_model = None
            from agentic_core.embeddings.bge_runtime import bge_embed_query

            with self.assertRaises(RuntimeError) as ctx:
                bge_embed_query("any text")
        self.assertIn("BGE_DIM_MISMATCH", str(ctx.exception))
        self.assertIn("dim=384", str(ctx.exception))
        self.assertIn("expected 1024", str(ctx.exception))


class TestStoredDimGuard(unittest.TestCase):
    """T3: _query_collection must raise RuntimeError when stored dim != 1024."""

    def _run(self, coro):
        return asyncio.run(coro)

    def test_384_stored_dim_raises_bge_dim_mismatch(self):
        from agentic_core.L1_cognition.reasoning.semantic_retriever import RetrievalQuery

        retriever, _, _ = _build_retriever(st_dim=1024, chroma_stored_dim=384)
        query = RetrievalQuery(text="test", collections=["code_chunks"], max_results=3)

        with self.assertRaises(RuntimeError) as ctx:
            self._run(retriever._query_collection("code_chunks", query))

        error_msg = str(ctx.exception)
        self.assertIn("BGE_DIM_MISMATCH", error_msg)
        self.assertIn("stored dim=384", error_msg)
        self.assertIn("vs query dim=1024", error_msg)

    def test_1024_stored_dim_does_not_raise(self):
        from agentic_core.L1_cognition.reasoning.semantic_retriever import RetrievalQuery

        retriever, _, _ = _build_retriever(st_dim=1024, chroma_stored_dim=1024)
        query = RetrievalQuery(text="test", collections=["code_chunks"], max_results=3)

        try:
            self._run(retriever._query_collection("code_chunks", query))
        except RuntimeError as exc:
            self.fail(f"Unexpected RuntimeError for matching dims: {exc}")

    def test_none_stored_embeddings_skips_guard(self):
        from agentic_core.L1_cognition.reasoning.semantic_retriever import RetrievalQuery

        retriever, _, _ = _build_retriever(st_dim=1024, chroma_stored_dim=None)
        query = RetrievalQuery(text="test", collections=["code_chunks"], max_results=3)

        try:
            self._run(retriever._query_collection("code_chunks", query))
        except RuntimeError as exc:
            self.fail(f"Unexpected RuntimeError when embeddings=None: {exc}")


class TestNoSovereignEmbedTexts(unittest.TestCase):
    """T4: the semantic query path must never invoke SovereignChromaClient.embed_texts()."""

    def _run(self, coro):
        return asyncio.run(coro)

    def test_embed_texts_not_called_during_query(self):
        from agentic_core.L1_cognition.reasoning.semantic_retriever import RetrievalQuery

        retriever, _, fake_sovereign = _build_retriever(st_dim=1024, chroma_stored_dim=1024)
        query = RetrievalQuery(text="UniversalWriteGateway", collections=["code_chunks"], max_results=3)

        self._run(retriever._query_collection("code_chunks", query))
        fake_sovereign.embed_texts.assert_not_called()

    def test_sovereign_query_not_called_during_retrieval(self):
        from agentic_core.L1_cognition.reasoning.semantic_retriever import RetrievalQuery

        retriever, _, fake_sovereign = _build_retriever(st_dim=1024, chroma_stored_dim=1024)
        query = RetrievalQuery(text="test", collections=["code_chunks"], max_results=3)

        self._run(retriever._query_collection("code_chunks", query))
        fake_sovereign.query.assert_not_called()


class TestQueryContractAndNormalization(unittest.TestCase):
    """T5: request validation and hit normalization remain stable."""

    def _run(self, coro):
        return asyncio.run(coro)

    def test_query_contract_rejects_blank_text(self):
        from agentic_core.L1_cognition.reasoning.semantic_retriever import RetrievalQuery

        with self.assertRaises(ValueError):
            RetrievalQuery(text="   ", collections=["code_chunks"], max_results=1).validate()

    def test_query_contract_rejects_duplicate_collections(self):
        from agentic_core.L1_cognition.reasoning.semantic_retriever import RetrievalQuery

        with self.assertRaises(ValueError):
            RetrievalQuery(
                text="test",
                collections=["code_chunks", "code_chunks"],
                max_results=1,
            ).validate()

    def test_query_contract_rejects_non_positive_max_results(self):
        from agentic_core.L1_cognition.reasoning.semantic_retriever import RetrievalQuery

        with self.assertRaises(ValueError):
            RetrievalQuery(text="test", collections=["code_chunks"], max_results=0).validate()

    def test_query_collection_requires_mapping_payload(self):
        from agentic_core.L1_cognition.reasoning.semantic_retriever import RetrievalQuery

        retriever, fake_col, _ = _build_retriever(st_dim=1024, chroma_stored_dim=1024)
        fake_col.query.return_value = ["not", "a", "mapping"]
        query = RetrievalQuery(text="test", collections=["code_chunks"], max_results=3)

        with self.assertRaises(RuntimeError) as ctx:
            self._run(retriever._query_collection("code_chunks", query))
        self.assertIn("mapping payload", str(ctx.exception))

    def test_normalization_handles_missing_documents_metadata_and_distances(self):
        from agentic_core.L1_cognition.reasoning.semantic_retriever import RetrievalQuery

        payload = {
            "ids": [["id1", "id2"]],
            "documents": [["doc content"]],
            "metadatas": [[{"file_path": "x.py"}, None]],
            "distances": [[0.1]],
        }
        retriever, _, _ = _build_retriever(
            st_dim=1024,
            chroma_stored_dim=1024,
            query_payload=payload,
        )
        query = RetrievalQuery(text="test", collections=["code_chunks"], max_results=3)

        results = self._run(retriever._query_collection("code_chunks", query))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].document, "doc content")
        self.assertEqual(results[0].metadata, {"file_path": "x.py"})
        self.assertEqual(results[0].distance, 0.1)
        self.assertEqual(results[1].document, "")
        self.assertEqual(results[1].metadata, {})
        self.assertIsNone(results[1].distance)


if __name__ == "__main__":
    unittest.main()
