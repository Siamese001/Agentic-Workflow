from __future__ import annotations

from pathlib import Path

from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import run_eval


def test_apps_rg_dev_suite_passes_from_snapshots(tmp_path: Path) -> None:
    record = run_eval(
        EvalRequest(
            suite_id="apps_rg.dev.resume_generation",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(tmp_path),
        )
    )
    assert record.app_id == "apps_rg"
    assert record.scorecard.verdict == "fail"
    assert record.scorecard.block_failures > 0
    assert record.scorecard.coverage_summary["release_blocked"] is True
    assert record.scorecard.coverage_summary["missing_required_artifacts"] > 0
    assert len(record.scorecard.scorecard_rows) == 134 * record.scorecard.scenario_count
    lane_rows = [row for row in record.scorecard.scorecard_rows if row["lane_id"] == "executive_summary"]
    assert {row["stage_id"] for row in lane_rows} == {"L2", "X2", "X1D", "X3", "L6"}
    for key in [
        "eval_record",
        "scorecard",
        "report",
        "manifest",
        "grader_findings",
        "regression",
        "regression_flywheel",
        "scorecard_rows",
        "component_scorecards",
        "apps_rg_component_scorecard",
        "coverage_matrix",
        "missing_required_components",
        "evidence_index",
        "apps_rg_l6_eval_handoff",
    ]:
        assert Path(record.artifact_paths[key]).is_file()
