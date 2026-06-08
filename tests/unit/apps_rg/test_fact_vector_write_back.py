"""fact_vectors write-back discipline (plan apps-rg-fact-vector-writeback-discipline-67652c).

Deterministic, hermetic. Guards the mental model: only EXTRACT/FUSE/ENRICH transforms of
already-grounded content (traceable to a source document) may be STAGED for fact_vectors; generated
content routes to the semantic-cache domain; a claimed transform with no provenance is REJECTED; and
staging→live promotion is gated by a deterministic re-validation (or HITL hold).
"""
from __future__ import annotations

import pytest

from apps_rg.runtime.c0.fact_vector_write_back import (
    ENRICH,
    EXTRACT,
    FUSE,
    GENERATED,
    PROMOTION_HITL_ENV,
    REJECT,
    SEMANTIC_CACHE,
    STAGE_FOR_FACT_VECTORS,
    STAGING_COLLECTION_NAME,
    _staged_row_is_promotable,
    classify_write_back_operation,
    decide_write_back,
    has_source_pointer,
    is_generated_source,
    promote_staged_fact_vectors,
    promotion_hitl_required,
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
    _stage_row(client, doc_id="apps_rg:fv:f1", embedding=emb,
               metadata={"write_back_operation": "extract", "source_document_id": "f1", "source_type": "candidate_fact_ledger"})
    _stage_row(client, doc_id="apps_rg:fv:bad", embedding=emb,
               metadata={"write_back_operation": "generated", "source_document_id": "bad", "source_type": "jd_payload"})

    receipt = promote_staged_fact_vectors(chroma_path=path)
    assert receipt["status"] == "PASS"
    assert receipt["staged_count"] == 2
    assert receipt["promoted_count"] == 1  # only the grounded extract
    assert receipt["rejected_count"] == 1  # the generated row

    live = client.get_or_create_collection(name="fact_vectors")
    assert live.get(ids=["apps_rg:fv:f1"])["ids"] == ["apps_rg:fv:f1"]
    # promoted row removed from staging; the rejected one stays
    staging = client.get_or_create_collection(name=STAGING_COLLECTION_NAME)
    remaining = set(staging.get()["ids"])
    assert "apps_rg:fv:f1" not in remaining
    assert "apps_rg:fv:bad" in remaining


def test_promotion_holds_for_hitl(tmp_path, _plain_chroma, monkeypatch) -> None:
    import chromadb

    monkeypatch.setenv(PROMOTION_HITL_ENV, "1")
    path = str(tmp_path / "chroma_hitl")
    client = chromadb.PersistentClient(path=path)
    _stage_row(client, doc_id="apps_rg:fv:f1", embedding=[0.1, 0.2, 0.3, 0.4],
               metadata={"write_back_operation": "extract", "source_document_id": "f1", "source_type": "candidate_fact_ledger"})

    receipt = promote_staged_fact_vectors(chroma_path=path)
    assert receipt["status"] == "HELD_FOR_HITL"
    assert receipt["held_count"] == 1
    assert receipt["promoted_count"] == 0
    # row stays in staging, nothing promoted to live
    staging = client.get_or_create_collection(name=STAGING_COLLECTION_NAME)
    assert "apps_rg:fv:f1" in set(staging.get()["ids"])
