from __future__ import annotations

from pathlib import Path

from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import run_eval


def test_report_contains_review_ready_sections(tmp_path: Path) -> None:
    record = run_eval(
        EvalRequest(
            suite_id="apps_rg.dev.resume_generation",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(tmp_path),
        )
    )
    report = Path(record.artifact_paths["report"]).read_text(encoding="utf-8")

    assert "## Run Context" in report
    assert "## apps_rg Microstep Coverage" in report
    assert "## Failure Modes" in report
    assert "## Fixture Provenance" in report
    assert "## Scenario Results" in report
    assert "## Dimension Scores" in report
    assert "## Regression" in report
    assert "## Regression Flywheel" in report
    assert "## Artifact Inventory" in report
    assert "## Review Guidance" in report
    assert "Record seed digest" in report
