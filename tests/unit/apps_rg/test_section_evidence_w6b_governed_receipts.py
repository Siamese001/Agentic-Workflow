"""W6B — governed R1B UWG receipt chain in section run folders (no Chroma)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.cache.r1b_governed_receipt_emission import (
    COMMIT_REQUEST_ARTIFACT,
    GOVERNED_CHAIN_MANIFEST,
    REASON_X3_NOT_X3C,
    emit_section_r1b_governed_receipt_chain,
)
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
from apps_rg.cache.r1b_uwg_gateway_shim import AppsRgR1BUwgGateway
from apps_rg.cache.r1b_uwg_promotion import build_r1b_promotion_candidate
from apps_rg.runtime.semantic_cache_persistence_quarantine import (
    NO_DIRECT_CHROMA_ASSERTION_ARTIFACT,
    assess_uwg_durable_write_chain,
    finalize_semantic_cache_quarantine,
)
from apps_rg.runtime.section_evidence_package import (
    EVIDENCE_PACKAGE_INDEX_ARTIFACT,
    finalize_section_evidence_package,
)
from apps_rg.runtime.section_l7_binding_manifest import build_section_l7_binding_manifest


def _write_x3_block_run(ad: Path) -> None:
    ad.mkdir(parents=True, exist_ok=True)
    (ad / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_BLOCK", "proof_eligible": False}),
        encoding="utf-8",
    )
    (ad / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": "exec_block_w6b",
                "section_id": "executive_summary",
                "proof_eligible": False,
            }
        ),
        encoding="utf-8",
    )


def _eligible_candidate(repo_root: Path, run_dir: Path) -> object:
    w7 = repo_root / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w7_fixtures"
    base = json.loads((w7 / "historical_intent_record_admissible.json").read_text(encoding="utf-8"))
    base["record_id"] = "hir_w6b_eligible"
    base["source_run_id"] = run_dir.name
    rec = HistoricalIntentRecord.from_dict(base)
    chunks = [
        HistoricalOutputChunk.from_dict(
            {
                "chunk_id": "hoc_w6b_a",
                "parent_intent_record_id": rec.record_id,
                "chunk_type": "final_resume",
                "section_id": "",
                "chunk_text": "{}",
                "chunk_digest": "",
                "chunk_vector_ref": "",
                "artifact_ref": "generated_resume.json",
                "artifact_digest": "",
                "source_fact_ids": [],
                "proof_pool_refs": [],
                "support_status": "",
                "x2_status": "PASS",
                "x1d_status": "",
                "section_prompt_hash": "",
                "section_model_profile_hash": "",
                "generated_at_utc": "2026-05-20T00:00:00+00:00",
            }
        )
    ]
    (run_dir / "generated_resume.json").write_text("{}\n", encoding="utf-8")
    assessment = {
        "admissible": True,
        "cache_admissible": True,
        "record": rec.to_dict(),
        "chunks": [c.to_dict() for c in chunks],
        "exit_metadata": {"source_run_id": run_dir.name, "x3_disposition": "X3_ALLOW"},
    }
    return build_r1b_promotion_candidate(
        record=rec,
        chunks=chunks,
        post_exit_eligibility=assessment,
        run_dir=run_dir,
    )


def test_x3_block_does_not_emit_commit_request(tmp_path: Path) -> None:
    ad = tmp_path / "run_block"
    _write_x3_block_run(ad)
    outcome = emit_section_r1b_governed_receipt_chain(
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="exec_block_w6b",
    )
    assert outcome.commit_request_status == "NOT_EMITTED"
    assert outcome.reason == REASON_X3_NOT_X3C
    assert not (ad / COMMIT_REQUEST_ARTIFACT).is_file()
    assert (ad / GOVERNED_CHAIN_MANIFEST).is_file()
    chain = json.loads((ad / GOVERNED_CHAIN_MANIFEST).read_text(encoding="utf-8"))
    assert chain["semantic_cache_persistence_status"] == "NOT_APPLICABLE"


def test_eligible_r1b_emits_commit_request_through_uwg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path
    ad = repo / "run_allow"
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
                "run_id": "run_allow",
                "section_id": "executive_summary",
                "proof_eligible": True,
                "runtime_generation_status": "REAL",
                "prompt_profile_hash": "prompt_profile_w7_v1",
                "gate_profile_hash": "gate_profile_w7_v1",
            }
        ),
        encoding="utf-8",
    )
    (ad / "generated_resume.json").write_text("{}\n", encoding="utf-8")
    (ad / "l2_output.json").write_text('{"section":"executive_summary"}\n', encoding="utf-8")
    w7 = repo / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w7_fixtures"
    w7.mkdir(parents=True)
    src_w7 = Path(__file__).resolve().parents[3] / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w7_fixtures"
    if src_w7.is_dir():
        for f in src_w7.glob("*.json"):
            (w7 / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        pytest.skip("w7 fixtures not present in repo")

    gw = AppsRgR1BUwgGateway()
    outcome = emit_section_r1b_governed_receipt_chain(
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="run_allow",
        raw_request={
            "jd_hash": "fixture_jd_digest",
            "resume_hash": "fixture_resume_digest",
        },
        gateway=gw,
    )
    assert outcome.commit_request_status == "EMITTED"
    assert (ad / COMMIT_REQUEST_ARTIFACT).is_file()
    assert (ad / "state_diff_validation_result.json").is_file()
    assert (ad / "l4_namespace_object_ref.json").is_file()
    assert outcome.read_surface_refresh_status == "NOT_APPLICABLE"
    assert outcome.chroma_projection_status == "MISSING"
    assert not (ad / "read_surface_refresh_receipt.json").is_file()
    uwg = assess_uwg_durable_write_chain(repo_root=repo, artifact_dir=ad, integrated_dir=None)
    assert uwg["r1b_uwg_chain_core_complete"] is True
    assert uwg["durable_proof_chain_complete"] is False
    assert uwg["governed_chroma_refresh_proven"] is False


def test_evidence_package_reflects_w6b_chain(tmp_path: Path) -> None:
    ad = tmp_path / "run_block"
    _write_x3_block_run(ad)
    binding = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="exec_block_w6b",
        command_surface="test",
        correlation=None,
    )
    summary = finalize_section_evidence_package(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="exec_block_w6b",
        binding_manifest=binding,
    )
    pkg = json.loads((ad / EVIDENCE_PACKAGE_INDEX_ARTIFACT).read_text(encoding="utf-8"))
    assert pkg["commit_request_status"] == "NOT_EMITTED"
    assert pkg["semantic_cache_persistence_status"] in ("NOT_APPLICABLE", "NOT_PROVEN")
    assert (ad / NO_DIRECT_CHROMA_ASSERTION_ARTIFACT).is_file()
    assert pkg["no_direct_chroma_write_bypass_assertion_ref"]
    assert pkg["read_surface_refresh_status"] == "NOT_APPLICABLE"
    assert summary["chroma_projection_status"] == "MISSING"
