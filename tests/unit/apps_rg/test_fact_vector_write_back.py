"""fact_vectors write-back discipline (plan apps-rg-fact-vector-writeback-discipline-67652c).

Deterministic, hermetic. Guards the mental model: only EXTRACT/FUSE/ENRICH transforms of
already-grounded content (traceable to a source document) may be STAGED for fact_vectors; generated
content routes to the semantic-cache domain; a claimed transform with no provenance is REJECTED; and
staging→live promotion is gated by a deterministic re-validation (or HITL hold).
"""
from __future__ import annotations

import json
import sqlite3

import pytest

from agentic_core.L4_state.fact_writeback import FactWritebackProfile
from apps_rg.runtime.c0.fact_vector_write_back import (
    APPS_RG_FACT_WRITEBACK_PROFILE,
    ENRICH,
    EXTRACT,
    FUSE,
    GENERATED,
    PROMOTION_HITL_ENV,
    PROMOTION_HOLD_REASON_METADATA_KEY,
    PROMOTION_MODE_DEFERRED,
    PROMOTION_MODE_ENV,
    PROMOTION_RECEIPT_NAME,
    REJECT,
    SEMANTIC_CACHE,
    STAGE_FOR_FACT_VECTORS,
    STAGING_COLLECTION_NAME,
    X3_ALLOW,
    _staged_row_is_promotable,
    classify_write_back_operation,
    decide_write_back,
    has_source_pointer,
    is_generated_source,
    list_staged_fact_vectors,
    promote_staged_fact_vectors,
    promotion_hitl_required,
    promotion_mode,
    source_grounding_ok,
)


def _grounded(**over):
    base = {
        "source_type": "candidate_fact_ledger",
        "proof_status": "proof_eligible",
        "source_span_ref": "ledger:fact_x",
        "text_to_embed": "x" * 40,
    }
    base.update(over)
    return base


def _promotable_metadata(**over):
    base = {
        "write_back_operation": "extract",
        "source_document_id": "f1",
        "source_type": "candidate_fact_ledger",
        "confidence": "HIGH",
        "proof_status": "proof_eligible",
        "authority_class": "PRIMARY",
        "chunk_digest": "digest-f1",
    }
    base.update(over)
    return base


def test_apps_rg_profile_binds_generic_fact_writeback_engine() -> None:
    assert isinstance(APPS_RG_FACT_WRITEBACK_PROFILE, FactWritebackProfile)
    assert APPS_RG_FACT_WRITEBACK_PROFILE.stage_route == STAGE_FOR_FACT_VECTORS
    assert APPS_RG_FACT_WRITEBACK_PROFILE.semantic_cache_route == SEMANTIC_CACHE
    assert set(APPS_RG_FACT_WRITEBACK_PROFILE.allowed_operations) == {EXTRACT, FUSE, ENRICH}


# --- classifier -------------------------------------------------------------


def test_grounded_default_is_extract() -> None:
    op, _ = classify_write_back_operation(_grounded())
    assert op == EXTRACT


def test_declared_fuse_and_enrich_honored_on_grounded() -> None:
    assert classify_write_back_operation(_grounded(write_back_operation="fuse"))[0] == FUSE
    assert classify_write_back_operation(_grounded(write_back_operation="enrich"))[0] == ENRICH


@pytest.mark.parametrize(
    "atom",
    [
        {"source_type": "jd_payload", "proof_status": "targeting_only", "text_to_embed": "y" * 40},
        {"source_type": "company_research", "proof_status": "not_proof", "text_to_embed": "z" * 40},
        _grounded(proof_status="not_proof"),
        _grounded(write_back_operation="generated"),
    ],
)
def test_generated_sources_classified_generated(atom) -> None:
    assert classify_write_back_operation(atom)[0] == GENERATED


# --- grounding gate ---------------------------------------------------------


def test_is_generated_source_flags_forbidden_and_proof() -> None:
    assert is_generated_source({"source_type": "jd_payload"})[0] is True
    assert is_generated_source({"proof_status": "targeting_only"})[0] is True
    assert is_generated_source(_grounded())[0] is False


def test_has_source_pointer() -> None:
    assert has_source_pointer({"source_span_ref": "ledger:f"}) is True
    assert has_source_pointer({"source_ref": "x.json"}) is True
    assert has_source_pointer({"source_span_ref": "", "source_ref": ""}) is False


def test_source_grounding_ok_requires_pointer_and_grounded_source() -> None:
    assert source_grounding_ok(_grounded())[0] is True
    assert source_grounding_ok(_grounded(source_span_ref="", source_ref=""))[0] is False
    assert source_grounding_ok({"source_type": "jd_payload", "source_span_ref": "x"})[0] is False


# --- routing (the three outcomes) ------------------------------------------


def test_route_grounded_transform_to_staging() -> None:
    d = decide_write_back(_grounded())
    assert d.route == STAGE_FOR_FACT_VECTORS and d.operation == EXTRACT


def test_route_generated_to_semantic_cache() -> None:
    d = decide_write_back({"source_type": "jd_payload", "proof_status": "targeting_only", "text_to_embed": "y" * 40})
    assert d.route == SEMANTIC_CACHE and d.operation == GENERATED


def test_route_claimed_transform_without_pointer_is_rejected() -> None:
    # Grounded-class source, declares enrich, but no source pointer → fail closed.
    d = decide_write_back(
        {"source_type": "candidate_fact_ledger", "proof_status": "proof_eligible",
         "write_back_operation": "enrich", "text_to_embed": "c" * 40}
    )
    assert d.route == REJECT and d.operation == ENRICH


# --- promotion gate re-validation (hostile verifier) -----------------------


def test_staged_row_promotable_requires_operation_source_and_provenance() -> None:
    ok, _ = _staged_row_is_promotable(
        {"write_back_operation": "extract", "source_document_id": "fact_x", "source_type": "candidate_fact_ledger"}
    )
    assert ok is True
    assert _staged_row_is_promotable({"write_back_operation": "generated", "source_document_id": "f"})[0] is False
    assert _staged_row_is_promotable({"write_back_operation": "extract", "source_document_id": ""})[0] is False
    assert _staged_row_is_promotable(
        {"write_back_operation": "extract", "source_document_id": "f", "source_type": "jd_payload"}
    )[0] is False


def test_promotion_hitl_required_env(monkeypatch) -> None:
    monkeypatch.delenv(PROMOTION_HITL_ENV, raising=False)
    assert promotion_hitl_required() is False
    monkeypatch.setenv(PROMOTION_HITL_ENV, "1")
    assert promotion_hitl_required() is True
    assert promotion_hitl_required(explicit=False) is False  # explicit overrides env


def test_promotion_mode_defaults_inline_and_accepts_deferred(monkeypatch) -> None:
    monkeypatch.delenv(PROMOTION_MODE_ENV, raising=False)
    assert promotion_mode() == "inline"
    monkeypatch.setenv(PROMOTION_MODE_ENV, PROMOTION_MODE_DEFERRED)
    assert promotion_mode() == PROMOTION_MODE_DEFERRED
    assert promotion_mode(explicit="inline") == "inline"


# --- staging → live round-trip (hermetic Chroma, no BGE model) -------------


@pytest.fixture
def _plain_chroma(monkeypatch):
    """Patch the precomputed-collection helper to a plain Chroma collection (explicit embeddings,
    no embedding function), so the promotion round-trip needs no BGE model."""
    import apps_rg.runtime.chroma_precomputed_collection as cpc

    def _plain(client, name, *, metadata=None):
        return client.get_or_create_collection(name=name)

    monkeypatch.setattr(cpc, "get_precomputed_embeddings_collection", _plain)
    return _plain


def _stage_row(client, *, doc_id, metadata, embedding):
    col = client.get_or_create_collection(name=STAGING_COLLECTION_NAME)
    col.upsert(ids=[doc_id], embeddings=[embedding], documents=["grounded claim text"], metadatas=[metadata])


def test_promotion_moves_promotable_rows_staging_to_live(tmp_path, _plain_chroma, monkeypatch) -> None:
    import chromadb

    monkeypatch.delenv(PROMOTION_HITL_ENV, raising=False)
    path = str(tmp_path / "chroma")
    client = chromadb.PersistentClient(path=path)
    emb = [0.1, 0.2, 0.3, 0.4]
    _stage_row(client, doc_id="apps_rg:fv:f1", embedding=emb, metadata=_promotable_metadata())
    _stage_row(client, doc_id="apps_rg:fv:bad", embedding=emb,
               metadata={"write_back_operation": "generated", "source_document_id": "bad", "source_type": "jd_payload"})

    receipt = promote_staged_fact_vectors(chroma_path=path, sparse_dir=tmp_path / "sparse")
    assert receipt["status"] == "PASS"
    assert receipt["staged_count"] == 2
    assert receipt["promoted_count"] == 1  # only the grounded extract
    assert receipt["rejected_count"] == 1  # the generated row
    assert receipt["sparse_synced"] is True
    assert receipt["dense_count"] == receipt["sparse_doc_count"] == 1

    live = client.get_or_create_collection(name="fact_vectors")
    live_row = live.get(ids=["apps_rg:fv:f1"], include=["metadatas"])
    assert live_row["ids"] == ["apps_rg:fv:f1"]
    assert live_row["metadatas"][0]["tier"] == "learned"
    assert live_row["metadatas"][0]["promotion_score"] == 1.0
    # promoted row removed from staging; the rejected one stays
    staging = client.get_or_create_collection(name=STAGING_COLLECTION_NAME)
    remaining = set(staging.get()["ids"])
    assert "apps_rg:fv:f1" not in remaining
    assert "apps_rg:fv:bad" in remaining

    with sqlite3.connect(str(tmp_path / "sparse" / "fact_vectors.db")) as conn:
        assert conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0] == 1
        assert conn.execute("SELECT id FROM docs_fts WHERE docs_fts MATCH 'grounded'").fetchone()[0] == "apps_rg:fv:f1"


def test_promotion_holds_for_hitl(tmp_path, _plain_chroma, monkeypatch) -> None:
    import chromadb

    monkeypatch.setenv(PROMOTION_HITL_ENV, "1")
    path = str(tmp_path / "chroma_hitl")
    client = chromadb.PersistentClient(path=path)
    _stage_row(
        client,
        doc_id="apps_rg:fv:f1",
        embedding=[0.1, 0.2, 0.3, 0.4],
        metadata=_promotable_metadata(),
    )

    receipt = promote_staged_fact_vectors(chroma_path=path)
    assert receipt["status"] == "HELD_FOR_HITL"
    assert receipt["held_count"] == 1
    assert receipt["held"] == [{"id": "apps_rg:fv:f1", "reason": "hitl_required"}]
    assert receipt["promoted_count"] == 0
    # row stays in staging, nothing promoted to live
    staging = client.get_or_create_collection(name=STAGING_COLLECTION_NAME)
    assert "apps_rg:fv:f1" in set(staging.get()["ids"])


def test_promotion_skips_duplicate_chunk_digest(tmp_path, _plain_chroma, monkeypatch) -> None:
    import chromadb

    monkeypatch.delenv(PROMOTION_HITL_ENV, raising=False)
    path = str(tmp_path / "chroma_duplicate")
    client = chromadb.PersistentClient(path=path)
    emb = [0.1, 0.2, 0.3, 0.4]
    live = client.get_or_create_collection(name="fact_vectors")
    live.upsert(
        ids=["apps_rg:fv:existing"],
        embeddings=[emb],
        documents=["existing grounded claim text"],
        metadatas=[_promotable_metadata(source_document_id="existing")],
    )
    _stage_row(
        client,
        doc_id="apps_rg:fv:new",
        embedding=emb,
        metadata=_promotable_metadata(source_document_id="new"),
    )

    receipt = promote_staged_fact_vectors(chroma_path=path, sparse_dir=tmp_path / "sparse")

    assert receipt["status"] == "NONE_PROMOTABLE"
    assert receipt["promoted_count"] == 0
    assert receipt["held_count"] == 1
    assert receipt["held"] == [
        {"id": "apps_rg:fv:new", "reason": "duplicate_digest:apps_rg:fv:existing"}
    ]
    staging = client.get_or_create_collection(name=STAGING_COLLECTION_NAME)
    assert "apps_rg:fv:new" in set(staging.get()["ids"])


def test_promotion_holds_below_score_floor(tmp_path, _plain_chroma, monkeypatch) -> None:
    import chromadb

    monkeypatch.delenv(PROMOTION_HITL_ENV, raising=False)
    path = str(tmp_path / "chroma_low_score")
    client = chromadb.PersistentClient(path=path)
    _stage_row(
        client,
        doc_id="apps_rg:fv:low",
        embedding=[0.1, 0.2, 0.3, 0.4],
        metadata=_promotable_metadata(
            source_document_id="low",
            confidence="LOW",
            chunk_digest="digest-low",
        ),
    )

    receipt = promote_staged_fact_vectors(chroma_path=path, sparse_dir=tmp_path / "sparse")

    assert receipt["status"] == "NONE_PROMOTABLE"
    assert receipt["promoted_count"] == 0
    assert receipt["held_count"] == 1
    assert receipt["held"][0]["id"] == "apps_rg:fv:low"
    assert receipt["held"][0]["reason"].startswith("promotion_score_below_floor")
    staging = client.get_or_create_collection(name=STAGING_COLLECTION_NAME)
    assert "apps_rg:fv:low" in set(staging.get()["ids"])


def test_sparse_sync_full_rebuilds_when_incremental_count_mismatches(tmp_path, _plain_chroma, monkeypatch) -> None:
    import chromadb

    monkeypatch.delenv(PROMOTION_HITL_ENV, raising=False)
    path = str(tmp_path / "chroma_sparse_mismatch")
    sparse_dir = tmp_path / "sparse"
    client = chromadb.PersistentClient(path=path)
    emb = [0.1, 0.2, 0.3, 0.4]
    live = client.get_or_create_collection(name="fact_vectors")
    live.upsert(
        ids=["apps_rg:fv:existing"],
        embeddings=[emb],
        documents=["existing alpha fact"],
        metadatas=[
            _promotable_metadata(
                source_document_id="existing",
                chunk_digest="digest-existing",
            )
        ],
    )
    _stage_row(
        client,
        doc_id="apps_rg:fv:new",
        embedding=emb,
        metadata=_promotable_metadata(
            source_document_id="new",
            chunk_digest="digest-new",
        ),
    )

    receipt = promote_staged_fact_vectors(chroma_path=path, sparse_dir=sparse_dir)

    assert receipt["status"] == "PASS"
    assert receipt["dense_count"] == receipt["sparse_doc_count"] == 2
    assert "full_rebuild_after_count_mismatch" in receipt["sparse_sync_reason"]
    with sqlite3.connect(str(sparse_dir / "fact_vectors.db")) as conn:
        assert conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0] == 2


def test_promotion_writes_standalone_receipt(tmp_path, _plain_chroma, monkeypatch, caplog) -> None:
    import chromadb

    from tools.ledgers import hook_helpers

    monkeypatch.delenv(PROMOTION_HITL_ENV, raising=False)
    emitted: list[dict[str, object]] = []

    def _fake_emit_ledger_event(**kwargs):
        emitted.append(kwargs)
        return "event-fv-witness"

    monkeypatch.setattr(hook_helpers, "emit_ledger_event", _fake_emit_ledger_event)
    caplog.set_level("INFO", logger="apps_rg.runtime.c0.fact_vector_write_back")
    path = str(tmp_path / "chroma_receipt")
    artifact_dir = tmp_path / "run"
    client = chromadb.PersistentClient(path=path)
    _stage_row(
        client,
        doc_id="apps_rg:fv:f1",
        embedding=[0.1, 0.2, 0.3, 0.4],
        metadata=_promotable_metadata(),
    )

    receipt = promote_staged_fact_vectors(
        chroma_path=path,
        artifact_dir=artifact_dir,
        sparse_dir=tmp_path / "sparse",
    )

    receipt_path = artifact_dir / PROMOTION_RECEIPT_NAME
    assert receipt_path.is_file()
    written = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert written["promotion_run_id"] == receipt["promotion_run_id"]
    assert written["promoted_count"] == 1
    assert written["uwg_witness"]["ledger"] == "router_l4_uwg"
    assert written["uwg_witness"]["event_id"] == "event-fv-witness"
    assert emitted[0]["ledger"] == "router_l4_uwg"
    assert emitted[0]["event_kind"] == "route_decision"
    assert emitted[0]["prediction"]["selected"] == "commit"
    assert emitted[0]["outcome"]["success"] is True
    assert (
        emitted[0]["metadata"]["promotion_receipt_digest"]
        == written["uwg_witness"]["promotion_receipt_digest"]
    )
    assert "ROUTER_DECISION: layer=L4 router=uwg" in caplog.text


def test_deferred_x3_gate_promotes_only_allow_run(tmp_path, _plain_chroma, monkeypatch) -> None:
    import chromadb

    monkeypatch.delenv(PROMOTION_HITL_ENV, raising=False)
    path = str(tmp_path / "chroma_x3")
    client = chromadb.PersistentClient(path=path)
    emb = [0.1, 0.2, 0.3, 0.4]
    _stage_row(
        client,
        doc_id="apps_rg:fv:allow",
        embedding=emb,
        metadata=_promotable_metadata(
            source_document_id="allow",
            chunk_digest="digest-allow",
            run_id="run-allow",
            staged_at_utc="2026-06-10T00:00:00+00:00",
        ),
    )
    _stage_row(
        client,
        doc_id="apps_rg:fv:block",
        embedding=emb,
        metadata=_promotable_metadata(
            source_document_id="block",
            chunk_digest="digest-block",
            run_id="run-block",
            staged_at_utc="2026-06-10T00:00:00+00:00",
        ),
    )

    blocked = promote_staged_fact_vectors(
        chroma_path=path,
        run_id="run-block",
        x3_code="X3_BLOCK",
        require_x3_allow=True,
    )

    assert blocked["status"] == "HELD_FOR_X3"
    assert blocked["promoted_count"] == 0
    assert blocked["held"][0]["reason"] == "run_not_x3_allow:X3_BLOCK"
    staging = client.get_or_create_collection(name=STAGING_COLLECTION_NAME)
    block_meta = staging.get(ids=["apps_rg:fv:block"], include=["metadatas"])["metadatas"][0]
    assert block_meta[PROMOTION_HOLD_REASON_METADATA_KEY] == "run_not_x3_allow:X3_BLOCK"

    allowed = promote_staged_fact_vectors(
        chroma_path=path,
        run_id="run-allow",
        x3_code=X3_ALLOW,
        require_x3_allow=True,
        sparse_dir=tmp_path / "sparse",
    )

    assert allowed["status"] == "PASS"
    assert allowed["promoted_count"] == 1
    live = client.get_or_create_collection(name="fact_vectors")
    assert live.get(ids=["apps_rg:fv:allow"])["ids"] == ["apps_rg:fv:allow"]
    remaining = set(staging.get()["ids"])
    assert "apps_rg:fv:block" in remaining
    assert "apps_rg:fv:allow" not in remaining


def test_list_staged_fact_vectors_surfaces_hold_reason(tmp_path, _plain_chroma, monkeypatch) -> None:
    import chromadb

    monkeypatch.delenv(PROMOTION_HITL_ENV, raising=False)
    path = str(tmp_path / "chroma_list")
    client = chromadb.PersistentClient(path=path)
    _stage_row(
        client,
        doc_id="apps_rg:fv:held",
        embedding=[0.1, 0.2, 0.3, 0.4],
        metadata=_promotable_metadata(
            source_document_id="held",
            chunk_digest="digest-held",
            run_id="run-held",
        ),
    )
    promote_staged_fact_vectors(
        chroma_path=path,
        run_id="run-held",
        x3_code="X3_BLOCK",
        require_x3_allow=True,
    )

    listed = list_staged_fact_vectors(chroma_path=path)

    assert listed["status"] == "PASS"
    row = listed["rows"][0]
    assert row["id"] == "apps_rg:fv:held"
    assert row["run_id"] == "run-held"
    assert row["hold_reason"] == "run_not_x3_allow:X3_BLOCK"
