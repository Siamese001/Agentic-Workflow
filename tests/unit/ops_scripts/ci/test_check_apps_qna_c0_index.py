"""Tests for the apps_qna C0 primary Chroma and flat fallback CI gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ops_scripts.ci import check_apps_qna_c0_index as mod


class _FakeCollection:
    metadata = {
        "embedding_model": mod.EXPECTED_MODEL,
        "embedding_dim": mod.EXPECTED_DIMS,
        "hnsw:space": mod.EXPECTED_DISTANCE,
    }

    def count(self) -> int:
        return mod.EXPECTED_VECTOR_COUNT

    def get(self, *, limit: int, include: list[str]) -> dict[str, Any]:  # noqa: ARG002
        return {
            "ids": ["card_a"],
            "metadatas": [{"embedding_model": mod.EXPECTED_MODEL}],
        }


def _write_flat_index(index_dir: Path) -> None:
    index_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": mod.EXPECTED_SCHEMA_VERSION,
        "embedder_id": mod.EXPECTED_MODEL,
        "model_version": mod.EXPECTED_MODEL,
        "dims": mod.EXPECTED_DIMS,
        "vector_count": mod.EXPECTED_VECTOR_COUNT,
    }
    index = {
        "index_type": "flat",
        "distance_metric": mod.EXPECTED_DISTANCE,
        "vectors": [
            {
                "id": "card_a",
                "embedding": [1.0] + [0.0] * (mod.EXPECTED_DIMS - 1),
                "metadata": {"card_id": "card_a"},
            }
        ],
    }
    (index_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (index_dir / "meta.json").write_text(json.dumps(manifest), encoding="utf-8")
    (index_dir / "index.json").write_text(json.dumps(index), encoding="utf-8")


def test_run_all_checks_reports_primary_and_flat_sections(monkeypatch) -> None:
    for name in (
        "check_chroma_persist_dir",
        "check_chroma_collection",
        "check_chroma_metadata",
        "check_chroma_vector_count",
        "check_chroma_sample_get",
        "check_flat_index_exists",
        "check_flat_required_files",
        "check_flat_schema_version",
        "check_flat_embedding_model",
        "check_flat_dimensions",
        "check_flat_vector_count",
        "check_flat_sample_vector",
    ):
        monkeypatch.setattr(mod, name, lambda context: (True, "ok"))

    passed, results = mod.run_all_checks()

    assert passed is True
    assert {result["target"] for result in results} == {"primary_chroma", "flat_fallback"}
    assert len(results) == 12


def test_chroma_collection_checks_validate_contract() -> None:
    context = {"chroma_collection": _FakeCollection()}

    assert mod.check_chroma_metadata(context)[0] is True
    assert mod.check_chroma_vector_count(context)[0] is True
    assert mod.check_chroma_sample_get(context)[0] is True


def test_chroma_metadata_rejects_wrong_dimension() -> None:
    collection = _FakeCollection()
    collection.metadata = dict(collection.metadata, embedding_dim=512)

    passed, message = mod.check_chroma_metadata({"chroma_collection": collection})

    assert passed is False
    assert "Wrong Chroma metadata" in message


def test_flat_fallback_checks_validate_manifest_and_sample(tmp_path: Path, monkeypatch) -> None:
    index_dir = tmp_path / "apps_qna_interview_cards"
    _write_flat_index(index_dir)
    monkeypatch.setattr(mod, "INDEX_DIR", index_dir)
    context: dict[str, Any] = {}

    assert mod.check_flat_index_exists(context)[0] is True
    assert mod.check_flat_required_files(context)[0] is True
    assert mod.check_flat_schema_version(context)[0] is True
    assert mod.check_flat_embedding_model(context)[0] is True
    assert mod.check_flat_dimensions(context)[0] is True
    assert mod.check_flat_vector_count(context)[0] is True
    assert mod.check_flat_sample_vector(context)[0] is True


def test_flat_required_files_reports_missing_manifest(tmp_path: Path, monkeypatch) -> None:
    index_dir = tmp_path / "apps_qna_interview_cards"
    index_dir.mkdir(parents=True)
    monkeypatch.setattr(mod, "INDEX_DIR", index_dir)

    passed, message = mod.check_flat_required_files({})

    assert passed is False
    assert "manifest.json" in message
