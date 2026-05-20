"""W7A — shadow product-path quarantine and proof-class relabeling."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.runtime.non_product_proof_stamp import (
    CONTRACT_TEST_PROOF_CLASSIFICATION,
    DEMO_HARNESS_ENV,
    DEMO_HARNESS_PROOF_CLASSIFICATION,
    FORBIDDEN_PRODUCT_PROOF_CLASSIFICATIONS,
    ORCHESTRATOR_PROOF_CLASSIFICATION,
    PACKAGE_DISPOSITION_CLASSIFICATION,
    orchestrator_non_product_stamp,
    package_rollup_non_product_stamp,
)
from apps_rg.runtime.shadow_product_path_quarantine import (
    assess_shadow_product_shaped_artifacts,
    reject_shadow_payload_as_integrated_proof,
)
from apps_rg.runtime.section_evidence_package import (
    EVIDENCE_PACKAGE_INDEX_ARTIFACT,
    finalize_section_evidence_package,
)
from apps_rg.runtime.section_l7_binding_manifest import build_section_l7_binding_manifest
from tests.helpers.ci_lane_dev_boundary import (
    CI_LANE_DEV_HARNESS_CLASSIFICATION,
    persist_ci_lane_dev_proof_artifact,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
EXEC_SUMMARY_REAL_ROOT = (
    REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "executive_summary" / "real"
)


def _latest_x3_block_run() -> Path | None:
    if not EXEC_SUMMARY_REAL_ROOT.is_dir():
        return None
    candidates = []
    for p in EXEC_SUMMARY_REAL_ROOT.iterdir():
        if not p.is_dir() or not p.name.startswith("exec_summary_"):
            continue
        x3 = p / "x3_disposition.json"
        if not x3.is_file():
            continue
        doc = json.loads(x3.read_text(encoding="utf-8"))
        if str(doc.get("x3_code") or "").upper() == "X3_BLOCK":
            candidates.append(p)
    if not candidates:
        return None
    return max(candidates, key=lambda x: x.stat().st_mtime)


def test_orchestrator_stamp_never_product_or_fort_knox() -> None:
    stamp = orchestrator_non_product_stamp()
    assert stamp["proof_classification"] == ORCHESTRATOR_PROOF_CLASSIFICATION
    assert stamp["proof_classification"] == "LANE_DEV_HARNESS"
    assert stamp["proof_classification"] not in FORBIDDEN_PRODUCT_PROOF_CLASSIFICATIONS
    claims = " ".join(stamp["explicit_non_claims"])
    assert "PRODUCT_RUNTIME_PROOF" in claims
    assert "FORT_KNOX_PROOF" in claims


def test_package_rollup_non_claims_w7a() -> None:
    stamp = package_rollup_non_product_stamp(package_x3_allow=True)
    claims = " ".join(stamp["explicit_non_claims"]).lower()
    assert "integrated r4" in claims
    assert "exit x3" in claims or "agentic_core" in claims
    assert "99" in claims
    assert "product certification" in claims


def test_demo_harness_fail_closed_without_env() -> None:
    env = os.environ.copy()
    env.pop(DEMO_HARNESS_ENV, None)
    proc = subprocess.run(
        [sys.executable, "-m", "apps_rg.runtime.dry_run.executive_summary_demo"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert proc.returncode == 2


def test_demo_harness_emits_non_product_when_enabled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(DEMO_HARNESS_ENV, "1")
    out = tmp_path / "demo_out"
    from apps_rg.runtime.dry_run.executive_summary_demo import run_demo_harness

    result = run_demo_harness(output_dir=out)
    assert result["proof_classification"] == DEMO_HARNESS_PROOF_CLASSIFICATION
    assert (out / "demo_harness_proof.json").is_file()
    blob = json.loads((out / "demo_harness_proof.json").read_text(encoding="utf-8"))
    assert blob["proof_classification"] == DEMO_HARNESS_PROOF_CLASSIFICATION


def test_shadow_artifacts_untrusted_in_section_binding(tmp_path: Path) -> None:
    ad = tmp_path / "lane_run"
    ad.mkdir()
    (ad / "resume_package_x3.json").write_text(
        json.dumps(package_rollup_non_product_stamp(package_x3_allow=False)),
        encoding="utf-8",
    )
    binding = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="w7a_shadow",
        command_surface="test",
    )
    assert binding["shadow_paths_present"] is True
    assert any(
        "resume_package_x3" in str(u.get("artifact") or "")
        for u in binding["l7_untrusted_artifacts"]
    )
    pkg = finalize_section_evidence_package(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="w7a_shadow",
        binding_manifest=binding,
    )
    index = json.loads((ad / EVIDENCE_PACKAGE_INDEX_ARTIFACT).read_text(encoding="utf-8"))
    assert index["shadow_paths_present"] is True
    assert index["proof_classification"] != "INTEGRATED_R4_PRODUCT_RUNTIME"
    assert index["product_certification_impact"]["runtime_proof_bundle_99_claimed"] is False


def test_ci_harness_labels_lane_dev_not_live_runtime(tmp_path: Path) -> None:
    artifact_path = tmp_path / "ci_lane_dev_proof.json"
    minimal = {
        "boundary_no_bypass": {
            "mock_pass": False,
            "direct_l2_chroma_bypass": False,
            "direct_l4_write_bypass": False,
        },
        "commands_run": [],
        "pa": {},
        "route": {},
        "c0": {},
        "exit": {},
    }
    persist_ci_lane_dev_proof_artifact(minimal, tmp_path, artifact_path=artifact_path)
    doc = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert doc["proof_classification"] == CI_LANE_DEV_HARNESS_CLASSIFICATION
    assert doc["proof_classification"] != "LIVE_RUNTIME_PROOF"
    assert doc["product_certification"] == "NOT_CLAIMED"


def test_reject_forbidden_product_classification() -> None:
    with pytest.raises(ValueError, match="forbidden product proof"):
        reject_shadow_payload_as_integrated_proof(
            {"proof_classification": "PRODUCT_RUNTIME_PROOF"},
            context="w7a",
        )


def test_latest_live_x3_block_not_vector_proof() -> None:
    run_dir = _latest_x3_block_run()
    if run_dir is None:
        pytest.skip("no X3_BLOCK executive_summary run on disk")
    pkg = json.loads((run_dir / EVIDENCE_PACKAGE_INDEX_ARTIFACT).read_text(encoding="utf-8"))
    assert pkg["commit_request_status"] == "NOT_EMITTED"
    assert pkg["durable_vector_persistence_proven"] is False
    assert pkg["proof_classification"] != "INTEGRATED_R4_PRODUCT_RUNTIME"
