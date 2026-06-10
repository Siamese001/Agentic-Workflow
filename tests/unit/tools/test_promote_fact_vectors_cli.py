"""Smoke tests for the fact_vectors staging operator CLI."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from apps_rg.runtime.c0.fact_vector_write_back import STAGING_COLLECTION_NAME

REPO = Path(__file__).resolve().parents[3]
CLI_PATH = REPO / "tools" / "apps_rg" / "promote_fact_vectors.py"


def _load_cli_module():
    spec = importlib.util.spec_from_file_location("promote_fact_vectors_cli", CLI_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _patch_plain_chroma(monkeypatch) -> None:
    import apps_rg.runtime.chroma_precomputed_collection as cpc

    def _plain(client, name, *, metadata=None):
        del metadata
        return client.get_or_create_collection(name=name)

    monkeypatch.setattr(cpc, "get_precomputed_embeddings_collection", _plain)


def test_promote_fact_vectors_cli_list_and_promote(tmp_path, monkeypatch, capsys) -> None:
    import chromadb

    _patch_plain_chroma(monkeypatch)
    cli = _load_cli_module()
    chroma_path = str(tmp_path / "chroma")
    client = chromadb.PersistentClient(path=chroma_path)
    staging = client.get_or_create_collection(name=STAGING_COLLECTION_NAME)
    staging.upsert(
        ids=["apps_rg:fv:cli"],
        embeddings=[[0.1, 0.2, 0.3, 0.4]],
        documents=["grounded cli claim text"],
        metadatas=[
            {
                "write_back_operation": "extract",
                "source_document_id": "cli",
                "source_type": "candidate_fact_ledger",
                "confidence": "HIGH",
                "proof_status": "proof_eligible",
                "authority_class": "PRIMARY",
                "chunk_digest": "digest-cli",
                "run_id": "run-cli",
                "staged_at_utc": "2026-06-10T00:00:00+00:00",
            }
        ],
    )

    assert cli.main(["--chroma-path", chroma_path, "--list"]) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed["status"] == "PASS"
    assert listed["rows"][0]["id"] == "apps_rg:fv:cli"

    assert (
        cli.main(
            [
                "--chroma-path",
                chroma_path,
                "--promote",
                "--ids",
                "apps_rg:fv:cli",
                "--sparse-dir",
                str(tmp_path / "sparse"),
            ]
        )
        == 0
    )
    promoted = json.loads(capsys.readouterr().out)
    assert promoted["status"] == "PASS"
    assert promoted["promoted_count"] == 1
    live = client.get_or_create_collection(name="fact_vectors")
    assert live.get(ids=["apps_rg:fv:cli"])["ids"] == ["apps_rg:fv:cli"]
