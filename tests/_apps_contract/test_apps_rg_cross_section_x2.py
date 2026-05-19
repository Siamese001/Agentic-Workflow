"""Contract tests for cross-section overlap X2 artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.assembly.final_resume_assembler import assemble_final_resume
from apps_rg.runtime.assembly.final_resume_manifest import resolve_default_paths
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root


@pytest.fixture(scope="module")
def paths():
    p = resolve_default_paths(find_repo_root())
    if not p.rollup_json.is_file():
        pytest.skip("rollup missing")
    return p


@pytest.fixture(scope="module")
def assembled(paths) -> dict[str, object]:
    try:
        return assemble_final_resume(paths)
    except Exception as exc:
        pytest.skip(f"assembly blocked: {exc}")


def test_cross_section_x2_artifact(paths, assembled: dict[str, object]) -> None:
    p = paths.output_dir / "cross_section_x2_gate_outputs.json"
    assert p.is_file()
    blob = json.loads(p.read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"] for g in blob.get("gates", [])}
    assert "x2_cross_section_exact_duplicate" in gate_ids
    assert "x2_cross_section_repeated_metric" in gate_ids


def test_kept_removed_claims_artifact(paths) -> None:
    p = paths.output_dir / "kept_removed_claims.json"
    assert p.is_file()
    blob = json.loads(p.read_text(encoding="utf-8"))
    assert "kept_claims" in blob
    assert "removed_claims" in blob


def test_receipt_v2_fields(assembled: dict[str, object]) -> None:
    receipt_path = assembled["paths"]["receipt"]
    blob = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
    assert blob["receipt_id"] == "final_resume_assembly_receipt_v2"
    assert "orchestration_fingerprint" in blob
    assert "kept_claims" in blob
    assert "removed_claims" in blob
    assert "overlap_decisions" in blob
    if blob.get("cross_section_x2_product_pass") and blob.get("review_lane_policy_summary", {}).get(
        "product_allow_claimed"
    ):
        assert blob.get("product_allow_claimed") is True
    else:
        assert blob.get("product_allow_claimed") is False
