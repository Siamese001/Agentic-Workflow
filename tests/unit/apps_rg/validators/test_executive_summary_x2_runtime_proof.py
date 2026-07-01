"""Executive summary X2 proof gates for section-pinned primary model."""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.validators.executive_summary_x2 import (
    ALLOWED_MODELS,
    PRE_X2_REQUIRED_ARTIFACTS,
    check_required_artifacts,
    model_name_matches_allowed,
)


def test_pre_x2_artifact_gate_does_not_require_final_receipts(tmp_path) -> None:
    for artifact in PRE_X2_REQUIRED_ARTIFACTS:
        path = tmp_path / artifact
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")

    ok, reason = check_required_artifacts(tmp_path, include_post_x2_receipts=False)

    assert ok is True
    assert reason is None

    full_ok, full_reason = check_required_artifacts(tmp_path)
    assert full_ok is False
    assert "fact_check_result.json" in str(full_reason)
    assert "real_l2_generation_result.json" in str(full_reason)
    assert "section_metric_receipt.json" in str(full_reason)
    assert "x3_disposition.json" in str(full_reason)


def test_executive_summary_model_allowlist_accepts_only_pinned_claude_primary() -> None:
    assert "claude-sonnet-5" in ALLOWED_MODELS
    assert "gpt-5.4-mini-2026-03-17" not in ALLOWED_MODELS
    assert "gpt-5.4-mini" not in ALLOWED_MODELS

    assert model_name_matches_allowed("claude-sonnet-5", ALLOWED_MODELS) is True
    assert model_name_matches_allowed("claude-haiku-3-5", ALLOWED_MODELS) is False
    assert model_name_matches_allowed("gpt-5.4-mini-2026-03-17", ALLOWED_MODELS) is False
    assert model_name_matches_allowed("gpt-5.4-mini", ALLOWED_MODELS) is False
    assert model_name_matches_allowed("gpt-5.5", ALLOWED_MODELS) is False


def test_executive_summary_defers_empty_x1d_artifact_until_x2_failure() -> None:
    source = (
        Path(__file__).resolve().parents[4]
        / "apps_rg"
        / "runtime"
        / "sections"
        / "executive_summary_lane.py"
    ).read_text(encoding="utf-8")

    assert 'if x2_failed_initial and not (artifact_dir / "x1d_llm_judge_outputs.json").is_file()' in source


def test_executive_summary_defers_x2_only_fact_check_on_real_llm_success() -> None:
    source = (
        Path(__file__).resolve().parents[4]
        / "apps_rg"
        / "runtime"
        / "sections"
        / "executive_summary_lane.py"
    ).read_text(encoding="utf-8")

    assert 'if x2_failed_initial or runtime_generation_status != "REAL_LLM":' in source
    assert '"status": "pending"' not in source
    assert source.count('artifact_dir / "fact_check_result.json"') == 2
