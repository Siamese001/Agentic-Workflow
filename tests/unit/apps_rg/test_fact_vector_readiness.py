from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from apps_rg.runtime import fact_vector_readiness as fvr


def _write_manifest(root: Path, *, stale: bool = False) -> None:
    path = root / fvr.MANIFEST_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    required_lanes = [] if stale else list(fvr.GENERATED_LANES)
    locked_lanes = ["ey_bullets"] if stale else []
    path.write_text(
        json.dumps(
            {
                "schema_version": "apps_rg.fact_vectors_bootstrap_manifest.v1",
                "generated_at_utc": "2026-06-24T00:00:00Z",
                "source": (
                    "candidate_fact_ledger + base_resume_employment_bullets "
                    "(tracked first-principles sources)"
                ),
                "dry_run": False,
                "required_lanes": required_lanes,
                "missing_required_lane_targets": [],
                "locked_deterministic_lanes": locked_lanes,
                "per_section_target_counts": {lane: 1 for lane in fvr.GENERATED_LANES},
                "upserted_count": 42,
                "collection_count_after": 42,
                "sparse_sidecar_built": True,
                "manifest_checksum": "b" * 64,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _meta(section: str, source_document_id: str) -> dict[str, Any]:
    return {
        "section_targets": section,
        "source_document_id": source_document_id,
        "source_class": "project_evidence",
        "tier": "seed",
        "embedding_model_id": fvr.BGE_M3_MODEL_ID,
        "embedding_dim": fvr.EXPECTED_BGE_DIMENSION,
    }


def _all_lane_metas() -> list[dict[str, Any]]:
    metas: list[dict[str, Any]] = []
    for lane in fvr.GENERATED_LANES:
        prefix, min_count = fvr.SECTION_SOURCE_SLOT_MIN_COUNTS.get(lane, (f"fact_{lane}_", 1))
        for idx in range(1, max(min_count, 1) + 1):
            metas.append(_meta(lane, f"{prefix}{idx:03d}"))
    return metas


def _direct_vector_metas() -> list[dict[str, Any]]:
    metas: list[dict[str, Any]] = []
    for lane in fvr.DIRECT_VECTOR_LANES:
        prefix, min_count = fvr.SECTION_SOURCE_SLOT_MIN_COUNTS.get(lane, (f"fact_{lane}_", 1))
        for idx in range(1, max(min_count, 1) + 1):
            metas.append(_meta(lane, f"{prefix}{idx:03d}"))
    return metas


def _write_chroma_sqlite(path: Path, metas: list[dict[str, Any]], *, dimension: int = 1024) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path))
    try:
        con.executescript(
            """
            create table collections(
              id text primary key,
              name text not null,
              dimension integer,
              database_id text not null,
              config_json_str text,
              schema_str text
            );
            create table segments(
              id text primary key,
              type text not null,
              scope text not null,
              collection text not null
            );
            create table embeddings(
              id integer primary key,
              segment_id text not null,
              embedding_id text not null,
              seq_id blob not null,
              created_at timestamp not null default current_timestamp
            );
            create table embedding_metadata(
              id integer not null,
              key text not null,
              string_value text,
              int_value integer,
              float_value real,
              bool_value integer,
              primary key (id, key)
            );
            """
        )
        con.execute(
            "insert into collections values (?, ?, ?, ?, ?, ?)",
            ("c1", fvr.COLLECTION_NAME, dimension, "db", "{}", "{}"),
        )
        con.execute(
            "insert into segments values (?, ?, ?, ?)",
            ("s1", "urn:chroma:segment/metadata/sqlite", "METADATA", "c1"),
        )
        for idx, meta in enumerate(metas, 1):
            con.execute(
                "insert into embeddings(id, segment_id, embedding_id, seq_id) values (?, ?, ?, ?)",
                (idx, "s1", f"apps_rg:fv:{meta['source_document_id']}", b"1"),
            )
            for key, value in meta.items():
                if isinstance(value, int):
                    con.execute(
                        "insert into embedding_metadata(id, key, int_value) values (?, ?, ?)",
                        (idx, key, value),
                    )
                else:
                    con.execute(
                        "insert into embedding_metadata(id, key, string_value) values (?, ?, ?)",
                        (idx, key, str(value)),
                    )
        con.commit()
    finally:
        con.close()


def _write_sparse_sidecar(root: Path, *, docs: int = 1) -> None:
    path = root / fvr.SPARSE_SIDE_CAR_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path))
    try:
        con.execute("create table docs(id text primary key, text text not null)")
        for idx in range(1, docs + 1):
            con.execute(
                "insert into docs(id, text) values (?, ?)",
                (f"doc_{idx}", f"fact vector doc {idx}"),
            )
        con.commit()
    finally:
        con.close()


def test_fact_vector_readiness_passes_when_manifest_and_all_sections_are_hydrated(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path)
    sqlite_path = tmp_path / "chroma" / "chroma.sqlite3"
    _write_chroma_sqlite(sqlite_path, _all_lane_metas())
    _write_sparse_sidecar(tmp_path, docs=11)

    receipt = fvr.build_fact_vector_readiness_receipt(
        repo_root=tmp_path,
        chroma_path=str(sqlite_path),
    )

    assert receipt["status"] == fvr.STATUS_PASS
    assert receipt["allowed"] is True
    assert receipt["failed_sections"] == []
    assert len(receipt["rows"]) == 11
    assert receipt["policy"]["c0_write_authority"] is False
    assert receipt["sparse_sidecar"]["doc_count"] == 11


def test_fact_vector_readiness_does_not_require_narrative_direct_hydration(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path)
    sqlite_path = tmp_path / "chroma" / "chroma.sqlite3"
    _write_chroma_sqlite(sqlite_path, _direct_vector_metas())
    _write_sparse_sidecar(tmp_path, docs=7)

    receipt = fvr.build_fact_vector_readiness_receipt(
        repo_root=tmp_path,
        chroma_path=str(sqlite_path),
    )

    narrative_rows = [
        row for row in receipt["rows"] if row["section_id"].endswith("_narrative")
    ]
    assert receipt["status"] == fvr.STATUS_PASS
    assert receipt["failed_sections"] == []
    assert len(narrative_rows) == 4
    assert all(row["direct_fact_vector_required"] is False for row in narrative_rows)
    assert all(row["pre_run_hydration_present"] is False for row in narrative_rows)
    assert all(row["authority_mode"] == "inherited_bullet_proof" for row in narrative_rows)


def test_fact_vector_readiness_narrative_scope_skips_fact_vector_environment(
    tmp_path: Path,
) -> None:
    receipt = fvr.build_fact_vector_readiness_receipt(
        repo_root=tmp_path,
        chroma_path=str(tmp_path / "missing" / "chroma.sqlite3"),
        sections_in_scope=("unify_narrative",),
    )

    assert receipt["status"] == fvr.STATUS_PASS
    assert receipt["sections_in_scope"] == ["unify_narrative"]
    assert receipt["direct_vector_lanes_in_scope"] == []
    assert receipt["collection"]["skipped"] is True
    assert receipt["sparse_sidecar"]["skipped"] is True
    assert receipt["rows"][0]["authority_mode"] == "inherited_bullet_proof"


def test_fact_vector_readiness_blocks_stale_manifest_before_u0(tmp_path: Path) -> None:
    _write_manifest(tmp_path, stale=True)
    sqlite_path = tmp_path / "chroma" / "chroma.sqlite3"
    _write_chroma_sqlite(sqlite_path, _all_lane_metas())
    _write_sparse_sidecar(tmp_path)

    receipt = fvr.build_fact_vector_readiness_receipt(
        repo_root=tmp_path,
        chroma_path=str(sqlite_path),
    )

    assert receipt["status"] == fvr.STATUS_BLOCKED
    assert "bootstrap_manifest_required_lanes_not_current" in receipt["reasons"]
    assert "bootstrap_manifest_has_locked_deterministic_lanes" in receipt["reasons"]
    assert receipt["failed_sections"] == []


def test_fact_vector_readiness_diagnostic_mode_can_ignore_manifest_alignment(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, stale=True)
    sqlite_path = tmp_path / "chroma" / "chroma.sqlite3"
    _write_chroma_sqlite(sqlite_path, _all_lane_metas())
    _write_sparse_sidecar(tmp_path)

    receipt = fvr.build_fact_vector_readiness_receipt(
        repo_root=tmp_path,
        chroma_path=str(sqlite_path),
        require_manifest_alignment=False,
    )

    assert receipt["status"] == fvr.STATUS_PASS
    assert receipt["failed_sections"] == []


def test_fact_vector_readiness_fallback_accepts_existing_sufficient_index(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, stale=True)
    sqlite_path = tmp_path / "chroma" / "chroma.sqlite3"
    _write_chroma_sqlite(sqlite_path, _all_lane_metas())
    _write_sparse_sidecar(tmp_path, docs=11)

    receipt = fvr.build_fact_vector_readiness_with_fallback_receipt(
        repo_root=tmp_path,
        chroma_path=str(sqlite_path),
        allow_existing_index_fallback=True,
    )

    assert receipt["status"] == fvr.STATUS_PASS
    assert receipt["fallback"]["decision"] == fvr.FALLBACK_DECISION_USED_EXISTING_INDEX
    assert "bootstrap_manifest_required_lanes_not_current" in receipt["fallback"]["strict_reasons"]
    assert receipt["summary"]["sparse_sidecar_doc_count"] == 11


def test_fact_vector_readiness_fallback_blocks_without_sparse_sidecar(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, stale=True)
    sqlite_path = tmp_path / "chroma" / "chroma.sqlite3"
    _write_chroma_sqlite(sqlite_path, _all_lane_metas())

    receipt = fvr.build_fact_vector_readiness_with_fallback_receipt(
        repo_root=tmp_path,
        chroma_path=str(sqlite_path),
        allow_existing_index_fallback=True,
    )

    assert receipt["status"] == fvr.STATUS_BLOCKED
    assert receipt["fallback"]["decision"] == fvr.FALLBACK_DECISION_BLOCKED
    assert "sparse_sidecar_missing" in receipt["fallback"]["fallback_reasons"]
