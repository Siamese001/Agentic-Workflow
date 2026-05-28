"""L6 shadow learning recommendations for executive_summary judge gaps."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.shadow.l6_shadow_learning import build_l6_shadow_learning_record


def _write_minimal_run_artifacts(ad: Path, *, x1d: dict) -> None:
    ad.mkdir(parents=True, exist_ok=True)
    (ad / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_REVIEW", "proof_eligible": False}),
        encoding="utf-8",
    )
    (ad / "x2_gate_outputs.json").write_text(json.dumps({"gates": []}), encoding="utf-8")
    (ad / "x1d_llm_judge_outputs.json").write_text(json.dumps(x1d), encoding="utf-8")


def test_executive_summary_judge_gap_emits_x1d_refresh_recommendation(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    _write_minimal_run_artifacts(
        ad,
        x1d={
            "judges": [
                {
                    "judge_id": "exec_narrative",
                    "provider_status": "MODEL_BACKED_FAIL_SOFT",
                    "pass": False,
                },
            ]
        },
    )
    rec = build_l6_shadow_learning_record(
        artifact_dir=ad,
        repo_root=tmp_path,
        section_id="executive_summary",
        lane_key="executive_summary",
    )
    texts = [r["recommendation"] for r in rec.get("recommendation_records") or []]
    assert any("APPS_RG_EXEC_SUMMARY_X1D_POST_X2_REFRESH=1" in t for t in texts)
    assert any("judge soft-fail" in t.lower() for t in texts)
    assert rec.get("judge_gap_observed") is True
    assert rec.get("current_run_mutation_assertion") is False


def test_non_executive_summary_section_omits_exec_summary_refresh_hint(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    _write_minimal_run_artifacts(
        ad,
        x1d={
            "judges": [
                {
                    "judge_id": "headline_fit",
                    "provider_status": "MODEL_BACKED_FAIL_SOFT",
                    "pass": False,
                },
            ]
        },
    )
    rec = build_l6_shadow_learning_record(
        artifact_dir=ad,
        repo_root=tmp_path,
        section_id="headline",
        lane_key="headline",
    )
    texts = [r["recommendation"] for r in rec.get("recommendation_records") or []]
    assert not any("APPS_RG_EXEC_SUMMARY_X1D_POST_X2_REFRESH" in t for t in texts)
