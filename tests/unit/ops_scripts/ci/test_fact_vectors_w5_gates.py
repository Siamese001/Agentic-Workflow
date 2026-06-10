"""W5 fact_vectors governance gate tests."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from ops_scripts.ci import check_fact_vectors_lane_parity as parity
from ops_scripts.ci import check_fact_vectors_schema_conformance as schema_gate


def test_lane_parity_accepts_matching_counts() -> None:
    ok, detail = parity.evaluate_parity(
        dense_count=3,
        dense_detail="ok",
        sparse_count=3,
        sparse_detail="ok",
    )

    assert ok is True
    assert detail == "dense_count=sparse_count=3"


def test_lane_parity_rejects_mismatched_counts() -> None:
    ok, detail = parity.evaluate_parity(
        dense_count=3,
        dense_detail="ok",
        sparse_count=2,
        sparse_detail="ok",
    )

    assert ok is False
    assert detail == "dense_count=3 sparse_count=2"


def test_sparse_count_reads_docs_table(tmp_path: Path) -> None:
    db_path = tmp_path / "fact_vectors.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("CREATE TABLE docs(id TEXT PRIMARY KEY, document TEXT, metadata TEXT)")
        conn.executemany(
            "INSERT INTO docs(id, document, metadata) VALUES(?, ?, '{}')",
            [("a", "alpha"), ("b", "beta")],
        )

    count, detail = parity._sparse_count(db_path)

    assert count == 2
    assert detail == "ok"


def test_schema_validator_accepts_required_fact_vector_metadata() -> None:
    schema = schema_gate.load_schema(schema_gate.DEFAULT_SCHEMA_PATH)
    metadata = {
        "app": "apps_rg",
        "source_class": "candidate_profile",
        "source_document_id": "fact_001",
        "source_version_hash": "hash_001",
        "ingestion_timestamp": "2026-06-10T00:00:00+00:00",
        "tier": "learned",
        "authority_class": "PRIMARY",
        "write_back_operation": "extract",
        "embedding_dim": 1024,
    }

    assert schema_gate.validate_metadata(metadata, schema) == []


def test_schema_validator_rejects_missing_tier_and_bad_source_class() -> None:
    schema = schema_gate.load_schema(schema_gate.DEFAULT_SCHEMA_PATH)
    metadata = {
        "app": "apps_rg",
        "source_class": "process_docs",
        "source_document_id": "fact_001",
        "source_version_hash": "hash_001",
        "ingestion_timestamp": "2026-06-10T00:00:00+00:00",
    }

    errors = schema_gate.validate_metadata(metadata, schema)

    assert "tier:missing_required" in errors
    assert any(error.startswith("source_class:allowed_values") for error in errors)


def test_w5_fact_vector_gates_registered_in_contract_runner() -> None:
    runner = Path("ops_scripts/ci/run_contract_gates.py").read_text(encoding="utf-8")

    assert "ops_scripts/ci/check_fact_vectors_lane_parity.py" in runner
    assert "ops_scripts/ci/check_fact_vectors_schema_conformance.py" in runner
    assert "CHECK-RG-FV-PARITY" in runner
    assert "CHECK-RG-FV-SCHEMA" in runner
