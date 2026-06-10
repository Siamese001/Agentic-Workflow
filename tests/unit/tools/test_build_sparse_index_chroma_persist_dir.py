"""Guard build_sparse_index honoring CHROMA_PERSIST_DIR (worktree/relocated-store ingest).

Deterministic, hermetic. The sparse FTS5 sidecars (data/cache/sparse/<collection>.db) are
gitignored runtime data; a git worktree (or a relocated store) has an empty repo-local
data/cache/chromadb. Before this fix the builder could only read the repo-local store, so the
sidecar could never be rebuilt in such an environment and the mandatory C0.2 sparse lane stayed
UNAVAILABLE. The builder now resolves its ChromaDB source via CHROMA_PERSIST_DIR (mirroring
agentic_core.L4_state.config.chroma_paths), so the sidecar can be built against any store.
"""
from __future__ import annotations

import importlib
import json
import os
import sqlite3
from pathlib import Path

import pytest

MOD = "tools.generate.ingestion.build_sparse_index"


@pytest.fixture
def _clean_env():
    saved = os.environ.get("CHROMA_PERSIST_DIR")
    os.environ.pop("CHROMA_PERSIST_DIR", None)
    try:
        yield
    finally:
        if saved is None:
            os.environ.pop("CHROMA_PERSIST_DIR", None)
        else:
            os.environ["CHROMA_PERSIST_DIR"] = saved


def test_default_chroma_path_is_repo_local(_clean_env) -> None:
    mod = importlib.import_module(MOD)
    resolved = mod._resolve_chroma_path()
    assert resolved == (mod.REPO_ROOT / "data" / "cache" / "chromadb")


def test_absolute_chroma_persist_dir_is_honored(_clean_env, tmp_path: Path) -> None:
    target = tmp_path / "external_chroma"
    target.mkdir()
    os.environ["CHROMA_PERSIST_DIR"] = str(target)
    mod = importlib.import_module(MOD)
    assert mod._resolve_chroma_path() == target.resolve()


def test_relative_chroma_persist_dir_is_repo_anchored(_clean_env) -> None:
    os.environ["CHROMA_PERSIST_DIR"] = "data/cache/chromadb_alt"
    mod = importlib.import_module(MOD)
    resolved = mod._resolve_chroma_path()
    assert resolved == (mod.REPO_ROOT / "data" / "cache" / "chromadb_alt").resolve()


def test_sparse_output_stays_repo_local_regardless_of_override(_clean_env, tmp_path: Path) -> None:
    # Reads may be pointed elsewhere, but writes MUST stay where bm25_store reads them
    # (<repo_root>/data/cache/sparse), which has no env override.
    os.environ["CHROMA_PERSIST_DIR"] = str(tmp_path)
    mod = importlib.import_module(MOD)
    assert mod.SPARSE_PATH == (mod.REPO_ROOT / "data" / "cache" / "sparse")


def test_upsert_documents_incrementally_replaces_sparse_rows(tmp_path: Path) -> None:
    mod = importlib.import_module(MOD)

    first = mod.upsert_documents(
        "fact_vectors",
        [
            {
                "id": "apps_rg:fv:f1",
                "document": "alpha grounded claim",
                "metadata": {"tier": "learned"},
            }
        ],
        sparse_dir=tmp_path,
    )
    assert first["upserted_count"] == 1
    assert first["doc_count"] == 1

    db_path = tmp_path / "fact_vectors.db"
    with sqlite3.connect(str(db_path)) as conn:
        assert conn.execute("SELECT id FROM docs_fts WHERE docs_fts MATCH 'alpha'").fetchone()[0] == "apps_rg:fv:f1"
        metadata = conn.execute("SELECT metadata FROM docs WHERE id = ?", ("apps_rg:fv:f1",)).fetchone()[0]
        assert json.loads(metadata)["tier"] == "learned"

    second = mod.upsert_documents(
        "fact_vectors",
        [
            {
                "id": "apps_rg:fv:f1",
                "document": "omega revised claim",
                "metadata": {"tier": "learned", "revision": "2"},
            }
        ],
        sparse_dir=tmp_path,
    )
    assert second["doc_count"] == 1

    with sqlite3.connect(str(db_path)) as conn:
        assert conn.execute("SELECT id FROM docs_fts WHERE docs_fts MATCH 'alpha'").fetchone() is None
        assert conn.execute("SELECT id FROM docs_fts WHERE docs_fts MATCH 'omega'").fetchone()[0] == "apps_rg:fv:f1"
        metadata = conn.execute("SELECT metadata FROM docs WHERE id = ?", ("apps_rg:fv:f1",)).fetchone()[0]
        assert json.loads(metadata)["revision"] == "2"


def test_build_for_collection_clears_sparse_rows_missing_from_chroma(tmp_path: Path) -> None:
    import chromadb

    mod = importlib.import_module(MOD)
    sparse_dir = tmp_path / "sparse"
    mod.upsert_documents(
        "fact_vectors",
        [
            {"id": "stale", "document": "stale content", "metadata": {}},
        ],
        sparse_dir=sparse_dir,
    )

    chroma_path = tmp_path / "chroma"
    client = chromadb.PersistentClient(path=str(chroma_path))
    col = client.get_or_create_collection(name="fact_vectors")
    col.upsert(
        ids=["fresh"],
        embeddings=[[0.1, 0.2, 0.3, 0.4]],
        documents=["fresh content"],
        metadatas=[{"tier": "learned"}],
    )

    stats = mod.build_for_collection(
        "fact_vectors",
        chroma_path=chroma_path,
        sparse_dir=sparse_dir,
    )
    assert stats["doc_count"] == 1

    with sqlite3.connect(str(sparse_dir / "fact_vectors.db")) as conn:
        assert conn.execute("SELECT id FROM docs ORDER BY id").fetchall() == [("fresh",)]
