"""Contract: modular section lanes bind to L7 via manifest only — no duplicate L7 emit."""
from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.section_l7_binding_manifest import (
    BINDING_MANIFEST_ARTIFACT,
    CLASS_APPS_RG_DOMAIN,
    CLASS_CORE_L7_MISSING,
    CLASS_CORE_L7_UNTRUSTED,
    build_section_l7_binding_manifest,
    emit_section_l7_binding_manifest,
)


def test_contract_lane_without_l7_files_core_l7_missing(tmp_path: Path) -> None:
    ad = tmp_path / "exec_summary_contract"
    ad.mkdir()
    for name in (
        "validated_request.json",
        "l1_plan_contract.json",
        "route_contract.json",
        "x2_gate_outputs.json",
        "section_runtime_proof_bundle.json",
    ):
        (ad / name).write_text("{}\n", encoding="utf-8")

    doc = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="exec_summary_contract",
        command_surface="python -m apps_rg --section executive_summary",
    )
    assert doc["integrated_l7_invoked"] is False
    assert doc["l7_how_trace_emitted"] is False
    assert doc["l7_route_family_coverage_emitted"] is False
    assert doc["l7_spine_proof_emitted"] is False
    assert doc["runtime_proof_bundle_99_emitted"] is False
    for l7_name in (
        "agentic_core_how_trace.json",
        "agentic_core_l7_route_family_coverage.json",
        "agentic_core_spine_proof.json",
    ):
        assert doc["artifact_classifications"][l7_name] == CLASS_CORE_L7_MISSING
    assert not (ad / "agentic_core_how_trace.json").exists()
    assert not (ad / "agentic_core_spine_proof.json").exists()


def test_contract_x2_is_apps_rg_domain_not_gate_verdict(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    (ad / "x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "exec_summary_claim_coverage", "pass": True}]}),
        encoding="utf-8",
    )
    doc = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="r1",
    )
    assert doc["artifact_classifications"]["x2_gate_outputs.json"] == CLASS_APPS_RG_DOMAIN


def test_contract_section_proof_bundle_not_runtime_proof_bundle_99(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    (ad / "section_runtime_proof_bundle.json").write_text(
        json.dumps(
            {
                "schema_version": "section_runtime_proof_bundle_v1",
                "proof_status": "INCOMPLETE",
                "notes": "not 99",
            }
        ),
        encoding="utf-8",
    )
    doc = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="r1",
    )
    assert doc["artifact_classifications"]["section_runtime_proof_bundle.json"] != "CORE_99_DESIGN_ONLY"
    assert doc["runtime_proof_bundle_99_emitted"] is False
    assert "section_runtime_proof_bundle is not core 99 RuntimeProofBundle" in " ".join(
        doc["explicit_non_claims"]
    )


def test_contract_fake_spine_proof_untrusted_not_emitted(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    (ad / "agentic_core_spine_proof.json").write_text(
        json.dumps({"producer": "apps_rg", "certified": True}),
        encoding="utf-8",
    )
    emit_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="r1",
    )
    doc = json.loads((ad / BINDING_MANIFEST_ARTIFACT).read_text(encoding="utf-8"))
    assert doc["l7_spine_proof_emitted"] is False
    assert doc["artifact_classifications"]["agentic_core_spine_proof.json"] == CLASS_CORE_L7_UNTRUSTED
    assert doc["integrated_l7_invoked"] is False
