from __future__ import annotations

from pathlib import Path

from apps_eval.matrix import run_matrix


def test_run_matrix_filters_apps_rg_dev_suites(tmp_path: Path) -> None:
    summary = run_matrix(app_id="apps_rg", split="dev", out_dir=str(tmp_path))

    assert summary["verdict"] == "fail"
    assert summary["suite_count"] == 1
    assert summary["schema_version"] == "apps_eval.matrix_summary.v2"
    assert summary["suites"][0]["suite_id"] == "apps_rg.dev.resume_generation"
    assert summary["suites"][0]["record_schema_version"] == "apps_eval.completed_eval.v3"
    assert summary["suites"][0]["record_seed_digest"]
    assert "top_failure_modes" in summary["suites"][0]
    assert "coverage.missing_required_artifact" in summary["suites"][0]["top_failure_modes"]
    assert summary["failure_mode_counts"]["dependency.not_run"] > 0
    assert Path(summary["artifact_paths"]["matrix_summary"]).is_file()
    assert Path(summary["artifact_paths"]["matrix_report"]).is_file()
