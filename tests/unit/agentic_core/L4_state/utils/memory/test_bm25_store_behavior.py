"""Behavioral tests for ``agentic_core.L4_state.utils.memory.bm25_store``.

Covers:
- Bm25Store: add_documents + query roundtrip; empty store returns [];
  zero-score hits are filtered; top_k bounds the result size.
- get_bm25_store returns the module singleton.
- _tokenize_sparse: stopwords removed, camel/snake split, tokens lowercased,
  dedup preserved in order, short-token filter.
- SparseIndex: unavailable (missing db) returns []; available returns FTS5 hits
  with 1/(1+rank) scoring and parsed metadata.
- get_sparse_index: None for unsupported collections; singleton per supported name.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from agentic_core.L4_state.utils.memory import bm25_store as mod
from agentic_core.L4_state.utils.memory.bm25_store import (
    Bm25Store,
    SparseIndex,
    _tokenize_sparse,
    get_bm25_store,
    get_sparse_index,
)


# ---- Bm25Store in-memory index ------------------------------------------


class TestBm25Store:
    def test_empty_store_returns_empty(self) -> None:
        store = Bm25Store()
        assert store.query("anything") == []

    def test_add_and_query_returns_results(self) -> None:
        store = Bm25Store()
        store.add_documents(
            [
                {"id": "a", "text": "alpha beta gamma"},
                {"id": "b", "text": "delta epsilon zeta"},
                {"id": "c", "text": "alpha delta"},
            ]
        )
        results = store.query("alpha", top_k=5)
        ids = {r["id"] for r in results}
        assert "a" in ids or "c" in ids
        for r in results:
            assert r["source"] == "bm25"
            assert "content" in r
            assert "score" in r
            assert r["score"] > 0  # zero-score entries filtered

    def test_top_k_bounds_results(self) -> None:
        store = Bm25Store()
        store.add_documents([{"id": f"d{i}", "text": f"token_{i} alpha"} for i in range(10)])
        results = store.query("alpha", top_k=3)
        assert len(results) <= 3

    def test_metadata_passthrough(self) -> None:
        store = Bm25Store()
        store.add_documents(
            [
                {"id": "a", "text": "keyword content", "metadata": {"tag": "x"}},
            ]
        )
        results = store.query("keyword")
        assert results[0]["metadata"] == {"tag": "x"}

    def test_metadata_default_empty(self) -> None:
        store = Bm25Store()
        store.add_documents([{"id": "a", "text": "keyword content"}])
        results = store.query("keyword")
        assert results[0]["metadata"] == {}


class TestSingleton:
    def test_get_bm25_store_returns_singleton(self) -> None:
        s1 = get_bm25_store()
        s2 = get_bm25_store()
        assert s1 is s2
        assert isinstance(s1, Bm25Store)


# ---- _tokenize_sparse ----------------------------------------------------


class TestTokenizeSparse:
    def test_lowercases(self) -> None:
        assert "foobar" in _tokenize_sparse("FOOBAR")

    def test_removes_stopwords(self) -> None:
        tokens = _tokenize_sparse("the quick and brown fox")
        assert "the" not in tokens
        assert "and" not in tokens
        assert "brown" in tokens
        assert "fox" in tokens

    def test_filters_single_char(self) -> None:
        tokens = _tokenize_sparse("a b cd")
        assert "a" not in tokens
        assert "b" not in tokens
        assert "cd" in tokens

    def test_dedupes_preserving_order(self) -> None:
        tokens = _tokenize_sparse("alpha beta alpha gamma beta")
        # Each appears once, in first-seen order
        assert tokens.count("alpha") == 1
        assert tokens.count("beta") == 1
        assert tokens.index("alpha") < tokens.index("beta") < tokens.index("gamma")

    def test_snake_case_split(self) -> None:
        tokens = _tokenize_sparse("my_variable_name")
        assert "my_variable_name" in tokens  # full token
        assert "variable" in tokens  # subtoken
        assert "name" in tokens

    def test_camel_case_lowercased_full_token(self) -> None:
        # Implementation lowercases before applying camel regex, so MyVariableName
        # collapses to a single lowercased token (no camel-subtoken split at runtime).
        tokens = _tokenize_sparse("MyVariableName")
        assert "myvariablename" in tokens

    def test_non_alphanumeric_split(self) -> None:
        tokens = _tokenize_sparse("foo.bar/baz")
        assert "foo" in tokens
        assert "bar" in tokens
        assert "baz" in tokens

    def test_empty_input(self) -> None:
        assert _tokenize_sparse("") == []
        assert _tokenize_sparse("the a an of") == []  # all stopwords


# ---- SparseIndex ---------------------------------------------------------


def _build_fts_db(path: Path) -> None:
    """Create an FTS5 sidecar matching SparseIndex's expected schema."""
    conn = sqlite3.connect(str(path))
    conn.executescript("""
        CREATE VIRTUAL TABLE docs_fts USING fts5(id UNINDEXED, document);
        CREATE TABLE docs (id TEXT PRIMARY KEY, metadata TEXT);
    """)
    conn.execute("INSERT INTO docs_fts(id, document) VALUES (?, ?)", ("doc1", "alpha beta gamma"))
    conn.execute("INSERT INTO docs_fts(id, document) VALUES (?, ?)", ("doc2", "delta epsilon"))
    conn.execute("INSERT INTO docs(id, metadata) VALUES (?, ?)", ("doc1", json.dumps({"tag": "x"})))
    conn.execute("INSERT INTO docs(id, metadata) VALUES (?, ?)", ("doc2", json.dumps({"tag": "y"})))
    conn.commit()
    conn.close()


class TestSparseIndex:
    def test_unavailable_when_db_missing(self, tmp_path: Path) -> None:
        with patch.object(mod, "_SPARSE_DIR", tmp_path):
            idx = SparseIndex("code_chunks")
        assert idx.is_available is False
        assert idx.search("anything") == []

    def test_empty_tokens_returns_empty(self, tmp_path: Path) -> None:
        _build_fts_db(tmp_path / "code_chunks.db")
        with patch.object(mod, "_SPARSE_DIR", tmp_path):
            idx = SparseIndex("code_chunks")
        # All stopwords → no tokens
        assert idx.search("the a an") == []

    def test_search_returns_matches_with_scoring(self, tmp_path: Path) -> None:
        _build_fts_db(tmp_path / "code_chunks.db")
        with patch.object(mod, "_SPARSE_DIR", tmp_path):
            idx = SparseIndex("code_chunks")
        results = idx.search("alpha", top_k=10)
        assert len(results) >= 1
        r = results[0]
        assert r["id"] == "doc1"
        assert r["source"] == "sparse_fts"
        assert r["score"] == 1.0  # rank 0 → 1/(1+0) = 1.0
        assert r["metadata"] == {"tag": "x"}
        assert "alpha" in r["content"]

    def test_top_k_bounds_results(self, tmp_path: Path) -> None:
        _build_fts_db(tmp_path / "code_chunks.db")
        with patch.object(mod, "_SPARSE_DIR", tmp_path):
            idx = SparseIndex("code_chunks")
        # Both rows in DB; top_k=1 must limit
        results = idx.search("alpha OR delta", top_k=1)
        assert len(results) <= 1

    def test_malformed_metadata_yields_empty_dict(self, tmp_path: Path) -> None:
        db = tmp_path / "code_chunks.db"
        _build_fts_db(db)
        conn = sqlite3.connect(str(db))
        conn.execute("UPDATE docs SET metadata=? WHERE id=?", ("not-json{", "doc1"))
        conn.commit()
        conn.close()
        with patch.object(mod, "_SPARSE_DIR", tmp_path):
            idx = SparseIndex("code_chunks")
        results = idx.search("alpha")
        assert results[0]["metadata"] == {}


# ---- get_sparse_index ----------------------------------------------------


class TestGetSparseIndex:
    def setup_method(self) -> None:
        mod._sparse_index_cache.clear()

    def teardown_method(self) -> None:
        mod._sparse_index_cache.clear()

    def test_unsupported_collection_returns_none(self) -> None:
        assert get_sparse_index("nonexistent_collection") is None

    @pytest.mark.parametrize(
        "name",
        [
            "code_chunks",
            "symbols",
            "arch_docs",
            "tests_guardrails",
            "runtime_evidence",
            "process_docs",
            "ext_knowledge",
            "incidents_rca",
        ],
    )
    def test_supported_collections_return_instance(self, name: str) -> None:
        idx = get_sparse_index(name)
        assert isinstance(idx, SparseIndex)
        assert idx.collection_name == name

    def test_caching_returns_same_instance(self) -> None:
        idx1 = get_sparse_index("code_chunks")
        idx2 = get_sparse_index("code_chunks")
        assert idx1 is idx2
