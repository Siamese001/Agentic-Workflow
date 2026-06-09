"""Tests for the apps_qna flat-index to Chroma migration utility."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tools.indexing import migrate_apps_qna_flat_index_to_chroma as mod


def _embedding(seed: float, dims: int = mod.EXPECTED_DIMS) -> list[float]:
    values = [0.0] * dims
    values[0] = seed
    return values


def _vector(row_id: str, *, dims: int = mod.EXPECTED_DIMS) -> dict[str, object]:
    return {
        "id": row_id,
        "embedding": _embedding(1.0, dims=dims),
        "metadata": {
            "card_id": row_id,
            "base_card_type": "runtime_root",
            "archetype": "senior",
            "expected_evidence": ["trace", "decision record"],
        },
    }


def _write_flat_index(index_dir: Path, vectors: list[dict[str, object]]) -> Path:
    index_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "embedder_id": mod.EXPECTED_MODEL,
        "model_version": mod.EXPECTED_MODEL,
        "dims": mod.EXPECTED_DIMS,
        "vector_count": len(vectors),
    }
    meta = dict(manifest)
    index = {
        "index_type": "flat",
        "distance_metric": mod.EXPECTED_DISTANCE,
        "vectors": vectors,
    }
    (index_dir / "index.json").write_text(json.dumps(index), encoding="utf-8")
    (index_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (index_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return index_dir


def test_dry_run_validates_without_creating_chroma_client(tmp_path: Path) -> None:
    index_dir = _write_flat_index(tmp_path / "index", [_vector("card_a"), _vector("card_b")])

    with patch.object(mod.chromadb, "PersistentClient") as client:
        summary = mod.migrate_flat_index_to_chroma(
            index_dir=index_dir,
            persist_dir=tmp_path / "chroma",
            dry_run=True,
        )

    assert summary.dry_run is True
    assert summary.vector_count == 2
    assert summary.dimension == mod.EXPECTED_DIMS
    client.assert_not_called()


def test_migration_upserts_batches_with_contract_metadata(tmp_path: Path) -> None:
    index_dir = _write_flat_index(tmp_path / "index", [_vector("card_a"), _vector("card_b")])
    collection = MagicMock()
    client = MagicMock()
    client.get_or_create_collection.return_value = collection

    with patch.object(mod.chromadb, "PersistentClient", return_value=client) as persistent_client:
        summary = mod.migrate_flat_index_to_chroma(
            index_dir=index_dir,
            persist_dir=tmp_path / "chroma",
            batch_size=1,
        )

    persistent_client.assert_called_once_with(path=str(tmp_path / "chroma"))
    client.get_or_create_collection.assert_called_once()
    collection_metadata = client.get_or_create_collection.call_args.kwargs["metadata"]
    assert collection_metadata["hnsw:space"] == "cosine"
    assert collection_metadata["embedding_model"] == mod.EXPECTED_MODEL
    assert collection_metadata["embedding_dim"] == mod.EXPECTED_DIMS
    assert collection_metadata["source_index_sha256"] == summary.index_sha256
    assert collection.upsert.call_count == 2

    first_upsert = collection.upsert.call_args_list[0].kwargs
    assert first_upsert["ids"] == ["card_a"]
    assert first_upsert["embeddings"][0] == _embedding(1.0)
    assert "runtime_root" in first_upsert["documents"][0]
    metadata = first_upsert["metadatas"][0]
    assert metadata["expected_evidence"] == '["trace", "decision record"]'
    assert metadata["source_index_sha256"] == summary.index_sha256
    assert metadata["embedding_dim"] == mod.EXPECTED_DIMS
    assert metadata["migration_plan"] == "bge-review-apps-qna-c0-chroma-migration-f9a3b2"


def test_reset_ignores_missing_collection_before_upsert(tmp_path: Path) -> None:
    index_dir = _write_flat_index(tmp_path / "index", [_vector("card_a")])
    collection = MagicMock()
    client = MagicMock()
    client.delete_collection.side_effect = mod.chromadb.errors.NotFoundError("Collection does not exist")
    client.get_or_create_collection.return_value = collection

    with patch.object(mod.chromadb, "PersistentClient", return_value=client):
        mod.migrate_flat_index_to_chroma(
            index_dir=index_dir,
            persist_dir=tmp_path / "chroma",
            reset=True,
        )

    client.delete_collection.assert_called_once_with(mod.COLLECTION_NAME)
    collection.upsert.assert_called_once()


def test_reset_reraises_unrelated_delete_failure(tmp_path: Path) -> None:
    index_dir = _write_flat_index(tmp_path / "index", [_vector("card_a")])
    client = MagicMock()
    client.delete_collection.side_effect = RuntimeError("permission denied")

    with patch.object(mod.chromadb, "PersistentClient", return_value=client):
        with pytest.raises(RuntimeError, match="permission denied"):
            mod.migrate_flat_index_to_chroma(
                index_dir=index_dir,
                persist_dir=tmp_path / "chroma",
                reset=True,
            )

    client.get_or_create_collection.assert_not_called()


def test_validation_rejects_duplicate_ids(tmp_path: Path) -> None:
    index_dir = _write_flat_index(tmp_path / "index", [_vector("card_a"), _vector("card_a")])

    with pytest.raises(ValueError, match="duplicate vector id"):
        mod.migrate_flat_index_to_chroma(index_dir=index_dir, persist_dir=tmp_path / "chroma", dry_run=True)


def test_validation_rejects_wrong_embedding_dimension(tmp_path: Path) -> None:
    index_dir = _write_flat_index(tmp_path / "index", [_vector("card_a", dims=2)])

    with pytest.raises(ValueError, match="embedding must be 1024-dim"):
        mod.migrate_flat_index_to_chroma(index_dir=index_dir, persist_dir=tmp_path / "chroma", dry_run=True)


def test_batch_size_must_be_positive(tmp_path: Path) -> None:
    index_dir = _write_flat_index(tmp_path / "index", [_vector("card_a")])

    with pytest.raises(ValueError, match="batch_size must be >= 1"):
        mod.migrate_flat_index_to_chroma(index_dir=index_dir, persist_dir=tmp_path / "chroma", batch_size=0)
