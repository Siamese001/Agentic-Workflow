"""W6D — read-only semantic-cache proof boundary validation (W6A–W6C).

Ensures live X3_BLOCK product runs cannot be misread as durable vector persistence,
while controlled UWG-admitted fixtures prove the governed chain only with assertion.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.cache.r1b_governed_receipt_emission import (
    COMMIT_REQUEST_ARTIFACT,
    STATE_DIFF_VALIDATION_ARTIFACT,
    UWG_COMMIT_RECEIPT_ARTIFACT,
    emit_section_r1b_governed_receipt_chain,
)
from apps_rg.cache.r1b_chroma_read_surface_projection import (
    CHROMA_COLLECTION_INDEX_ARTIFACT,
    CHROMA_READ_AFTER_WRITE_ARTIFACT,
    READ_SURFACE_REFRESH_ARTIFACT,
)
from apps_rg.cache.r1b_uwg_promotion import AppsRgR1BUwgGateway
from apps_rg.runtime.semantic_cache_persistence_quarantine import (
    CHROMA_CLASS_NON_DURABLE,
    CHROMA_CLASS_GOVERNED_REFRESH,
    CULPRIT_CALL_CHAIN,
    NO_DIRECT_CHROMA_ASSERTION_ARTIFACT,
    PROMOTE_TO_LONG_TERM_CALLERS,
    assess_uwg_durable_write_chain,
    build_no_direct_chroma_write_bypass_assertion,
    classify_shadow_chroma_write_path,
    finalize_semantic_cache_quarantine,
)
from apps_rg.runtime.section_evidence_package import (
    EVIDENCE_PACKAGE_INDEX_ARTIFACT,
    finalize_section_evidence_package,
)
from apps_rg.runtime.section_l7_binding_manifest import build_section_l7_binding_manifest

REPO_ROOT = Path(__file__).resolve().parents[3]
EXEC_SUMMARY_REAL_ROOT = (
    REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "executive_summary" / "real"
)


def _latest_exec_summary_run_dir() -> Path | None:
    if not EXEC_SUMMARY_REAL_ROOT.is_dir():
        return None
    candidates = [
        p
        for p in EXEC_SUMMARY_REAL_ROOT.iterdir()
        if p.is_dir() and p.name.startswith("exec_summary_")
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _load_pkg(run_dir: Path) -> dict:
    path = run_dir / EVIDENCE_PACKAGE_INDEX_ARTIFACT
    assert path.is_file(), f"missing {path}"
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(doc, dict)
    return doc


def _eligible_fixture_dir(repo: Path, ad: Path) -> None:
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


def test_w6d_latest_x3_block_exec_summary_cannot_claim_vector_persistence() -> None:
    run_dir = _latest_exec_summary_run_dir()
    if run_dir is None:
        pytest.skip("no executive_summary real runtime proof dirs on disk")
    x3 = json.loads((run_dir / "x3_disposition.json").read_text(encoding="utf-8"))
    if str(x3.get("x3_code") or "").upper() != "X3_BLOCK":
        pytest.skip(f"latest run is {x3.get('x3_code')!r}, not X3_BLOCK")

    pkg = _load_pkg(run_dir)
    assert pkg["commit_request_status"] == "NOT_EMITTED"
    assert pkg["read_surface_refresh_status"] == "NOT_APPLICABLE"
    assert pkg["chroma_projection_status"] == "NOT_APPLICABLE"
    assert pkg["durable_vector_persistence_proven"] is False
    assert pkg["read_surface_refresh_complete"] is False
    assert pkg["chroma_projection_complete"] is False
    assert pkg["r1b_uwg_chain_core_complete"] is False
    assert pkg["chroma_semantic_cache_classification"] == CHROMA_CLASS_NON_DURABLE
    assert not (run_dir / COMMIT_REQUEST_ARTIFACT).is_file()
    assert not (run_dir / READ_SURFACE_REFRESH_ARTIFACT).is_file()

    chain = json.loads((run_dir / "r1b_governed_receipt_chain.json").read_text(encoding="utf-8"))
    assert chain["x3_code"] == "X3_BLOCK"
    assert chain["durable_vector_persistence_proven"] is False


def test_w6d_controlled_fixture_full_chain_and_assertion_gated_durable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APPS_RG_R1B_SKIP_CHROMA_PROJECTION", raising=False)
    repo = tmp_path
    ad = repo / "w6d_eligible"
    _eligible_fixture_dir(repo, ad)
    outcome = emit_section_r1b_governed_receipt_chain(
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="w6d_eligible",
        raw_request={"jd_hash": "fixture_jd_digest", "resume_hash": "fixture_resume_digest"},
        gateway=AppsRgR1BUwgGateway(),
    )
    assert outcome.commit_request_status == "EMITTED"
    assert outcome.uwg_commit_or_block_status == "ADMITTED"
    assert (ad / COMMIT_REQUEST_ARTIFACT).is_file()
    assert (ad / STATE_DIFF_VALIDATION_ARTIFACT).is_file()
    assert (ad / UWG_COMMIT_RECEIPT_ARTIFACT).is_file()
    assert (ad / "l4_namespace_object_ref.json").is_file()
    assert (ad / READ_SURFACE_REFRESH_ARTIFACT).is_file()
    assert (ad / CHROMA_COLLECTION_INDEX_ARTIFACT).is_file()
    assert (ad / CHROMA_READ_AFTER_WRITE_ARTIFACT).is_file()

    pre = assess_uwg_durable_write_chain(repo_root=repo, artifact_dir=ad, integrated_dir=None)
    assert pre["durable_vector_chain_artifacts_complete"] is True
    assert pre["durable_vector_persistence_proven"] is False
    assert not (ad / NO_DIRECT_CHROMA_ASSERTION_ARTIFACT).is_file()

    post = finalize_semantic_cache_quarantine(
        repo_root=repo,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="w6d_eligible",
        integrated_dir=None,
    )
    assert (ad / NO_DIRECT_CHROMA_ASSERTION_ARTIFACT).is_file()
    assertion = post["no_direct_chroma_write_bypass_assertion"]
    assert assertion["durable_persistence_claim_allowed"] is False
    assert post["uwg_assessment"]["durable_vector_persistence_proven"] is True
    assert post["chroma_classification"] == CHROMA_CLASS_GOVERNED_REFRESH


def test_w6d_core_d2_shadow_path_non_durable_cannot_prove_vectors(tmp_path: Path) -> None:
    uwg = assess_uwg_durable_write_chain(
        repo_root=tmp_path,
        artifact_dir=tmp_path / "empty",
        integrated_dir=None,
    )
    assert classify_shadow_chroma_write_path(uwg_assessment=uwg) == CHROMA_CLASS_NON_DURABLE
    assert uwg["durable_vector_persistence_proven"] is False
    assert uwg["governed_chroma_refresh_proven"] is False

    assertion = build_no_direct_chroma_write_bypass_assertion(
        repo_root=tmp_path,
        artifact_dir=tmp_path / "empty",
        section_id="executive_summary",
        run_id="w6d_empty",
        uwg_assessment=uwg,
        chroma_classification=CHROMA_CLASS_NON_DURABLE,
    )
    assert assertion["durable_persistence_claim_allowed"] is False
    assert assertion["chroma_semantic_cache_classification"] == CHROMA_CLASS_NON_DURABLE
    assert "execution_orchestrator" in assertion["primary_culprit"]
    assert any("gptcache_client" in step for step in CULPRIT_CALL_CHAIN)
    d2_callers = {c["caller"] for c in PROMOTE_TO_LONG_TERM_CALLERS}
    assert "agentic_core/L0_routing/reasoning/execution_orchestrator.py" in d2_callers
    for caller in PROMOTE_TO_LONG_TERM_CALLERS:
        if "execution_orchestrator" in caller["caller"] or "gptcache" in caller.get("symbol", ""):
            assert caller["classification"] == CHROMA_CLASS_NON_DURABLE
            assert caller["uwg_gated"] == "no"


def test_w6d_evidence_package_separates_four_completion_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APPS_RG_R1B_SKIP_CHROMA_PROJECTION", raising=False)
    repo = tmp_path
    ad = repo / "w6d_pkg"
    _eligible_fixture_dir(repo, ad)
    binding = build_section_l7_binding_manifest(
        repo_root=repo,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="w6d_pkg",
        command_surface="test",
        correlation=None,
    )
    finalize_section_evidence_package(
        repo_root=repo,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="w6d_pkg",
        binding_manifest=binding,
    )
    pkg = _load_pkg(ad)
    assert pkg["r1b_uwg_chain_core_complete"] is True
    assert pkg["read_surface_refresh_complete"] is True
    assert pkg["chroma_projection_complete"] is True
    assert pkg["durable_vector_persistence_proven"] is True
    assert pkg["durable_semantic_cache_proof_present"] is True
    assert pkg["semantic_cache_persistence_status"] == "PROVEN_GOVERNED_VECTOR_CHAIN"
    assert pkg["chroma_semantic_cache_classification"] == CHROMA_CLASS_GOVERNED_REFRESH

    cert = pkg["product_certification_impact"]
    assert cert["product_certification"] in ("NOT_CLAIMED", "UNKNOWN")
    assert cert["runtime_proof_bundle_99_claimed"] is False
    assert "no 99 RuntimeProofBundle claimed" in pkg["explicit_non_claims"]
    assert not (ad / "runtime_proof_bundle.json").is_file()


def test_w6d_x3_block_evidence_package_product_cert_unchanged(tmp_path: Path) -> None:
    ad = tmp_path / "x3_block_pkg"
    ad.mkdir()
    (ad / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_BLOCK", "proof_eligible": False}),
        encoding="utf-8",
    )
    (ad / "run_manifest.json").write_text(
        json.dumps({"run_id": "x3_block_pkg", "section_id": "executive_summary"}),
        encoding="utf-8",
    )
    binding = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="x3_block_pkg",
        command_surface="test",
        correlation=None,
    )
    finalize_section_evidence_package(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="x3_block_pkg",
        binding_manifest=binding,
    )
    pkg = _load_pkg(ad)
    assert pkg["durable_vector_persistence_proven"] is False
    cert = pkg["product_certification_impact"]
    assert cert["product_certification"] in ("NOT_CLAIMED", "UNKNOWN")
    assert cert.get("l7_certification_claimed") is False
    assert cert.get("runtime_proof_bundle_99_claimed") is False
