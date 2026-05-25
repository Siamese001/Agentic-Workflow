"""Phase-2 runtime matrix: parity from artifacts only, not grep."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.targeting_context_authority import material_targeting_digest
from apps_rg.runtime.targeting_context_lane_runtime_audit import (
    TARGETING_NOT_APPLICABLE,
    audit_lane_artifact_dir,
    build_lane_runtime_matrix,
)

REPO = Path(__file__).resolve().parents[2]
PROVEN_FAIL_RUN = (
    REPO
    / "artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149"
)


@pytest.mark.skipif(not PROVEN_FAIL_RUN.is_dir(), reason="proven-fail runtime proof dir not present")
def test_proven_fail_run_derived_parity_is_false() -> None:
    row = audit_lane_artifact_dir(PROVEN_FAIL_RUN, lane_id="executive_summary")
    assert row.get("classification") in ("RUNTIME_DERIVED_PARITY", "RUNTIME_PARITY_RECEIPT")
    assert row.get("parity_match") is False


def test_headline_classified_targeting_not_applicable_without_judge_targeting() -> None:
    row = audit_lane_artifact_dir(Path("/nonexistent"), lane_id="headline")
    assert row["classification"] == TARGETING_NOT_APPLICABLE
    assert row["parity_match"] is None


def test_matrix_merges_lane_rows() -> None:
    matrix = build_lane_runtime_matrix(
        {
            "headline": Path("/nonexistent"),
            "competencies": Path("/nonexistent"),
        }
    )
    assert matrix["schema"] == "targeting_lane_runtime_matrix_v1"
    assert matrix["lanes"]["headline"]["classification"] == TARGETING_NOT_APPLICABLE


def test_synthetic_exec_summary_parity_pass_fixture(tmp_path: Path) -> None:
    from tests._apps_contract.test_targeting_context_authority_contract import _sample_compiled

    jd, br = "jd-mat", "brief-mat"
    (tmp_path / "compiled_prompt.txt").write_text(_sample_compiled(jd, br), encoding="utf-8")
    packet = {
        "targeting_context": {"jd_text": jd, "briefing": br},
    }
    import json

    (tmp_path / "executive_summary_judge_packet.json").write_text(
        json.dumps(packet), encoding="utf-8"
    )
    row = audit_lane_artifact_dir(tmp_path, lane_id="executive_summary")
    assert row["parity_match"] is True
    assert row["generation_material_digest"] == row["judge_material_digest"]
    assert row["generation_material_digest"] == material_targeting_digest(jd, br)
