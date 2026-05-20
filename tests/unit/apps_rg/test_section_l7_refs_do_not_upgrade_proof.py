"""SP-004: L7 correlation refs do not upgrade lane to product proof."""
from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.section_l7_binding_manifest import build_section_l7_binding_manifest


def test_lane_proof_eligible_mirrored_from_run_manifest(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    (ad / "run_manifest.json").write_text(
        json.dumps({"proof_eligible": False, "proof_scope": "plumbing_only"}),
        encoding="utf-8",
    )
    (ad / "x2_gate_outputs.json").write_text(json.dumps({"gates": []}), encoding="utf-8")

    doc = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="r1",
    )
    assert doc["lane_proof_eligible"] is False


def test_l7_correlation_classification_includes_non_product_flags(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "apps_rg.runtime.section_l7_binding_manifest._proof_classification",
        lambda **kwargs: "SECTION_RUN_WITH_L7_CORRELATION_REFS_NOT_PRODUCT_PROOF",
    )
    ad = tmp_path / "run"
    ad.mkdir()
    (ad / "run_manifest.json").write_text(json.dumps({"proof_eligible": False}), encoding="utf-8")

    doc = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="r2",
    )
    assert doc["proof_classification"] == "SECTION_RUN_WITH_L7_CORRELATION_REFS_NOT_PRODUCT_PROOF"
    assert doc["proof_classification_legacy"] == "SECTION_RUN_WITH_INTEGRATED_L7_REFS"
    assert doc["section_l7_refs_are_correlation_only"] is True
    assert doc["section_l7_refs_do_not_prove_spine_runtime"] is True
