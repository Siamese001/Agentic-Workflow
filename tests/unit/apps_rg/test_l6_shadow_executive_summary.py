"""L6 shadow learning: executive_summary post-X2 judge refresh recommendations."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.shadow.l6_shadow_learning import build_l6_shadow_learning_record


def _write_minimal_run_artifacts(ad: Path, *, x1_judges: list[dict]) -> None:
    (ad / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_REVIEW", "pass": False}),
        encoding="utf-8",
    )
    (ad / "x2_gate_outputs.json").write_text(
        json.dumps({"gates": [{"gate_id": "x2_json_parse_valid", "pass": True}], "failed_gates": []}),
        encoding="utf-8",
    )
    (ad / "x1d_llm_judge_outputs.json").write_text(
        json.dumps({"judges": x1_judges}),
        encoding="utf-8",
    )
    (ad / "parsed_output.json").write_text(json.dumps({"parse_status": "OK"}), encoding="utf-8")
    (ad / "text_claim_coverage.json").write_text(json.dumps({"overall_pass": True}), encoding="utf-8")
    (ad / "canonical_claim_ledger_v2.json").write_text(json.dumps({"parse_status": "OK"}), encoding="utf-8")


def test_executive_summary_judge_gap_emits_post_x2_refresh_recommendation(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    _write_minimal_run_artifacts(
        ad,
        x1_judges=[
            {
                "judge_id": "exec_summary_judge_a",
                "provider_key": "judge_a",
                "provider_status": "MODEL_BACKED_FAIL",
                "pass": False,
                "decisive_failure": False,
            }
        ],
    )

    rec = build_l6_shadow_learning_record(
        artifact_dir=ad,
        repo_root=tmp_path,
        section_id="executive_summary",
        lane_key="executive_summary",
    )

    texts = [r.get("recommendation", "") for r in rec.get("recommendation_records") or []]
    assert any("APPS_RG_EXEC_SUMMARY_X1D_POST_X2_REFRESH=1" in t for t in texts)
    assert any("soft-fail judges" in t and "judge_a" in t for t in texts)
    assert rec.get("judge_gap_observed") is True
    for row in rec.get("recommendation_records") or []:
        assert row.get("applies_to") == "future_run_only"


def test_non_executive_summary_skips_exec_summary_refresh_hint(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    _write_minimal_run_artifacts(
        ad,
        x1_judges=[
            {
                "judge_id": "j1",
                "provider_key": "j1",
                "provider_status": "MODEL_BACKED_FAIL",
                "pass": False,
                "decisive_failure": False,
            }
        ],
    )

    rec = build_l6_shadow_learning_record(
        artifact_dir=ad,
        repo_root=tmp_path,
        section_id="headline",
        lane_key="headline",
    )

    texts = " ".join(r.get("recommendation", "") for r in rec.get("recommendation_records") or [])
    assert "APPS_RG_EXEC_SUMMARY_X1D_POST_X2_REFRESH" not in texts
