from __future__ import annotations

from pathlib import Path

from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import run_eval


def test_apps_lic_dev_suite_passes_from_snapshots(tmp_path: Path) -> None:
    record = run_eval(
        EvalRequest(
            suite_id="apps_lic.dev.outreach_message",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(tmp_path),
        )
    )
    assert record.app_id == "apps_lic"
    assert record.scorecard.verdict == "pass"
    assert record.scorecard.block_failures == 0
    for key in ["eval_record", "scorecard", "report", "manifest", "grader_findings", "regression", "regression_flywheel"]:
        assert Path(record.artifact_paths[key]).is_file()
