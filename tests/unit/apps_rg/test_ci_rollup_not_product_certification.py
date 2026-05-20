"""SP-005: CI e2e prove script stamps LANE_DEV_HARNESS, not product cert."""
from __future__ import annotations

from pathlib import Path


def test_prove_e2e_source_stamps_lane_dev_harness() -> None:
    src = (Path(__file__).resolve().parents[3] / "ops_scripts" / "ci" / "prove_apps_rg_e2e_runtime.py").read_text(
        encoding="utf-8"
    )
    assert "LANE_DEV_HARNESS" in src
    assert "proof_classification" in src
    assert "integrated_r4_invoked" in src
    assert "not L7 or Fort Knox proof" in src


def test_persist_adds_non_product_fields(monkeypatch, tmp_path: Path) -> None:
    import ops_scripts.ci.prove_apps_rg_e2e_runtime as mod

    monkeypatch.setattr(mod, "ARTIFACT_PATH", tmp_path / "proof.json")
    monkeypatch.setattr(mod, "finalize_boundary_no_bypass", lambda a, r: None)
    monkeypatch.setattr(
        mod,
        "_run_cmd",
        lambda *a, **k: type("R", (), {"stdout": "", "stderr": ""})(),
    )
    art = {"status": "PASS"}
    mod._persist_e2e_proof_artifact(art, tmp_path)
    loaded = __import__("json").loads((tmp_path / "proof.json").read_text(encoding="utf-8"))
    assert loaded["proof_classification"] == "LANE_DEV_HARNESS"
    assert loaded["product_certification"] == "NOT_CLAIMED"
    assert loaded["integrated_r4_invoked"] is False
