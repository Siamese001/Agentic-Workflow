"""SP-001: orchestrate_full_resume outputs are explicitly non-product."""
from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.non_product_proof_stamp import (
    ORCHESTRATOR_PROOF_CLASSIFICATION,
    orchestrator_non_product_stamp,
)


def test_orchestrator_stamp_fields() -> None:
    stamp = orchestrator_non_product_stamp()
    assert stamp["proof_classification"] == ORCHESTRATOR_PROOF_CLASSIFICATION
    assert stamp["product_certification"] == "NOT_CLAIMED"
    assert stamp["l7_certification"] == "NOT_CLAIMED"
    assert stamp["fort_knox_certification"] == "NOT_CLAIMED"
    assert stamp["integrated_r4_invoked"] is False
    claims = " ".join(stamp["explicit_non_claims"]).lower()
    assert "exit x3" in claims or "agentic_core" in claims


def test_orchestrate_module_documents_non_product() -> None:
    src = (
        Path(__file__).resolve().parents[3]
        / "tests"
        / "helpers"
        / "offline_lane_orchestration.py"
    ).read_text(encoding="utf-8")
    assert "orchestrator_non_product_stamp" in src
    assert "orchestrator_non_product_stamp" in src
    assert "product spine" in src.lower() or "non-product" in src.lower()


def test_orchestrate_module_has_no_cli_entry() -> None:
    src = (Path(__file__).resolve().parents[3] / "apps_rg" / "runtime" / "internal" / "lane_batch.py").read_text(
        encoding="utf-8"
    )
    assert "not an operator CLI entrypoint" in src
    assert "def main(" not in src
    assert "python -m apps_rg" in src
    assert "run_canonical_apps_rg_from_cli_primitives" not in src
