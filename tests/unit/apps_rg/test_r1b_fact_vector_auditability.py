"""R1B and fact-vector auditability regressions."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.cache.cache_preflight_evidence import build_cache_preflight_evidence
from apps_rg.cache.r1b_constants import CACHE_GRAIN_ROLE_TARGET_RUN
from apps_rg.cache.r1b_whole_run_preflight import WholeRunR1BPreflightResult
from apps_rg.cache.whole_run_entrypoint_preflight import (
    ENTRYPOINT_CANONICAL_DISPATCH,
    run_whole_run_cache_preflight,
)
from apps_rg.runtime.embedding_settings import AppsRgEmbeddingSettings


def _settings() -> AppsRgEmbeddingSettings:
    return AppsRgEmbeddingSettings(
        embeddings_enabled=True,
        embedding_required=False,
        embedding_model_name="BAAI/bge-m3",
        embedding_model_path="/models/bge-m3",
        embedding_model_resolved=True,
        embedding_model_source="local",
        vector_db="chroma",
        semantic_cache_enabled=True,
        dense_retrieval_enabled=True,
        chroma_default_ef_allowed=False,
        chroma_default_ef_used=False,
        failure_mode="not_applicable",
        semantic_cache_ineligible=False,
        dense_retrieval_ineligible=False,
        route_result="CONTINUE_WITH_NON_EMBEDDING_PATH",
        decisive_reason="explicit local BGE resolved",
        chroma_persist_dir="/tmp/chroma",
    )


def test_r1b_disabled_preflight_has_explicit_reason(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import apps_rg.cache.whole_run_entrypoint_preflight as preflight_mod
    import apps_rg.runtime.embedding_settings as embedding_settings

    monkeypatch.delenv("APPS_RG_ENABLE_R1B_SEMANTIC_CACHE", raising=False)
    monkeypatch.delenv("APPS_RG_R1B_PREFLIGHT_PROBE_ONLY", raising=False)
    monkeypatch.setattr(preflight_mod, "check_r1a_cache", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        embedding_settings,
        "resolve_apps_rg_embedding_settings",
        lambda **_kwargs: _settings(),
    )

    def _unexpected_r1b(**_kwargs):
        raise AssertionError("R1B must not execute when reuse and probe-only are disabled")

    monkeypatch.setattr(preflight_mod, "execute_whole_run_r1b_preflight", _unexpected_r1b)
    preflight = run_whole_run_cache_preflight(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        raw_request={"resume_hash": "r", "jd_hash": "j"},
        target_company="Co",
        target_role="Role",
        artifact_dir=tmp_path / "run",
        runs_dir=tmp_path,
    )
    evidence = build_cache_preflight_evidence(preflight, artifact_dir=tmp_path / "run")

    assert evidence["r1b_preflight_status"] == "skipped"
    assert evidence["r1b_preflight_reason"] == "APPS_RG_ENABLE_R1B_SEMANTIC_CACHE_FALSE"
    assert evidence["r1b_eligibility"]["probeable"] is True
    assert evidence["r1b_eligibility"]["reuse_authority_enabled"] is False


def test_r1b_probe_only_hit_does_not_skip_generation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import apps_rg.cache.whole_run_entrypoint_preflight as preflight_mod
    import apps_rg.runtime.embedding_settings as embedding_settings

    monkeypatch.delenv("APPS_RG_ENABLE_R1B_SEMANTIC_CACHE", raising=False)
    monkeypatch.setenv("APPS_RG_R1B_PREFLIGHT_PROBE_ONLY", "1")
    monkeypatch.setattr(preflight_mod, "check_r1a_cache", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        embedding_settings,
        "resolve_apps_rg_embedding_settings",
        lambda **_kwargs: _settings(),
    )
    monkeypatch.setattr(
        preflight_mod,
        "execute_whole_run_r1b_preflight",
        lambda **_kwargs: WholeRunR1BPreflightResult(
            outcome="r1b_hit",
            r1b_hit=True,
            lookup_anchor="HistoricalIntentRecord.request_intent_vector",
            cache_grain=CACHE_GRAIN_ROLE_TARGET_RUN,
            terminal_packet={"x3_disposition": "X3_ALLOW", "run_id": "source-run"},
            generation_required=False,
        ),
    )

    preflight = run_whole_run_cache_preflight(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        raw_request={"resume_hash": "r", "jd_hash": "j"},
        target_company="Co",
        target_role="Role",
        artifact_dir=tmp_path / "run",
        runs_dir=tmp_path,
    )
    evidence = build_cache_preflight_evidence(preflight, artifact_dir=tmp_path / "run")

    assert preflight.r1b_hit is True
    assert preflight.r1b_probe_only is True
    assert preflight.generation_required is True
    assert evidence["r1b_preflight_status"] == "hit_probe_only"
    assert evidence["generation_spine_invocation_allowed"] is True


def test_product_gate_blocks_grounded_fact_vectors_without_promotion_proof(tmp_path: Path) -> None:
    from apps_rg.runtime.integrated_product_proof_gate import _fact_vector_writeback_blockers

    section_dir = tmp_path / "sections" / "competencies"
    section_dir.mkdir(parents=True)
    (section_dir / "c02_fact_vectors_ingest_receipt.json").write_text(
        """{
          "status": "STAGED_DEFERRED",
          "run_id": "section-run",
          "staged_count": 1,
          "promotion_mode": "deferred"
        }
        """,
        encoding="utf-8",
    )

    blockers, present, status = _fact_vector_writeback_blockers(tmp_path)

    assert present is True
    assert status == "FAIL"
    assert "fact_vector_writeback_promotion_proof_missing" in blockers


def test_fact_vector_promotion_receipt_has_uwg_and_live_retrieval_proof(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import apps_rg.runtime.chroma_precomputed_collection as cpc
    from agentic_core.L4_state.uwg.durable_write_gateway import reset_default_gateway
    from apps_rg.runtime.c0.chroma_persistent_client import (
        ensure_apps_rg_chroma_client,
        reset_apps_rg_chroma_client_cache_for_tests,
    )
    from apps_rg.runtime.c0.fact_vector_write_back import (
        PROMOTION_HITL_ENV,
        STAGING_COLLECTION_NAME,
        promote_staged_fact_vectors,
    )

    reset_default_gateway()
    reset_apps_rg_chroma_client_cache_for_tests()
    monkeypatch.delenv(PROMOTION_HITL_ENV, raising=False)

    def _plain(client, name, *, metadata=None):
        del metadata
        return client.get_or_create_collection(name=name)

    monkeypatch.setattr(cpc, "get_precomputed_embeddings_collection", _plain)

    chroma_path = str(tmp_path / "chroma")
    client = ensure_apps_rg_chroma_client(chroma_path)
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
                "run_id": "section-run",
            }
        ],
    )

    receipt = promote_staged_fact_vectors(
        chroma_path=chroma_path,
        artifact_dir=tmp_path / "run",
        promotion_run_id="test-promotion-run",
        run_id="section-run",
        x3_code="X3D",
        require_x3_allow=True,
        sparse_dir=tmp_path / "sparse",
    )

    assert receipt["status"] == "PASS"
    assert receipt["source_x3_code"] == "X3D"
    assert receipt["x3_finish_code_normalized"] == "X3_ALLOW"
    assert receipt["uwg"]["status"] == "ADMITTED"
    assert receipt["uwg"]["target_surface"] == "l4.apps_rg.fact_vectors"
    assert receipt["retrieval_proof"]["status"] == "PASS"
    assert receipt["live_projection"]["retrieved_ids"] == ["apps_rg:fv:f1"]
    assert (tmp_path / "run" / "fact_vectors_uwg" / "uwg_commit_receipt.json").is_file()
