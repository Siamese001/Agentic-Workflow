from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def test_bootstrap_fast_skips_when_dense_and_sparse_ready(monkeypatch, tmp_path: Path) -> None:
    from tools.apps_rg import bootstrap_fact_vectors as mod

    def fail_dense(*_args, **_kwargs):
        raise AssertionError("dense build should not run")

    def fail_sparse(*_args, **_kwargs):
        raise AssertionError("sparse build should not run")

    monkeypatch.setattr(mod, "dense_count", lambda *_args, **_kwargs: 12)
    monkeypatch.setattr(mod, "sparse_doc_count", lambda *_args, **_kwargs: 12)
    monkeypatch.setattr(mod, "_run_dense_build", fail_dense)
    monkeypatch.setattr(mod, "_run_sparse_build", fail_sparse)

    receipt_path = tmp_path / "receipt.json"
    receipt = mod.bootstrap(chroma_path=tmp_path / "chroma", receipt_path=receipt_path)

    assert receipt["status"] == "skipped_ready"
    assert receipt["dense_built"] is False
    assert receipt["sparse_built"] is False
    assert json.loads(receipt_path.read_text(encoding="utf-8"))["status"] == "skipped_ready"


def test_bootstrap_builds_sparse_only_when_dense_exists(monkeypatch, tmp_path: Path) -> None:
    from tools.apps_rg import bootstrap_fact_vectors as mod

    state = {"sparse_docs": 0, "dense_calls": 0, "sparse_calls": 0}

    def fake_dense_count(*_args, **_kwargs) -> int:
        return 18

    def fake_sparse_doc_count(*_args, **_kwargs) -> int:
        return state["sparse_docs"]

    def fake_dense_build(*_args, **_kwargs) -> int:
        state["dense_calls"] += 1
        return 0

    def fake_sparse_build(*_args, **_kwargs) -> dict[str, int]:
        state["sparse_calls"] += 1
        state["sparse_docs"] = 18
        return {"doc_count": 18, "term_count": 42}

    monkeypatch.setattr(mod, "dense_count", fake_dense_count)
    monkeypatch.setattr(mod, "sparse_doc_count", fake_sparse_doc_count)
    monkeypatch.setattr(mod, "_run_dense_build", fake_dense_build)
    monkeypatch.setattr(mod, "_run_sparse_build", fake_sparse_build)

    receipt = mod.bootstrap(chroma_path=tmp_path / "chroma", receipt_path=tmp_path / "receipt.json")

    assert receipt["status"] == "ready"
    assert receipt["dense_built"] is False
    assert receipt["sparse_built"] is True
    assert state["dense_calls"] == 0
    assert state["sparse_calls"] == 1


def test_seed_rg_fv_delegates_to_bootstrap(monkeypatch, tmp_path: Path) -> None:
    from ops_scripts.ci import seed_apps_rg_fact_vectors_chroma as seed
    from tools.apps_rg import bootstrap_fact_vectors

    seen: dict[str, object] = {}

    def fake_bootstrap(*, chroma_path: Path, force: bool = False):
        seen["chroma_path"] = chroma_path
        seen["force"] = force
        return {
            "status": "ready",
            "dense_count_after": 3,
            "sparse_doc_count_after": 3,
        }

    monkeypatch.delenv("APPS_RG_SEED_FACT_VECTORS_BYPASS", raising=False)
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "external_chroma"))
    monkeypatch.setattr(bootstrap_fact_vectors, "bootstrap", fake_bootstrap)

    assert seed.main(["--force"]) == 0
    assert seen == {"chroma_path": tmp_path / "external_chroma", "force": True}


def test_sparse_readiness_counts_docs(tmp_path: Path) -> None:
    from ops_scripts.ci.check_apps_rg_fact_vectors_readiness import _sparse_doc_count

    db_path = tmp_path / "fact_vectors.db"
    assert _sparse_doc_count(db_path) == 0

    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("CREATE TABLE docs(id TEXT PRIMARY KEY, document TEXT, metadata TEXT)")
        conn.executemany(
            "INSERT INTO docs(id, document, metadata) VALUES(?, ?, ?)",
            [("a", "one", "{}"), ("b", "two", "{}")],
        )
        conn.commit()

    assert _sparse_doc_count(db_path) == 2
