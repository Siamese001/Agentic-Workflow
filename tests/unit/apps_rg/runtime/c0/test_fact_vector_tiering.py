"""W1 tier metadata tests for c0-grounded-fact-writeback-spine-4f8e2a."""
from __future__ import annotations

from pathlib import Path

import yaml

from apps_rg.runtime.bindings.c0_binding import _metadata_match_for_chunk
from apps_rg.runtime.c0.c02_fact_vector_ingest import chunk_to_chroma_document
from apps_rg.runtime.c0.fact_vector_write_back import (
    PROMOTION_HITL_ENV,
    STAGING_COLLECTION_NAME,
    promote_staged_fact_vectors,
)
from apps_rg.tools.fact_vector_ingest import FactVectorChunk, FactVectorSchema
from ops_scripts.maintenance.backfill_fact_vectors_tier import (
    backfill_collection_tier,
    infer_fact_vector_tier,
)


def _chunk(**overrides: object) -> FactVectorChunk:
    values = {
        "chunk_id": "apps_rg:fv:fact_test_001",
        "content": "Grounded fact text with enough detail for the dense lane.",
        "app": "apps_rg",
        "source_class": "candidate_profile",
        "ingestion_timestamp": "2026-06-10T00:00:00+00:00",
        "source_document_id": "fact_test_001",
        "source_version_hash": "hash_test",
    }
    values.update(overrides)
    return FactVectorChunk(**values)


def test_fact_vectors_schema_v21_declares_tier_and_stamped_fields() -> None:
    schema_path = Path("apps_rg/config/domain_contract/fact_vectors_schema.yaml")
    data = yaml.safe_load(schema_path.read_text(encoding="utf-8"))

    assert data["schema_version"] == "2.1"
    metadata_schema = data["metadata_schema"]
    expected = {
        "tier",
        "candidate_fact_id",
        "confidence",
        "proof_status",
        "source_span_ref",
        "source_type",
        "write_back_operation",
        "promoted_at_utc",
        "promotion_run_id",
        "run_id",
        "staged_at_utc",
        "promotion_hold_reason",
        "x3_code",
    }
    assert expected <= set(metadata_schema)
    assert metadata_schema["tier"]["required"] is True
    assert metadata_schema["tier"]["allowed_values"] == ["seed", "learned"]


def test_fact_vector_chunk_defaults_to_seed_and_validator_enforces_tier() -> None:
    schema = FactVectorSchema()
    chunk = _chunk()
    doc = chunk.to_chroma_document()

    assert doc["metadata"]["tier"] == "seed"
    assert schema.validate_chunk(chunk)[0] is True

    bad = _chunk(tier="unknown")
    valid, errors = schema.validate_chunk(bad)
    assert valid is False
    assert any("tier" in err.lower() for err in errors)


def test_chunk_to_chroma_document_keeps_seed_tier_with_c02_metadata() -> None:
    doc = chunk_to_chroma_document(
        _chunk(),
        {
            "fact_id": "fact_test_001",
            "confidence": "HIGH",
            "proof_status": "proof_eligible",
            "source_span_ref": "ledger:fact_test_001",
            "source_type": "candidate_fact_ledger",
            "write_back_operation": "extract",
        },
    )

    metadata = doc["metadata"]
    assert metadata["tier"] == "seed"
    assert metadata["candidate_fact_id"] == "fact_test_001"
    assert metadata["write_back_operation"] == "extract"


class _FakeCollection:
    def __init__(self, rows: list[tuple[str, dict[str, object]]]) -> None:
        self.rows = {row_id: dict(metadata) for row_id, metadata in rows}

    def count(self) -> int:
        return len(self.rows)

    def get(self, *, include: list[str], limit: int, offset: int) -> dict[str, object]:
        del include
        items = list(self.rows.items())[offset : offset + limit]
        return {
            "ids": [row_id for row_id, _metadata in items],
            "metadatas": [metadata for _row_id, metadata in items],
        }

    def update(self, *, ids: list[str], metadatas: list[dict[str, object]]) -> None:
        for row_id, metadata in zip(ids, metadatas, strict=True):
            self.rows[row_id] = dict(metadata)


def test_backfill_infers_learned_from_write_back_operation_and_seed_otherwise() -> None:
    assert infer_fact_vector_tier({"write_back_operation": "extract"}) == "learned"
    assert infer_fact_vector_tier({}) == "seed"

    collection = _FakeCollection(
        [
            ("seed_missing", {"app": "apps_rg"}),
            ("learned_missing", {"app": "apps_rg", "write_back_operation": "extract"}),
            ("already_seed", {"app": "apps_rg", "tier": "seed"}),
        ]
    )

    dry = backfill_collection_tier(collection, execute=False, page_size=2)
    assert dry["status"] == "DRY_RUN"
    assert dry["untagged_before"] == 2
    assert dry["untagged_after"] == 2
    assert collection.rows["seed_missing"].get("tier") is None

    receipt = backfill_collection_tier(collection, execute=True, page_size=2)
    assert receipt["status"] == "PASS"
    assert receipt["updated_count"] == 2
    assert receipt["untagged_after"] == 0
    assert collection.rows["seed_missing"]["tier"] == "seed"
    assert collection.rows["learned_missing"]["tier"] == "learned"


def test_metadata_tier_does_not_change_c2_metadata_fit_score() -> None:
    app_payload = {"jd_payload": {"target_company": "Blend360"}}
    base = {"company": "Blend360", "source_class": "candidate_profile"}
    with_tier = {**base, "tier": "learned"}

    assert _metadata_match_for_chunk(base, app_payload) == 1.0
    assert _metadata_match_for_chunk(with_tier, app_payload) == 1.0


def test_promotion_stamps_live_rows_as_learned(tmp_path, monkeypatch) -> None:
    import chromadb

    import apps_rg.runtime.chroma_precomputed_collection as cpc

    monkeypatch.delenv(PROMOTION_HITL_ENV, raising=False)

    def _plain(client, name, *, metadata=None):
        del metadata
        return client.get_or_create_collection(name=name)

    monkeypatch.setattr(cpc, "get_precomputed_embeddings_collection", _plain)

    chroma_path = str(tmp_path / "chroma")
    client = chromadb.PersistentClient(path=chroma_path)
    staging = client.get_or_create_collection(name=STAGING_COLLECTION_NAME)
    staging.upsert(
        ids=["apps_rg:fv:f1"],
        embeddings=[[0.1, 0.2, 0.3, 0.4]],
        documents=["grounded claim text"],
        metadatas=[
            {
                "tier": "seed",
                "write_back_operation": "extract",
                "source_document_id": "f1",
                "source_type": "candidate_fact_ledger",
                "confidence": "HIGH",
                "proof_status": "proof_eligible",
                "authority_class": "PRIMARY",
                "chunk_digest": "digest-f1",
            }
        ],
    )

    receipt = promote_staged_fact_vectors(
        chroma_path=chroma_path,
        promotion_run_id="test-promotion-run",
        sparse_dir=tmp_path / "sparse",
    )

    assert receipt["status"] == "PASS"
    assert receipt["promotion_run_id"] == "test-promotion-run"
    live = client.get_or_create_collection(name="fact_vectors")
    metadata = live.get(ids=["apps_rg:fv:f1"], include=["metadatas"])["metadatas"][0]
    assert metadata["tier"] == "learned"
    assert metadata["promotion_run_id"] == "test-promotion-run"
    assert metadata["promoted_at_utc"]
