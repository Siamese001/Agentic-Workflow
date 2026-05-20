"""W1–W3 section evidence package: refs, owner taxonomy, subphase coverage."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.section_evidence_package import (
    EVIDENCE_PACKAGE_INDEX_ARTIFACT,
    REF_KIND_VERIFIED_EXTERNAL,
    SCHEMA_SUBPHASE_COVERAGE_V1,
    SUBPHASE_COVERAGE_INDEX_ARTIFACT,
    assert_evidence_ref_shape,
    build_evidence_ref_record,
    build_spine_subphase_coverage_index,
    build_verified_external_refs_for_integrated,
    design_law_owner_for_artifact,
    finalize_section_evidence_package,
)
from apps_rg.runtime.section_l7_binding_manifest import (
    CLASS_APPS_RG_DOMAIN,
    CLASS_CORE_99_DESIGN_ONLY,
    SCHEMA_VERSION,
    build_section_l7_binding_manifest,
)


def test_evidence_ref_schema_verified_external() -> None:
    ref = build_evidence_ref_record(
        ref_kind=REF_KIND_VERIFIED_EXTERNAL,
        artifact_name="agentic_core_how_trace.json",
        source_path="artifacts/apps_rg/runs/cli_x/agentic_core_how_trace.json",
        local_path=None,
        source_owner_layer="agentic_core",
        owner_class="VERIFIED_EXTERNAL_REF",
        producer_module="agentic_core.L7_auditability.how_trace.how_trace_builder",
        sha256="abc",
        trust_status="trusted",
        trust_reason="l7_how_trace_shape",
        runtime_authority_claimed=False,
        explicit_non_claims=["no relocation"],
    )
    assert_evidence_ref_shape(ref)
    assert ref["runtime_authority_claimed"] is False


def test_design_law_owner_x2_not_gate_verdict() -> None:
    oc = design_law_owner_for_artifact(
        "x2_gate_outputs.json",
        legacy_class=CLASS_APPS_RG_DOMAIN,
        trusted=False,
        present=True,
    )
    assert oc == "APP_DOMAIN_EVIDENCE"
    assert oc != "CORE_GATE_VERDICT"


def test_section_proof_bundle_not_runtime_proof_bundle_99() -> None:
    oc = design_law_owner_for_artifact(
        "section_runtime_proof_bundle.json",
        legacy_class="APP_SHIM",
        trusted=False,
        present=True,
    )
    assert oc == "APP_SHIM"
    oc99 = design_law_owner_for_artifact(
        "runtime_proof_bundle.json",
        legacy_class=CLASS_CORE_99_DESIGN_ONLY,
        trusted=False,
        present=False,
    )
    assert oc99 == "DESIGN_ONLY"


def test_subphase_coverage_includes_all_v40_groups(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    for name in (
        "validated_request.json",
        "l1_plan_contract.json",
        "route_contract.json",
        "compiled_prompt_artifact.json",
        "l2_execution_packet.json",
        "x2_gate_outputs.json",
        "x3_disposition.json",
        "section_runtime_proof_bundle.json",
    ):
        (ad / name).write_text("{}\n", encoding="utf-8")

    doc = build_spine_subphase_coverage_index(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="run_cov",
        verified_external_refs=[],
        integrated_dir=None,
    )
    assert doc["schema_version"] == SCHEMA_SUBPHASE_COVERAGE_V1
    ids = {r["subphase_id"] for r in doc["subphases"]}
    assert "U0.1" in ids and "L7" in ids and "99" in ids
    assert "00C.G01" in ids and "00C.G29" in ids
    assert "C0.7" in ids
    c07 = next(r for r in doc["subphases"] if r["subphase_id"] == "C0.7")
    assert c07.get("c07_classification") == "real"
    x2 = next(r for r in doc["subphases"] if r["subphase_id"] == "X2")
    assert x2["owner_class"] == "APP_DOMAIN_EVIDENCE"
    g99 = next(r for r in doc["subphases"] if r["subphase_id"] == "99")
    assert g99["coverage_status"] in ("DESIGN_ONLY", "DRIFT")


def test_binding_manifest_v2_has_design_law_and_refs(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    (ad / "x2_gate_outputs.json").write_text("{}\n", encoding="utf-8")
    doc = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="r_v2",
    )
    assert doc["schema_version"] == SCHEMA_VERSION
    assert "design_law_owner_classifications" in doc
    assert doc["design_law_owner_classifications"]["x2_gate_outputs.json"] == "APP_DOMAIN_EVIDENCE"
    assert "verified_external_refs" in doc
    assert doc["imported_core_evidence_snapshots"] == []


def test_finalize_writes_evidence_package_and_patches_index(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    (ad / "RUN_BUNDLE_INDEX.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "run_id": "run_pkg",
                "correlation_id": None,
                "created_at": "t",
                "bundle_kind": "lane_runtime_proof",
                "lane": "executive_summary",
                "root_path": "artifacts/apps_rg/runtime_proofs/executive_summary/real/run",
                "artifact_namespace": "artifacts/apps_rg/runs",
                "log_namespace": "apps_rg/pipeline_logs",
                "entries": [],
            }
        ),
        encoding="utf-8",
    )
    binding = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="run_pkg",
    )
    summary = finalize_section_evidence_package(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="run_pkg",
        binding_manifest=binding,
    )
    assert (ad / EVIDENCE_PACKAGE_INDEX_ARTIFACT).is_file()
    assert (ad / SUBPHASE_COVERAGE_INDEX_ARTIFACT).is_file()
    assert (ad / "RUN_LINKS.json").is_file()
    idx = json.loads((ad / "RUN_BUNDLE_INDEX.json").read_text(encoding="utf-8"))
    assert idx.get("evidence_package_index_ref") == EVIDENCE_PACKAGE_INDEX_ARTIFACT


def test_verified_external_refs_from_integrated_fixture(tmp_path: Path) -> None:
    fixture_dir = (
        Path(__file__).resolve().parents[3]
        / "certification"
        / "agentic_core"
        / "integrated_runtime"
        / "r4_latest"
    )
    if not fixture_dir.is_dir():
        pytest.skip("certification integrated fixture missing")
    section_ad = tmp_path / "section_run"
    section_ad.mkdir()
    refs = build_verified_external_refs_for_integrated(
        tmp_path, fixture_dir, section_artifact_dir=section_ad
    )
    names = {r["artifact_name"] for r in refs}
    assert "agentic_core_spine_proof.json" in names or "agentic_core_how_trace.json" in names
    for ref in refs:
        assert ref["ref_kind"] == REF_KIND_VERIFIED_EXTERNAL
        assert ref["local_path"] is None
