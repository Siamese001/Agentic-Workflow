"""Unit tests for section_l7_binding_manifest classification and L7 trust checks."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.section_l7_binding_manifest import (
    BINDING_MANIFEST_ARTIFACT,
    CLASS_APPS_RG_DOMAIN,
    CLASS_APPS_RG_SHIM,
    CLASS_CORE_99_DESIGN_ONLY,
    CLASS_CORE_L7_MISSING,
    CLASS_CORE_L7_REF,
    CLASS_CORE_L7_UNTRUSTED,
    CLASS_NOT_APPLICABLE,
    assess_l7_how_trace_trust,
    assess_l7_spine_proof_trust,
    build_section_l7_binding_manifest,
    emit_section_l7_binding_manifest,
)


def _touch(ad: Path, name: str, doc: dict) -> None:
    (ad / name).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def test_manifest_modular_lane_missing_l7(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    _touch(ad, "x2_gate_outputs.json", {"gates": []})
    _touch(ad, "validated_request.json", {"contract_version": "apps_rg_section_front_bridge_v1"})
    _touch(
        ad,
        "product_certification_receipt.json",
        {"product_certification": "NOT_CLAIMED"},
    )
    _touch(ad, "proof_eligibility_receipt.json", {"proof_eligible": False})

    doc = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="run_test",
        command_surface="python -m apps_rg --section executive_summary",
    )
    assert doc["integrated_l7_invoked"] is False
    assert doc["l7_how_trace_emitted"] is False
    assert doc["runtime_proof_bundle_99_emitted"] is False
    assert doc["artifact_classifications"]["agentic_core_how_trace.json"] == CLASS_CORE_L7_MISSING
    assert doc["artifact_classifications"]["x2_gate_outputs.json"] == CLASS_APPS_RG_DOMAIN
    assert doc["artifact_classifications"]["validated_request.json"] == CLASS_APPS_RG_SHIM
    assert doc["artifact_classifications"]["section_runtime_proof_bundle.json"] == CLASS_APPS_RG_SHIM
    assert doc["artifact_classifications"]["runtime_gate_verdict_bundle.json"] == CLASS_NOT_APPLICABLE
    assert doc["design_law_owner_classifications"]["x2_gate_outputs.json"] == "APP_DOMAIN_EVIDENCE"
    assert "section_l7_binding_manifest is not agentic_core_how_trace" in doc["explicit_non_claims"]


def test_x2_not_classified_as_gate_verdict(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    _touch(ad, "x2_gate_outputs.json", {"gate_id": "apps_rg_lane_gate"})
    doc = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="r1",
    )
    assert doc["artifact_classifications"]["x2_gate_outputs.json"] == CLASS_APPS_RG_DOMAIN
    assert doc["artifact_classifications"]["x2_gate_outputs.json"] != "GateVerdict"


def test_section_runtime_proof_bundle_not_99(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    _touch(
        ad,
        "section_runtime_proof_bundle.json",
        {"schema_version": "section_runtime_proof_bundle_v1", "proof_status": "INCOMPLETE"},
    )
    doc = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="r1",
    )
    assert doc["artifact_classifications"]["section_runtime_proof_bundle.json"] == CLASS_APPS_RG_SHIM
    assert doc["artifact_classifications"]["runtime_proof_bundle.json"] == CLASS_CORE_99_DESIGN_ONLY


def test_fake_spine_proof_marked_untrusted(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    _touch(ad, "agentic_core_spine_proof.json", {"success": True, "certified": True})
    doc = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="r1",
    )
    assert doc["artifact_classifications"]["agentic_core_spine_proof.json"] == CLASS_CORE_L7_UNTRUSTED
    assert doc["l7_spine_proof_emitted"] is False
    assert doc["l7_untrusted_artifacts"]
    assert doc["proof_classification"] == "SECTION_MODULAR_L7_UNTRUSTED_ARTIFACTS_PRESENT"
    assert doc.get("lane_proof_eligible") is None or doc.get("lane_proof_eligible") is False


def test_trusted_spine_proof_from_certification_fixture(tmp_path: Path) -> None:
    fixture = (
        Path(__file__).resolve().parents[3]
        / "certification"
        / "agentic_core"
        / "integrated_runtime"
        / "r4_latest"
        / "agentic_core_spine_proof.json"
    )
    if not fixture.is_file():
        pytest.skip("certification spine proof fixture missing")
    ad = tmp_path / "run"
    ad.mkdir()
    (ad / "agentic_core_spine_proof.json").write_text(
        fixture.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    doc = json.loads((ad / "agentic_core_spine_proof.json").read_text(encoding="utf-8"))
    trusted, _ = assess_l7_spine_proof_trust(doc)
    assert trusted is True
    manifest = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="r1",
    )
    assert manifest["artifact_classifications"]["agentic_core_spine_proof.json"] == CLASS_CORE_L7_REF
    assert manifest["l7_spine_proof_emitted"] is True


def test_trusted_how_trace_shape() -> None:
    doc = {
        "schema_version": "1.0",
        "runtime_subject": "agentic_core",
        "evidence_plane": "L7_AUDITABILITY",
        "stages": [],
    }
    ok, reason = assess_l7_how_trace_trust(doc)
    assert ok is True
    assert reason == "l7_how_trace_shape"


def test_emit_writes_manifest_file(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    out = emit_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="emit_test",
    )
    assert out.name == BINDING_MANIFEST_ARTIFACT
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "section_l7_binding_manifest_v2"
    assert "design_law_owner_classifications" in loaded
    assert "verified_external_refs" in loaded
