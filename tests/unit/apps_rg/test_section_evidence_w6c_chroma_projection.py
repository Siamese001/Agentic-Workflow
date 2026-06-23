"""W6C — governed Chroma read-surface projection after UWG-admitted R1B commit."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import apps_rg.cache.r1b_chroma_read_surface_projection as projection
from apps_rg.cache.r1b_chroma_read_surface_projection import (
    CHROMA_COLLECTION_INDEX_ARTIFACT,
    CHROMA_READ_AFTER_WRITE_ARTIFACT,
    READ_SURFACE_REFRESH_ARTIFACT,
)
from apps_rg.cache.r1b_governed_receipt_emission import (
    COMMIT_REQUEST_ARTIFACT,
    REASON_X3_NOT_X3C,
    emit_section_r1b_governed_receipt_chain,
)
from apps_rg.cache.r1b_uwg_promotion import AppsRgR1BUwgGateway
from apps_rg.runtime.semantic_cache_persistence_quarantine import (
    CHROMA_CLASS_NON_DURABLE,
    NO_DIRECT_CHROMA_ASSERTION_ARTIFACT,
    assess_uwg_durable_write_chain,
    classify_shadow_chroma_write_path,
    finalize_semantic_cache_quarantine,
)
from apps_rg.runtime.section_evidence_package import (
    EVIDENCE_PACKAGE_INDEX_ARTIFACT,
    finalize_section_evidence_package,
)
from apps_rg.runtime.section_l7_binding_manifest import build_section_l7_binding_manifest

# apps-test-model: APP CONTRACT


def _projection_chunk(chunk_id: str, text: str):
    from apps_rg.cache.r1b_models import HistoricalOutputChunk

    return HistoricalOutputChunk.from_dict(
        {
            "chunk_id": chunk_id,
            "parent_intent_record_id": "record-1",
            "chunk_type": "summary",
            "section_id": "executive_summary",
            "chunk_text": text,
            "chunk_digest": f"digest-{chunk_id}",
            "chunk_vector_ref": f"vectors/{chunk_id}.json",
            "artifact_ref": f"artifacts/{chunk_id}.json",
            "artifact_digest": f"artifact-{chunk_id}",
            "source_fact_ids": [],
            "proof_pool_refs": [],
            "support_status": "PASS",
            "x2_status": "PASS",
            "x1d_status": "PASS",
            "section_prompt_hash": "prompt",
            "section_model_profile_hash": "model",
            "generated_at_utc": "2026-06-23T00:00:00+00:00",
        }
    )


def test_projection_embedding_payloads_batch_parent_and_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], int]] = []

    def fake_embed_texts(texts: list[str], *, batch_size: int = 64):
        calls.append((list(texts), batch_size))
        return [
            [0.1] * 1024,
            [0.2] * 1024,
            [0.3] * 1024,
        ]

    monkeypatch.setattr(projection, "embed_texts_bge", fake_embed_texts)
    intent_payload, chunk_payloads = projection._build_projection_embedding_payloads(
        intent_text="intent text",
        digest="intent-digest",
        chunks=[
            _projection_chunk("chunk-1", "chunk one"),
            _projection_chunk("chunk-2", "chunk two"),
        ],
    )

    assert calls == [(["intent text", "chunk one", "chunk two"], 64)]
    assert intent_payload["embedding_model"] == projection.BGE_M3_MODEL_ID
    assert intent_payload["dimensions"] == 1024
    assert intent_payload["values"] == [0.1] * 1024
    assert set(chunk_payloads) == {"chunk-1", "chunk-2"}
    assert chunk_payloads["chunk-1"]["values"] == [0.2] * 1024
    assert chunk_payloads["chunk-2"]["values"] == [0.3] * 1024


def _eligible_run_dir(repo: Path, ad: Path) -> None:
    ad.mkdir(parents=True)
    (ad / "x3_disposition.json").write_text(
        json.dumps(
            {
                "x3_code": "X3_ALLOW",
                "proof_eligible": True,
                "runtime_generation_status": "REAL",
            }
        ),
        encoding="utf-8",
    )
    (ad / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": ad.name,
                "section_id": "executive_summary",
                "proof_eligible": True,
                "runtime_generation_status": "REAL",
                "prompt_profile_hash": "prompt_profile_w7_v1",
                "gate_profile_hash": "gate_profile_w7_v1",
                "jd_hash": "fixture_jd_digest",
                "resume_hash": "fixture_resume_digest",
            }
        ),
        encoding="utf-8",
    )
    from tests.unit.apps_rg.w6_r1b_fixture import seed_w7_fixtures, write_w6_eligible_run_artifacts

    write_w6_eligible_run_artifacts(ad)
    try:
        seed_w7_fixtures(repo)
    except FileNotFoundError:
        pytest.skip("w7 fixtures not present in repo")


def test_x3_block_no_read_surface_or_chroma_projection(tmp_path: Path) -> None:
    ad = tmp_path / "run_block"
    ad.mkdir()
    (ad / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_BLOCK", "proof_eligible": False}),
        encoding="utf-8",
    )
    (ad / "run_manifest.json").write_text(
        json.dumps({"run_id": "run_block", "section_id": "executive_summary"}),
        encoding="utf-8",
    )
    outcome = emit_section_r1b_governed_receipt_chain(
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="run_block",
    )
    assert outcome.reason == REASON_X3_NOT_X3C
    assert outcome.read_surface_refresh_status == "NOT_APPLICABLE"
    assert outcome.chroma_projection_status == "NOT_APPLICABLE"
    assert not (ad / READ_SURFACE_REFRESH_ARTIFACT).is_file()
    assert not (ad / CHROMA_COLLECTION_INDEX_ARTIFACT).is_file()
    assert outcome.durable_vector_persistence_proven is False


def test_eligible_uwg_admitted_emits_w6c_receipts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_R1B_SKIP_CHROMA_PROJECTION", raising=False)
    repo = tmp_path
    ad = repo / "run_allow_w6c"
    _eligible_run_dir(repo, ad)
    outcome = emit_section_r1b_governed_receipt_chain(
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="run_allow_w6c",
        raw_request={
            "jd_hash": "fixture_jd_digest",
            "resume_hash": "fixture_resume_digest",
        },
        gateway=AppsRgR1BUwgGateway(),
    )
    assert outcome.uwg_commit_or_block_status == "ADMITTED"
    assert (ad / READ_SURFACE_REFRESH_ARTIFACT).is_file()
    assert (ad / CHROMA_COLLECTION_INDEX_ARTIFACT).is_file()
    assert (ad / CHROMA_READ_AFTER_WRITE_ARTIFACT).is_file()
    refresh = json.loads((ad / READ_SURFACE_REFRESH_ARTIFACT).read_text(encoding="utf-8"))
    payload = refresh.get("payload") or refresh
    assert payload.get("read_surface") == "r1b_semantic_cache_projection"
    assert payload.get("refresh_status") == "COMPLETE"
    assert payload.get("commit_request_ref")
    assert payload.get("uwg_commit_receipt_ref")
    assert payload.get("l4_namespace_object_ref")
    assert payload.get("proposed_state_diff_ref")

    uwg = assess_uwg_durable_write_chain(repo_root=repo, artifact_dir=ad, integrated_dir=None)
    assert uwg["r1b_uwg_chain_core_complete"] is True
    assert uwg["read_surface_refresh_complete"] is True
    assert uwg["chroma_projection_complete"] is True
    assert uwg["durable_vector_chain_artifacts_complete"] is True
    bundle = finalize_semantic_cache_quarantine(
        repo_root=repo,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="run_allow_w6c",
        integrated_dir=None,
    )
    assert bundle["uwg_assessment"]["durable_vector_persistence_proven"] is True


def test_shadow_chroma_without_chain_stays_non_durable(tmp_path: Path) -> None:
    uwg = assess_uwg_durable_write_chain(
        repo_root=tmp_path,
        artifact_dir=tmp_path / "empty",
        integrated_dir=None,
    )
    assert classify_shadow_chroma_write_path(uwg_assessment=uwg) == CHROMA_CLASS_NON_DURABLE
    assert uwg["durable_vector_persistence_proven"] is False


def test_partial_uwg_chain_does_not_prove_durable_vectors(tmp_path: Path) -> None:
    ad = tmp_path / "partial"
    ad.mkdir()
    (ad / COMMIT_REQUEST_ARTIFACT).write_text(
        json.dumps({"payload": {"commit_request_id": "cr_partial"}}),
        encoding="utf-8",
    )
    uwg = assess_uwg_durable_write_chain(repo_root=tmp_path, artifact_dir=ad, integrated_dir=None)
    assert uwg["durable_vector_persistence_proven"] is False


def test_evidence_package_w6c_status_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_R1B_SKIP_CHROMA_PROJECTION", raising=False)
    repo = tmp_path
    ad = repo / "run_pkg_w6c"
    _eligible_run_dir(repo, ad)
    binding = build_section_l7_binding_manifest(
        repo_root=repo,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="run_pkg_w6c",
        command_surface="test",
        correlation=None,
    )
    finalize_section_evidence_package(
        repo_root=repo,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="run_pkg_w6c",
        binding_manifest=binding,
    )
    pkg = json.loads((ad / EVIDENCE_PACKAGE_INDEX_ARTIFACT).read_text(encoding="utf-8"))
    assert pkg["read_surface_refresh_complete"] is True
    assert pkg["chroma_projection_complete"] is True
    assert pkg["durable_vector_persistence_proven"] is True
    assert (ad / NO_DIRECT_CHROMA_ASSERTION_ARTIFACT).is_file()


def test_skip_chroma_env_defers_projection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_R1B_SKIP_CHROMA_PROJECTION", "1")
    repo = tmp_path
    ad = repo / "run_skip"
    _eligible_run_dir(repo, ad)
    outcome = emit_section_r1b_governed_receipt_chain(
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="run_skip",
        raw_request={
            "jd_hash": "fixture_jd_digest",
            "resume_hash": "fixture_resume_digest",
        },
        gateway=AppsRgR1BUwgGateway(),
    )
    assert outcome.uwg_commit_or_block_status == "ADMITTED"
    assert not (ad / READ_SURFACE_REFRESH_ARTIFACT).is_file()
    assert outcome.durable_vector_persistence_proven is False
    uwg = assess_uwg_durable_write_chain(repo_root=repo, artifact_dir=ad, integrated_dir=None)
    assert uwg["durable_vector_persistence_proven"] is False
