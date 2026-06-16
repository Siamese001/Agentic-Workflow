from __future__ import annotations

from pathlib import Path

from apps_eval.matrix import run_matrix


def test_run_matrix_filters_apps_rg_dev_suites(tmp_path: Path) -> None:
    summary = run_matrix(app_id="apps_rg", split="dev", out_dir=str(tmp_path))

    assert summary["verdict"] == "pass"
    assert summary["suite_count"] == 1
    assert summary["suites"][0]["suite_id"] == "apps_rg.dev.resume_generation"
    assert Path(summary["artifact_paths"]["matrix_summary"]).is_file()
    assert Path(summary["artifact_paths"]["matrix_report"]).is_file()
